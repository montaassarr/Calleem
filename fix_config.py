#!/usr/bin/env python3
"""Fix MongoDB business config to match Pydantic model"""
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from datetime import datetime

async def fix_config():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.ai_barber_receptionist
    
    # Delete old config
    await db.business_configs.delete_many({})
    print("✅ Cleared old config")
    
    # Insert correct config matching BusinessConfigBase model
    correct_config = {
        "business_id": "default",
        "business_name": "Royal Fade Barbershop",
        "business_phone": "+216 20 123 456",
        "business_email": "contact@royalfade.tn",
        "business_address": "123 Avenue Habib Bourguiba, Tunis",
        "timezone": "Africa/Tunis",
        
        # opening_hours (not business_hours) with open/close/closed fields
        "opening_hours": [
            {"day": "monday", "open": "09:00", "close": "19:00", "closed": False},
            {"day": "tuesday", "open": "09:00", "close": "19:00", "closed": False},
            {"day": "wednesday", "open": "09:00", "close": "19:00", "closed": False},
            {"day": "thursday", "open": "09:00", "close": "19:00", "closed": False},
            {"day": "friday", "open": "09:00", "close": "20:00", "closed": False},
            {"day": "saturday", "open": "10:00", "close": "20:00", "closed": False},
            {"day": "sunday", "open": "00:00", "close": "00:00", "closed": True}
        ],
        
        # services with description and active fields
        "services": [
            {
                "name": "Classic Haircut",
                "description": "Traditional haircut with scissors and clippers",
                "duration_minutes": 30,
                "price": 25.0,
                "active": True
            },
            {
                "name": "Beard Trim",
                "description": "Professional beard shaping and trimming",
                "duration_minutes": 20,
                "price": 15.0,
                "active": True
            },
            {
                "name": "Royal Fade",
                "description": "Premium fade haircut with styling",
                "duration_minutes": 45,
                "price": 40.0,
                "active": True
            }
        ],
        
        # Capacity settings
        "max_clients_per_day": 20,
        "default_appointment_duration": 30,
        
        # AI config
        "ai_config": {
            "model": "llama-3.1-70b-versatile",
            "temperature": 0.7,
            "max_tokens": 500,
            "system_prompt": "You are Ava, a friendly and professional AI receptionist for Royal Fade Barbershop in Tunis, Tunisia. Help customers book appointments, answer questions about services, and provide excellent customer service.",
            "voice_enabled": False,
            "voice_model": "whisper-large-v3"
        },
        
        # WhatsApp config
        "whatsapp_config": {
            "phone_number_id": "897432366779845",
            "access_token": "",
            "verify_token": "",
            "webhook_url": ""
        },
        
        # Additional fields
        "active": True,
        "features_enabled": {
            "whatsapp": True,
            "voice_calls": False,
            "sms": False
        },
        
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await db.business_configs.insert_one(correct_config)
    print(f"✅ Inserted correct config: {result.inserted_id}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_config())
