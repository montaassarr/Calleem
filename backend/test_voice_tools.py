import asyncio
import logging
from datetime import datetime, timedelta
from voice_agent.tools import voice_tools
from database.mongo_config import connect_to_mongo

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_tools():
    print("🔌 Connecting to MongoDB...")
    await connect_to_mongo()
    
    print("\n🛠️  Testing Voice Tools...")
    
    # 1. Get Services
    print("\n1. Testing 'get_services'...")
    result = await voice_tools.execute_tool("get_services", {}, "default")
    print(f"Result: {result}")
    
    if not result.get("success"):
        print("❌ Failed to get services")
    elif not result.get("services"):
        print("⚠️  Success but no services found. Database might be empty.")
    else:
        print(f"✅ Found {len(result['services'])} services")

    # 2. Check Availability (Next Monday)
    today = datetime.now()
    days_ahead = 7 - today.weekday() # Days until next Monday (0)
    if days_ahead <= 0: days_ahead += 7
    next_monday = (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
    
    print(f"\n2. Testing 'check_availability' for {next_monday}...")
    result = await voice_tools.execute_tool("check_availability", {"date": next_monday}, "default")
    print(f"Result: {result}")
    
    if not result.get("success"):
        print("❌ Failed to check availability")
    else:
        slots = result.get("available_slots", [])
        print(f"✅ Found {len(slots)} available slots")

if __name__ == "__main__":
    asyncio.run(test_tools())
