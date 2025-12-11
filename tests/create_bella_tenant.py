#!/usr/bin/env python3
"""
Create Bella's Hair Salon Tenant User
Links to the existing Vapi assistant
"""

import asyncio
import httpx
from datetime import datetime

BACKEND_URL = "http://localhost:8000/api/v1"
BELLA_ASSISTANT_ID = "8c250351-532d-4399-9b0c-85ec8bde4f1e"

# Bella's Salon credentials
BELLA_USER = {
    "email": "bella@hairsalon.test",
    "password": "BellaSalon123!",
    "name": "Bella Martinez",
    "business_name": "Bella's Hair Salon"
}

async def main():
    print("="*60)
    print("🏪 CREATING BELLA'S HAIR SALON TENANT")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Step 1: Register new user
        print("\n📝 Step 1: Registering user...")
        register_response = await client.post(
            f"{BACKEND_URL}/auth/register",
            json={
                "email": BELLA_USER["email"],
                "password": BELLA_USER["password"],
                "name": BELLA_USER["name"],
                "business_name": BELLA_USER["business_name"]
            }
        )
        
        if register_response.status_code == 200:
            data = register_response.json()
            print(f"   ✅ User registered: {BELLA_USER['email']}")
            access_token = data.get("access_token")
            user_data = data.get("user", {})
            tenant_id = user_data.get("tenant_id")
            print(f"   Tenant ID: {tenant_id}")
        elif register_response.status_code == 400:
            print(f"   ⚠️ User may already exist, trying login...")
            # Try login instead
            login_response = await client.post(
                f"{BACKEND_URL}/auth/login",
                data={
                    "username": BELLA_USER["email"],
                    "password": BELLA_USER["password"]
                }
            )
            if login_response.status_code == 200:
                data = login_response.json()
                access_token = data.get("access_token")
                print(f"   ✅ Logged in successfully")
                
                # Get user info
                me_response = await client.get(
                    f"{BACKEND_URL}/auth/me",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                if me_response.status_code == 200:
                    user_data = me_response.json()
                    tenant_id = user_data.get("tenant_id")
                    print(f"   Tenant ID: {tenant_id}")
            else:
                print(f"   ❌ Login failed: {login_response.text}")
                return
        else:
            print(f"   ❌ Registration failed: {register_response.status_code}")
            print(f"   Error: {register_response.text}")
            return
        
        # Step 2: Link Vapi Assistant to tenant
        print("\n🔗 Step 2: Linking Vapi assistant to tenant...")
        
        auth_headers = {"Authorization": f"Bearer {access_token}"}
        
        # Check current assistant
        assistant_response = await client.get(
            f"{BACKEND_URL}/assistant/me",
            headers=auth_headers
        )
        
        if assistant_response.status_code == 200:
            current = assistant_response.json()
            if current.get("configured") and current.get("assistant_id"):
                print(f"   ℹ️  Already has assistant: {current.get('assistant_id')}")
            else:
                print(f"   Current status: {current}")
        
        # Create/update assistant config
        print("\n🤖 Step 3: Creating assistant via backend API...")
        create_response = await client.post(
            f"{BACKEND_URL}/assistant/me",
            headers=auth_headers,
            json={
                "voice": "jennifer",
                "voice_provider": "11labs",
                "instructions": """You are Sarah, the friendly AI receptionist for Bella's Hair Salon.
                
Services: 
- Women's Haircut: $45-65
- Men's Haircut: $30-40
- Full Color: $85-120
- Highlights: $95-185
- Blowout: $45

Hours: Tue-Fri 9AM-7PM, Sat 9AM-6PM, Sun 10AM-4PM, Closed Monday

Always collect name, phone, service, and preferred date/time when booking.""",
                "first_message": "Hi! Thank you for calling Bella's Hair Salon, this is Sarah. How can I help you today?",
                "company_name": "Bella's Hair Salon"
            }
        )
        
        if create_response.status_code == 200:
            result = create_response.json()
            print(f"   ✅ Assistant created!")
            print(f"   Assistant ID: {result.get('assistant_id')}")
        else:
            print(f"   ⚠️ Create response: {create_response.status_code}")
            print(f"   {create_response.text[:300]}")
        
        # Step 4: Verify the setup
        print("\n✅ Step 4: Verifying setup...")
        verify_response = await client.get(
            f"{BACKEND_URL}/assistant/me",
            headers=auth_headers
        )
        
        if verify_response.status_code == 200:
            final = verify_response.json()
            print(f"   Configured: {final.get('configured')}")
            print(f"   Assistant ID: {final.get('assistant_id')}")
            print(f"   Name: {final.get('name')}")
        
        print("\n" + "="*60)
        print("🎉 BELLA'S HAIR SALON TENANT READY!")
        print("="*60)
        print(f"""
Login Credentials:
   Email: {BELLA_USER['email']}
   Password: {BELLA_USER['password']}

Dashboard URL: http://localhost:3000/login
Then go to: Voice Agent → Control Center

The tenant can now:
- Configure their AI assistant
- Test calls from the dashboard
- View call analytics
""")


if __name__ == "__main__":
    asyncio.run(main())
