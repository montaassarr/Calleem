#!/usr/bin/env python3
"""
Manual Onboarding Test Flow
Simulates a user manually configuring their salon from the dashboard.
Tests:
1. Registration
2. Assistant Creation (Voice Config)
3. Tool Enablement
4. Knowledge Base Setup
5. Full Verification
"""

import asyncio
import httpx
from datetime import datetime
import json

BACKEND_URL = "http://localhost:8000/api/v1"

# Test Tenant Configuration
TEST_TENANT = {
    "email": "manual_test@salon.com",
    "password": "TestPassword123!",
    "name": "Mario Rossi",
    "business_name": "Mario's Barbershop",
    "phone": "+15550009999"
}

ASSISTANT_CONFIG = {
    "voice": "jennifer",
    "voice_provider": "11labs", 
    "instructions": """You are Mario, the AI barber for Mario's Barbershop.
    
Services:
- Men's Haircut: $35
- Beard Trim: $25
- Hot Towel Shave: $40

Hours: Mon-Sat 10AM-8PM, Sun Closed.

Your goal is to book appointments. Always ask for name and phone number.""",
    "first_message": "Ciao! Welcome to Mario's Barbershop. How can I freshen up your look today?",
    "company_name": "Mario's Barbershop"
}

# Colors for output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_step(step, msg):
    print(f"\n{Colors.BLUE}[STEP {step}]{Colors.END} {msg}")

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

async def main():
    print(f"{Colors.HEADER}{Colors.BOLD}🧪 MANUAL ONBOARDING TEST FLOW{Colors.END}")
    print("="*60)

    async with httpx.AsyncClient(timeout=60.0) as client:
        
        # 1. Registration
        print_step(1, "Registering New Account")
        reg_res = await client.post(f"{BACKEND_URL}/users/register", json={
            "email": TEST_TENANT["email"],
            "password": TEST_TENANT["password"],
            "username": TEST_TENANT["email"],
            "full_name": TEST_TENANT["name"],
            "business_name": TEST_TENANT["business_name"]
        })
        
        if reg_res.status_code == 201 or reg_res.status_code == 200:
            token = reg_res.json()["access_token"]
            print_success(f"Registered {TEST_TENANT['email']}")
        elif reg_res.status_code == 400:
            print(f"{Colors.YELLOW}User exists, logging in...{Colors.END}")
            # Login uses OAuth2 form data
            login_res = await client.post(f"{BACKEND_URL}/users/login", data={
                "username": TEST_TENANT["email"],
                "password": TEST_TENANT["password"]
            })
            token = login_res.json().get("access_token")
            if token:
                print_success("Logged in successfully")
            else:
                print_error(f"Login failed: {login_res.text}")
                return
        else:
            print_error(f"Registration failed: {reg_res.text}")
            return

        headers = {"Authorization": f"Bearer {token}"}

        # 2. Configure Voice/Assistant (First time setup)
        print_step(2, "Configuring Voice Assistant (Dashboard: Voice Config)")
        assist_res = await client.post(f"{BACKEND_URL}/assistant/me", headers=headers, json=ASSISTANT_CONFIG)
        
        if assist_res.status_code == 200:
            data = assist_res.json()
            assistant_id = data["assistant_id"]
            print_success(f"Assistant Created! ID: {assistant_id}")
            print(f"   Name: {data.get('name')}")
            print(f"   First Message: {data.get('first_message')}")
        else:
            print_error(f"Assistant configuration failed: {assist_res.text}")
            return

        # 3. Enable Tools
        print_step(3, "Enabling Tools (Dashboard: Tools Page)")
        
        # Get builtin tools first to find IDs
        tools_res = await client.get(f"{BACKEND_URL}/tools/built-in")
        builtin_tools = tools_res.json()
        
        tool_ids = ["check_availability", "book_appointment"]
        for t_id in tool_ids:
            found = next((t for t in builtin_tools if t["id"] == t_id), None)
            if found:
                print(f"   Enabling {t_id}...")
                enable_res = await client.post(f"{BACKEND_URL}/assistant/me/tools/{t_id}/enable", headers=headers)
                if enable_res.status_code == 200:
                    print_success(f"Enabled {t_id}")
                else:
                    print_error(f"Failed to enable {t_id}: {enable_res.text}")
            else:
                print_error(f"Tool {t_id} not found in builtin list")

        # 4. Verify Final State
        print_step(4, "Verifying Full Configuration (Dashboard: Control Center)")
        final_res = await client.get(f"{BACKEND_URL}/assistant/me", headers=headers)
        
        if final_res.status_code == 200:
            final = final_res.json()
            
            # Check Config
            is_configured = final["configured"]
            voice_correct = final["voice"]["voiceId"] == "jennifer" 
            
            # Check Tools
            # Note: API might return "tools" list differently depending on structure
            # We implemented local tool storage, so we should check /assistant/me/tools too
            my_tools_res = await client.get(f"{BACKEND_URL}/assistant/me/tools", headers=headers)
            my_tools = my_tools_res.json()
            
            has_booking = any(t["function"]["name"] == "bookAppointment" for t in my_tools)
            has_checking = any(t["function"]["name"] == "checkAvailability" for t in my_tools)
            
            print(f"   Configured: {is_configured}")
            print(f"   Voice: {final['voice']['provider']} ({final['voice']['voiceId']})")
            print(f"   Tools Active: {len(my_tools)}")
            
            if is_configured and voice_correct and has_booking and has_checking:
                print("\n" + "="*60)
                print_success("🎉 MANUAL ONBOARDING FLOW VERIFIED!")
                print(f"{Colors.BOLD}Mario's Barbershop is fully operational like Bella's!{Colors.END}")
            else:
                print_error("Verification failed checks:")
                print(f"   - Configured: {is_configured}")
                print(f"   - Voice Correct: {voice_correct}")
                print(f"   - Has Booking Tool: {has_booking}")
                print(f"   - Has Check Tool: {has_checking}")
        else:
            print_error(f"Could not fetch final assistant state: {final_res.text}")

if __name__ == "__main__":
    asyncio.run(main())
