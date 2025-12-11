#!/usr/bin/env python3
"""
Create a customer user for testing
"""
import requests

BACKEND_URL = "http://localhost:8000/api/v1"
OWNER_EMAIL = "montamsallem@gmail.com"
OWNER_PASSWORD = "Mariemmontassar03$"

def login_as_owner():
    """Login as owner"""
    print("🔐 Logging in as owner...")
    response = requests.post(
        f"{BACKEND_URL}/users/login",
        data={"username": OWNER_EMAIL, "password": OWNER_PASSWORD},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Owner login successful")
        print(f"   User ID: {data.get('user_id')}")
        print(f"   Tenant ID: {data.get('tenant_id')}")
        return data["access_token"], data.get('tenant_id')
    else:
        print(f"❌ Owner login failed: {response.text}")
        return None, None

def create_customer(token):
    """Create a customer user"""
    print("\n👤 Creating customer user...")
    customer_data = {
        "email": "customer@test.com",
        "password": "TestPassword123",
        "full_name": "Test Customer",
        "phone": "+1234567890",
        "role": "customer"
    }
    
    response = requests.post(
        f"{BACKEND_URL}/users",
        json=customer_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        customer = response.json()
        print(f"✅ Customer created successfully")
        print(f"   Email: {customer.get('email')}")
        print(f"   Name: {customer.get('full_name')}")
        print(f"   ID: {customer.get('id')}")
        return customer
    else:
        print(f"⚠️  Response: {response.status_code}")
        print(f"   {response.text}")
        return None

def main():
    print("="*70)
    print("👤 CUSTOMER USER CREATION")
    print("="*70)
    
    token, tenant_id = login_as_owner()
    if not token:
        return
    
    customer = create_customer(token)
    
    if customer:
        print("\n" + "="*70)
        print("✅ Customer account ready!")
        print("="*70)
        print("\nUse these credentials for testing:")
        print("   Email: customer@test.com")
        print("   Password: TestPassword123")
        print("="*70)
    else:
        print("\n⚠️  Use owner account for testing instead:")
        print(f"   Email: {OWNER_EMAIL}")
        print(f"   Password: {OWNER_PASSWORD}")

if __name__ == "__main__":
    main()
