import os
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017"))
db = client["ai_barber_receptionist"]
agents_collection = db["agents"]

tenant_id = "69319a0e7436614acd86b5d5"

# Agent Config
agent_data = {
    "tenant_id": tenant_id,
    "name": "Hakimi AI Receptionist",
    "status": "active",
    "voice_settings": {
        "provider": "elevenlabs",
        "voice_id": "21m00Tcm4TlvDq8ikWAM" # Rachel
    },
    "tts_model": "elevenlabs/eleven_multilingual_v2",
    "voice_provider": "elevenlabs",
    "stt_model": "deepgram/nova-3",
    "llm_model": "groq/llama-3.3-70b-versatile",
    "system_prompt": "You are the AI receptionist for Hakimi, a premium barber shop. Keep it brief."
}

# Updates with upsert=True
result = agents_collection.update_one(
    {"tenant_id": tenant_id},
    {"$set": agent_data},
    upsert=True
)

print(f"Matched: {result.matched_count}, Modified: {result.modified_count}, Upserted: {result.upserted_id}")
