from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.client import User, Users
from diagrams.onprem.compute import Server
from diagrams.onprem.database import MongoDB
from diagrams.programming.framework import React, FastAPI
from diagrams.programming.language import Python, TypeScript
from diagrams.saas.chat import Slack
from diagrams.onprem.container import Docker
from diagrams.generic.device import Mobile, Tablet
# from diagrams.generic.os import Linux

# If FastAPI is not available, we can use Python
try:
    from diagrams.programming.framework import FastAPI
except ImportError:
    from diagrams.programming.language import Python as FastAPI

with Diagram("CallFlow AI Architecture", show=False, direction="LR"):
    user = User("Business Owner")
    end_user = Users("End Users (Callers)")

    with Cluster("Client Side"):
        dashboard = React("Next.js Dashboard\n(App Router)")
        
    with Cluster("Server Side"):
        with Cluster("Backend API"):
            backend = FastAPI("FastAPI Server\n(Python 3.11)")
        
        with Cluster("Database"):
            mongo = MongoDB("MongoDB\n(Multi-tenant)")

        with Cluster("AI Voice Agent"):
            agent = Python("LiveKit Worker\n(Python)")
            
        with Cluster("Workflows"):
            n8n = Docker("n8n Workflows\n(Webhooks)")

    with Cluster("External Services"):
        livekit_cloud = Server("LiveKit Cloud")
        openai = Server("OpenAI\n(LLM)")
        deepgram = Server("Deepgram\n(STT)")
        elevenlabs = Server("ElevenLabs\n(TTS)")

    # Connections
    user >> dashboard
    dashboard >> backend
    backend >> mongo
    
    # Agent flow
    end_user >> livekit_cloud
    livekit_cloud >> agent
    agent >> openai
    agent >> deepgram
    agent >> elevenlabs
    
    # Backend control
    backend >> agent
    
    # N8N integration
    agent >> n8n
    n8n >> backend
    
    # Dashboard config
    dashboard >> livekit_cloud
