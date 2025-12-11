#!/usr/bin/env python3
"""
Add Cartesia API key to your tenant configuration
"""
from pymongo import MongoClient
from utils.encryption import encrypt_value
import uuid
from datetime import datetime

# Your Cartesia API key - GET IT FROM: https://cartesia.ai
CARTESIA_API_KEY = input("Enter your Cartesia API key: ").strip()

if not CARTESIA_API_KEY:
    print("❌ No API key provided")
    exit(1)

# Connect to database
client = MongoClient("mongodb://localhost:27017/")
db = client["callflow_ai_saas"]

tenant_id = "692f43697c982c08898e127b"

# Encrypt the API key
encrypted_key = encrypt_value(CARTESIA_API_KEY)

# Create the API key object
cartesia_key = {
    "id": str(uuid.uuid4()),
    "provider": "cartesia",
    "name": "Voice TTS",
    "masked_key": "•" * (len(CARTESIA_API_KEY) - 4) + CARTESIA_API_KEY[-4:],
    "encrypted_key": encrypted_key,
    "created_at": datetime.utcnow(),
    "last_used": None,
    "is_valid": True
}

# Add to business_config
result = db.business_config.update_one(
    {"tenant_id": tenant_id},
    {"$push": {"api_keys": cartesia_key}}
)

if result.modified_count > 0:
    print("✅ Cartesia API key added successfully!")
    print("\nNow restart the LiveKit agent:")
    print("  pkill -f livekit-agent")
    print("  cd livekit-agent-worker && bash start.sh &")
else:
    print("❌ Failed to add API key")
