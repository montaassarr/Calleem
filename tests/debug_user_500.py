#!/usr/bin/env python3
"""
Debug Script for User 500 Error
Tries to enable a tool for the specific user reporting the issue.
"""
import asyncio
import httpx

BACKEND_URL = "http://localhost:8000/api/v1"
USER_EMAIL = "montamsallem@gmail.com"
USER_PASS = "Mariemmontassar03$"

async def main():
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Login
        print(f"Logging in as {USER_EMAIL}...")
        res = await client.post(f"{BACKEND_URL}/users/login", data={
            "username": USER_EMAIL, 
            "password": USER_PASS
        })
        
        if res.status_code != 200:
            print(f"Login failed: {res.status_code} {res.text}")
            return
            
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Check current state (expecting configured=False or 404 from tools)
        print("Checking assistant status...")
        assist = await client.get(f"{BACKEND_URL}/assistant/me", headers=headers)
        print(f"Assistant status: {assist.status_code}")
        print(assist.text)
        
        # Try converting "checkAvailability" tool (simulate enable toggle)
        print("Attempting to enable 'checkAvailability'...")
        # Note: Tools endpoint usually just needs tool_id
        enable_res = await client.post(
            f"{BACKEND_URL}/assistant/me/tools/checkAvailability/enable", 
            headers=headers
        )
        print(f"Enable Tool Response: {enable_res.status_code}")
        print(enable_res.text)

if __name__ == "__main__":
    asyncio.run(main())
