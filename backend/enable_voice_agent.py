"""Enable voice agent feature in business config"""

import asyncio
from database.mongo_config import get_database
from datetime import datetime


async def enable_voice_agent():
    db = get_database()
    
    # Check if config exists
    config = await db.business_configs.find_one({"business_id": "default"})
    
    if not config:
        # Create new config with voice agent enabled
        await db.business_configs.insert_one({
            "business_id": "default",
            "business_name": "Royal Fade Barbershop",
            "features_enabled": {
                "voice_agent": True,
                "whatsapp": True,
                "appointments": True
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
        print("✓ Created new business config with voice agent enabled")
    else:
        # Update existing config
        await db.business_configs.update_one(
            {"business_id": "default"},
            {
                "$set": {
                    "features_enabled.voice_agent": True,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        print("✓ Updated business config - voice agent enabled")
    
    # Verify
    updated = await db.business_configs.find_one({"business_id": "default"})
    print(f"\nVoice agent enabled: {updated.get('features_enabled', {}).get('voice_agent')}")


if __name__ == "__main__":
    asyncio.run(enable_voice_agent())
