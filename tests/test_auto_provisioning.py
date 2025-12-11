#!/usr/bin/env python3
"""
Test Auto-Provisioning
Verifies that registering a new user AUTOMATICALLY creates and configures a Vapi assistant.
"""

import asyncio
import httpx
import time
import random

BACKEND_URL = "http://localhost:8000/api/v1"

# Generate random user to avoid conflicts
RANDOM_ID = str(int(time.time()))[-6:]
TEST_USER = {
    "email": f"auto_test_{RANDOM_ID}@provisioning.com",
    "password": "TestPassword123!",
    "name": f"Auto Test {RANDOM_ID}",
    "business_name": f"Auto Salon {RANDOM_ID}"
}

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
END = '\033[0m'

async def main():
    print(f"{BLUE}🚀 TESTING VAPI AUTO-PROVISIONING{END}")
    print(f"Target: {TEST_USER['email']}")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # 1. Register
        print("\n📝 1. Registering user...", end=" ")
        reg_res = await client.post(f"{BACKEND_URL}/users/register", json={
            "email": TEST_USER["email"],
            "password": TEST_USER["password"],
            "username": TEST_USER["email"],
            "full_name": TEST_USER["name"],
            "business_name": TEST_USER["business_name"]
        })
        
        if reg_res.status_code not in [200, 201]:
            print(f"{RED}FAILED{END}")
            print(reg_res.text)
            return
            
        token = reg_res.json()["access_token"]
        print(f"{GREEN}SUCCESS{END}")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Check Assistant Immediately
        print("🤖 2. Checking Assistant Status...", end=" ")
        
        # Poll briefly as it might take a second if running async (though we awaited it)
        assist_res = await client.get(f"{BACKEND_URL}/assistant/me", headers=headers)
        
        if assist_res.status_code != 200:
            print(f"{RED}FAILED (API Error){END}")
            print(assist_res.text)
            return
            
        data = assist_res.json()
        
        if data.get("configured") is True and data.get("assistant_id"):
            print(f"{GREEN}SUCCESS{END}")
            print(f"   Assistant ID: {data['assistant_id']}")
            print(f"   Name: {data.get('name')}")
            print(f"   Voice: {data.get('voice', {}).get('voiceId')}")
            
            # 3. Check Tools
            # Check the tools returned in assistant config
            # OR check /assistant/me/tools endpoint if implemented
            tools = data.get("tools", [])
            tool_names = [t.get("function", {}).get("name") for t in tools]
            
            print(f"🛠️  3. Tools Enabled: {tool_names}")
            
            if "checkAvailability" in tool_names and "bookAppointment" in tool_names:
                print(f"\n{GREEN}✅ VERIFICATION PASSED: Full Vapi Auto-Provisioning Works!{END}")
            else:
                print(f"\n{RED}⚠️ PARTIAL SUCCESS: Assistant created but tools missing.{END}")
                print(f"Expected checkAvailability, bookAppointment. Found: {tool_names}")
                
        else:
            print(f"{RED}FAILED{END}")
            print(f"   Assistant NOT configured automatically.")
            print(f"   Response: {data}")

if __name__ == "__main__":
    asyncio.run(main())
