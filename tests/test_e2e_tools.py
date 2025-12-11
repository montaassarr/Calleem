#!/usr/bin/env python3
"""
End-to-End Test: Vapi Tools Integration
Tests: Login → Enable Tools → Verify Vapi Sync → Simulate Tool Calls
"""

import asyncio
import os
import sys
import httpx
from datetime import datetime, timedelta

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from dotenv import load_dotenv
load_dotenv("backend/.env", override=True)

BACKEND_URL = "http://localhost:8000/api/v1"
TEST_EMAIL = "montamsallem@gmail.com"
TEST_PASSWORD = "password123"  # Adjust if different

async def login():
    """Login and get auth token"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BACKEND_URL}/users/login",
            data={"username": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token")
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None

async def get_assistant_info(token: str):
    """Get current assistant info"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{BACKEND_URL}/assistant/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            return response.json()
        return None

async def enable_tool(token: str, tool_id: str):
    """Enable a tool"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BACKEND_URL}/assistant/me/tools/{tool_id}/enable",
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.status_code == 200, response.text

async def disable_tool(token: str, tool_id: str):
    """Disable a tool"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.delete(
            f"{BACKEND_URL}/assistant/me/tools/{tool_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.status_code == 200, response.text

async def get_enabled_tools(token: str):
    """Get enabled tools list"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{BACKEND_URL}/assistant/me/tools",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            return response.json()
        return []

async def check_vapi_tools(assistant_id: str):
    """Check tools configured in Vapi"""
    from services.vapi_service import vapi_service
    details = await vapi_service.get_assistant(assistant_id)
    if details:
        model = details.get("model", {})
        return model.get("tools", [])
    return []

async def simulate_check_availability(token: str, date: str):
    """Simulate checking availability via API"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{BACKEND_URL}/appointments/availability?date={date}",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            return response.json()
        return {"error": response.text}

async def simulate_book_appointment(token: str, date: str, time: str, name: str, phone: str):
    """Simulate booking an appointment via API"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BACKEND_URL}/appointments/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "date": date,
                "time": time,
                "customer_name": name,
                "customer_phone": phone,
                "service": "Haircut"
            }
        )
        return response.status_code, response.json() if response.status_code in [200, 201] else response.text

async def run_e2e_test():
    print("=" * 60)
    print("🧪 E2E TEST: Vapi Tools Integration")
    print("=" * 60)
    
    # Step 1: Login
    print("\n📌 Step 1: Login")
    token = await login()
    if not token:
        print("❌ Cannot proceed without auth token")
        return False
    print(f"✅ Logged in successfully")
    
    # Step 2: Get assistant info
    print("\n📌 Step 2: Get Assistant Info")
    assistant = await get_assistant_info(token)
    if not assistant:
        print("❌ Failed to get assistant info")
        return False
    assistant_id = assistant.get("assistant_id")
    print(f"✅ Assistant ID: {assistant_id}")
    
    # Step 3: Disable and re-enable tools to force sync
    print("\n📌 Step 3: Sync Tools to Vapi")
    
    # First disable both
    print("   Disabling check_availability...")
    success, msg = await disable_tool(token, "check_availability")
    print(f"   {'✅' if success else '❌'} Disable check_availability: {msg[:100] if not success else 'OK'}")
    
    print("   Disabling book_appointment...")
    success, msg = await disable_tool(token, "book_appointment")
    print(f"   {'✅' if success else '❌'} Disable book_appointment: {msg[:100] if not success else 'OK'}")
    
    # Now enable both
    print("   Enabling check_availability...")
    success, msg = await enable_tool(token, "check_availability")
    print(f"   {'✅' if success else '❌'} Enable check_availability: {msg[:100] if not success else 'OK'}")
    
    print("   Enabling book_appointment...")
    success, msg = await enable_tool(token, "book_appointment")
    print(f"   {'✅' if success else '❌'} Enable book_appointment: {msg[:100] if not success else 'OK'}")
    
    # Step 4: Verify Vapi has the tools
    print("\n📌 Step 4: Verify Vapi Configuration")
    vapi_tools = await check_vapi_tools(assistant_id)
    print(f"   Vapi Tools Count: {len(vapi_tools)}")
    for tool in vapi_tools:
        func_name = tool.get("function", {}).get("name", "unknown")
        server_url = tool.get("server", {}).get("url", "NO URL")
        print(f"   - {func_name}: {server_url[:50]}...")
    
    if len(vapi_tools) < 2:
        print("❌ Tools not properly synced to Vapi!")
        return False
    print("✅ Tools synced to Vapi successfully!")
    
    # Step 5: Test availability check
    print("\n📌 Step 5: Test Availability Check")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    availability = await simulate_check_availability(token, tomorrow)
    print(f"   Availability for {tomorrow}: {availability}")
    
    # Step 6: Test booking
    print("\n📌 Step 6: Test Appointment Booking")
    status, result = await simulate_book_appointment(
        token,
        tomorrow,
        "14:00",
        "Test Customer",
        "+1234567890"
    )
    print(f"   Booking Result ({status}): {result}")
    
    if status in [200, 201]:
        print("✅ Appointment booked successfully!")
    else:
        print(f"⚠️ Booking returned {status}")
    
    print("\n" + "=" * 60)
    print("🎉 E2E TEST COMPLETE")
    print("=" * 60)
    return True

if __name__ == "__main__":
    asyncio.run(run_e2e_test())
