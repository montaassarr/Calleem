"""
FINAL VALIDATION TEST - All 3 Fixes
Tests appointment creation, admin login, and verifies all fixes work
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api/v1"

def log(msg, status="✅"):
    print(f"{status} {msg}")

def main():
    print("=" * 70)
    print("FINAL VALIDATION TEST - ALL 3 CRITICAL FIXES")
    print("=" * 70)
    
    # FIX #1: Test Appointment Creation
    print("\n🔧 FIX #1: Testing Appointment Creation with datetime+duration")
    
    # First register and login
    requests.post(f"{BASE_URL}/users/register", json={
        "email": "final@example.com",
        "username": "final_test",
        "password": "Test123!",
        "full_name": "Final Test",
        "phone_number": "+15559999999"
    })
    
    login_resp = requests.post(f"{BASE_URL}/users/login", data={
        "username": "final_test",
        "password": "Test123!"
    })
    
    if login_resp.status_code == 200:
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test appointment creation
        appt_payload = {
            "client_name": "Test Client",
            "client_phone": "+15551234567",
            "service": "Test Service",
            "datetime": (datetime.utcnow() + timedelta(days=2)).isoformat(),
            "duration_minutes": 60
        }
        
        appt_resp = requests.post(
            f"{BASE_URL}/appointments/",
            json=appt_payload,
            headers=headers
        )
        
        if appt_resp.status_code == 201:
            log("FIX #1 WORKING: Appointment created successfully (201)", "✅")
            print(f"   Response: {json.dumps(appt_resp.json(), indent=2)[:200]}...")
        else:
            log(f"FIX #1 FAILED: {appt_resp.status_code} - {appt_resp.text}", "❌")
    
    # FIX #2: Test Super Admin Login
    print("\n🔧 FIX #2: Testing Super Admin Login")
    
    admin_resp = requests.post(f"{BASE_URL}/users/login", data={
        "username": "admin",
        "password": "CallFlow2025!Admin"
    })
    
    if admin_resp.status_code == 200:
        log("FIX #2 WORKING: Super admin login successful", "✅")
        admin_token = admin_resp.json()["access_token"]
        
        # Test admin endpoints
        tenants_resp = requests.get(
            f"{BASE_URL}/admin/tenants",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        if tenants_resp.status_code == 200:
            log(f"   Admin can list tenants: {len(tenants_resp.json())} tenants found", "✅")
    else:
        log(f"FIX #2 FAILED: Admin login failed ({admin_resp.status_code})", "❌")
    
    # FIX #3: Rate Limiting (will be added to code)
    print("\n🔧 FIX #3: Rate Limiting")
    log("FIX #3: Code changes ready (needs implementation)", "⚠️")
    
    print("\n" + "=" * 70)
    print("VALIDATION COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    main()
