import os
import logging
from typing import Dict, Any, List

from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_tool_calling_agent
from langchain.agents.agent import AgentExecutor
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

from ai.tools import get_receptionist_tools

logger = logging.getLogger(__name__)

# Global generic store for in-memory chat history (for now)
# In production, use Redis or MongoDB
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

from database.mongo_config import get_database

class ReceptionistAgent:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            logger.warning("GROQ_API_KEY not found in environment variables.")
        
        # Default LLM (fallback)
        self.default_llm = ChatGroq(
            temperature=0.7,
            model_name="llama-3.3-70b-versatile",
            groq_api_key=self.api_key
        )
        self.all_tools = get_receptionist_tools()
        
    def get_agent_executor(self, tools: List[Any], system_prompt: str, llm_model: str = "llama-3.3-70b-versatile"):
        # Strip provider prefix if present (e.g. "groq/llama-3.3" -> "llama-3.3")
        model_name_clean = llm_model.split("/")[-1] if "/" in llm_model else llm_model
        
        if "openai" in llm_model.lower() or "gpt" in llm_model.lower() or model_name_clean.startswith("gpt"):
                 llm = ChatOpenAI(
                    temperature=0.7,
                    model=model_name_clean,
                    api_key=os.getenv("OPENAI_API_KEY")
                )
        else:
            llm = ChatGroq(
                temperature=0.7,
                model_name=model_name_clean,
                groq_api_key=self.api_key
            )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    system_prompt
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )
        
        agent = create_tool_calling_agent(llm, tools, prompt)
        
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        
        # Wrap with message history
        agent_with_history = RunnableWithMessageHistory(
            agent_executor,
            get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
        )
        
        return agent_with_history

    async def get_agent_config(self, tenant_id: str) -> Dict[str, Any]:
        """Fetch agent configuration from DB"""
        try:
            db = get_database()
            # Find active agent for tenant
            agent_doc = await db.agents.find_one({"tenant_id": tenant_id, "status": "active"})
            
            if not agent_doc:
                # Fallback to defaults if no specific agent config
                return {
                    "system_prompt": """You are Parker, a friendly and professional AI receptionist for businesses.
Your role is to help customers with:
- Booking appointments
- Checking appointment availability
- Canceling appointments
- Viewing their upcoming appointments
- Getting information about the business

When interacting with customers:
1. Always be polite, professional, and helpful
2. Ask for necessary information (name, email, phone, preferred date/time)
3. Confirm details before booking or canceling
4. If a time is unavailable, suggest alternatives
5. Use natural, conversational language

The current tenant_id is: {tenant_id}
Today is: {current_date}

When using tools, always include the tenant_id in your requests. THIS IS CRITICAL.""",
                    "tools_config": {
                        "check_availability": True,
                        "book_appointment": True,
                        "cancel_appointment": True,
                        "update_appointment": False,
                        "list_appointments": True
                    },
                    "llm_model": "llama-3.3-70b-versatile"
                }

            # Extract config
            tools_config = agent_doc.get("tools_config", {})
            # Ensure defaults for tools if missing
            full_tools_config = {
                "check_availability": tools_config.get("check_availability", True),
                "book_appointment": tools_config.get("book_appointment", True),
                "cancel_appointment": tools_config.get("cancel_appointment", True),
                "update_appointment": tools_config.get("update_appointment", False),
                "list_appointments": tools_config.get("get_business_info", True) # Map generic info to list for now or keep separate
            }
            
            # Construct System Prompt
            base_prompt = agent_doc.get("system_prompt", "You are a helpful AI receptionist.")
            # Append dynamic context placeholders if not present
            if "{tenant_id}" not in base_prompt:
                base_prompt += "\nThe current tenant_id is: {tenant_id}"
            if "{current_date}" not in base_prompt:
                base_prompt += "\nToday is: {current_date}"
            
            return {
                "system_prompt": base_prompt,
                "tools_config": full_tools_config,
                "llm_model": agent_doc.get("llm_model", "llama-3.3-70b-versatile")
            }
            
        except Exception as e:
            logger.error(f"Error fetching agent config: {e}")
            return {} # Should trigger fallback upstream or handle gracefully

    def filter_tools(self, config: Dict[str, bool]) -> List[Any]:
        """Filter tools based on configuration"""
        allowed_tools = []
        for tool in self.all_tools:
            tool_name = tool.name
            # Map tool names to config keys if necessary, or assume 1:1 match
            # Current tools: check_availability, book_appointment, list_appointments, cancel_appointment_by_email_and_date
            
            if tool_name == "check_availability" and config.get("check_availability"):
                allowed_tools.append(tool)
            elif tool_name == "book_appointment" and config.get("book_appointment"):
                allowed_tools.append(tool)
            elif tool_name == "list_appointments" and config.get("list_appointments"): # or get_business_info logic
                allowed_tools.append(tool)
            elif "cancel" in tool_name and config.get("cancel_appointment"):
                allowed_tools.append(tool)
                
        return allowed_tools

    async def chat(self, session_id: str, tenant_id: str, message: str) -> str:
        try:
            # 1. Fetch Config
            config = await self.get_agent_config(tenant_id)
            if not config:
                 # Fallback hardcoded if DB fails completely
                 prompt_text = "You are a helpful assistant."
                 active_tools = self.all_tools
                 model = "llama-3.3-70b-versatile"
            else:
                prompt_text = config["system_prompt"]
                active_tools = self.filter_tools(config.get("tools_config", {}))
                model = config.get("llm_model", "llama-3.3-70b-versatile")
            
            # 2. Initialize Executor with dynamic settings
            agent = self.get_agent_executor(tools=active_tools, system_prompt=prompt_text, llm_model=model)
            
            from datetime import datetime
            current_date_str = datetime.now().strftime("%Y-%m-%d")
            
            # 3. Invoke
            result = await agent.ainvoke(
                {
                    "input": message,
                    "tenant_id": tenant_id,
                    "current_date": current_date_str
                },
                config={"configurable": {"session_id": session_id}}
            )
            
            return result["output"]
            
        except Exception as e:
            print(f"CRITICAL AGENT ERROR: {e}")
            logger.error(f"Agent chat error: {e}")
            return "I apologize, but I'm having trouble processing your request right now. Please try again later."

# Singleton instance
receptionist_agent = ReceptionistAgent()
