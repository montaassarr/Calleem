"""
Live call transfer: urgent calls (a burst pipe, flooding, no heat, a caller who insists on a person)
are put straight through to the business owner's phone, tenant["transfer_phone_number"].

- The number is stored on the tenant only. Each time the assistant's tools are synced to Vapi
  (AssistantService._sync_tools_to_vapi), the transfer_call tool gets it as its destination.
  Without a number the tool is left out: a transferCall with no destination makes Vapi ask our
  server where to send the call, and we don't answer that.
- The rules telling the assistant when to transfer follow the tools, not the tenant: VapiService
  adds them to the system prompt of an assistant whose tools can transfer and takes them out
  otherwise, so the prompt never offers a transfer the assistant can't make.
- Transfers are blind (Vapi's default): the caller hears the hold message and the call rings the
  owner's phone; the assistant is no longer on the call.
"""

import re
from typing import Any, Dict, List, Optional

from services import voice_languages

TOOL_ID = "transfer_call"

# Said by the assistant's voice while Vapi connects the caller, so it is in the assistant's language.
HOLD_MESSAGES = {
    voice_languages.DEFAULT_LANGUAGE: "Please hold, I'm connecting you now.",
    voice_languages.TUNISIAN: "ثانية برك، توّا نحوّلك.",
}
DESTINATION_DESCRIPTION = "Transfer to the business owner for emergencies or when the caller asks for a person"

# Who the caller must call instead when there is gas or danger; that rule always wins over a transfer.
EMERGENCY_SERVICES = {
    voice_languages.DEFAULT_LANGUAGE: "911 or the gas company",
    voice_languages.TUNISIAN: "the civil protection or the gas company",
}

RULES_PATTERN = re.compile(r"\s*<call_transfer>.*?</call_transfer>", re.DOTALL)


def vapi_tool(number: Optional[str], language: str = voice_languages.DEFAULT_LANGUAGE) -> Optional[Dict[str, Any]]:
    """The Vapi transferCall tool putting calls through to `number` (E.164), or None without a number."""
    if not number:
        return None
    return {
        "type": "transferCall",
        "destinations": [{
            "type": "number",
            "number": number,
            "message": HOLD_MESSAGES[voice_languages.normalize(language)],
            "description": DESTINATION_DESCRIPTION,
        }],
    }


def can_transfer(tools: Optional[List[Dict[str, Any]]]) -> bool:
    """True if these Vapi tools include a transferCall that has somewhere to send the call."""
    return any(
        isinstance(tool, dict) and tool.get("type") == "transferCall" and bool(tool.get("destinations"))
        for tool in tools or []
    )


def prompt_rules(language: str) -> str:
    """When and how to transfer, appended to the system prompt of an assistant that can transfer."""
    emergency_services = EMERGENCY_SERVICES[voice_languages.normalize(language)]
    return f"""<call_transfer>
TRANSFERRING URGENT CALLS: the transferCall tool puts the caller straight through to the business owner's phone. For the calls below, a transfer replaces booking a visit or promising a callback.
- Transfer when it is an emergency that can't wait (for example water actively leaking, a burst pipe or flooding, sewage backing up, or no heat in freezing weather), or when the caller clearly asks to speak to a person.
- Safety comes first: if the caller smells gas or anyone is in danger, tell them to leave the building and call {emergency_services} from outside. Do not transfer that call.
- Before transferring, give any quick safety step from your instructions (like shutting off the main water valve if it is safe). If the caller is calm enough, first get their name, phone number and the service address, one question at a time; if they are panicking, transfer right away.
- Then call transferCall at once. It tells the caller to hold, so don't announce the transfer yourself, and you don't need to book anything first.
- Handle everything else yourself (questions, prices, regular bookings), and never read out the number you transfer to.
</call_transfer>"""


def with_prompt_rules(prompt: str, language: str, tools: Optional[List[Dict[str, Any]]]) -> str:
    """`prompt` ending with the transfer rules if the tools can transfer, and without them otherwise."""
    prompt = RULES_PATTERN.sub("", prompt or "")
    if can_transfer(tools):
        prompt = f"{prompt.rstrip()}\n\n{prompt_rules(language)}"
    return prompt


def sync_prompt_rules(model: Dict[str, Any], language: str, tools: Optional[List[Dict[str, Any]]] = None) -> None:
    """Apply with_prompt_rules to the system message of a Vapi model config; tools default to the model's own."""
    messages = model.get("messages") or []
    for index, message in enumerate(messages):
        if isinstance(message, dict) and message.get("role") == "system":
            if isinstance(message.get("content") or "", str):
                content = with_prompt_rules(
                    message.get("content") or "", language, model.get("tools") if tools is None else tools
                )
                model["messages"] = [*messages[:index], {**message, "content": content}, *messages[index + 1:]]
            return
