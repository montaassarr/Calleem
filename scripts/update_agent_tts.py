import os
from pymongo import MongoClient
from bson import ObjectId

# Connect to MongoDB
client = MongoClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017"))
db = client["ai_receptionist"]
agents_collection = db["agents"]

tenant_id = "69319a0e7436614acd86b5d5"

# Update the agent configuration
result = agents_collection.update_one(
    {"tenant_id": tenant_id},
    {
        "$set": {
            "tts_model": "elevenlabs/eleven_multilingual_v2",
            "voice_provider": "elevenlabs",
            "voice_id": "21m00Tcm4TlvDq8ikWAM" # Rachel or similar default
        }
    }
)

print(f"Matched: {result.matched_count}, Modified: {result.modified_count}")

# Verify
agent = agents_collection.find_one({"tenant_id": tenant_id})
print("Updated Agent Config:", agent)
