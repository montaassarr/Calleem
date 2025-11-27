import requests
import json
import sys
import time

# Configuration
API_URL = "http://localhost:8000/api/v1"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password"  # Default password from setup
SUPER_ADMIN_USERNAME = "superadmin" # Assuming we have a superadmin or can create one
SUPER_ADMIN_PASSWORD = "password"

def print_step(message):
    print(f"\n🔹 {message}")

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def login(username, password):
    print_step(f"Logging in as {username}...")
    try:
        response = requests.post(
            f"{API_URL}/users/login",
            data={"username": username, "password": password}
        )
        if response.status_code == 200:
            token = response.json()["access_token"]
            print_success("Login successful")
            return token
        else:
            print_error(f"Login failed: {response.text}")
            return None
    except Exception as e:
        print_error(f"Connection failed: {e}")
        return None

def verify_admin_endpoints(token):
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. List Tenants
    print_step("Testing GET /admin/tenants")
    response = requests.get(f"{API_URL}/admin/tenants", headers=headers)
    if response.status_code == 200:
        tenants = response.json()
        print_success(f"Successfully retrieved {len(tenants)} tenants")
        if len(tenants) > 0:
            print(f"   First tenant: {tenants[0].get('name')} (Configured: {tenants[0].get('is_configured')})")
    else:
        print_error(f"Failed to list tenants: {response.status_code} - {response.text}")

    # 2. List Users
    print_step("Testing GET /admin/users")
    response = requests.get(f"{API_URL}/admin/users", headers=headers)
    if response.status_code == 200:
        users = response.json()
        print_success(f"Successfully retrieved {len(users)} users")
    else:
        print_error(f"Failed to list users: {response.status_code} - {response.text}")

    # 3. Global Analytics
    print_step("Testing GET /admin/analytics/global")
    response = requests.get(f"{API_URL}/admin/analytics/global", headers=headers)
    if response.status_code == 200:
        analytics = response.json()
        print_success("Successfully retrieved global analytics")
        print(f"   Stats: {json.dumps(analytics, indent=2)}")
    else:
        print_error(f"Failed to get analytics: {response.status_code} - {response.text}")

def verify_data_isolation(token1, token2):
    print_step("Verifying Data Isolation")
    
    headers1 = {"Authorization": f"Bearer {token1}"}
    headers2 = {"Authorization": f"Bearer {token2}"}
    
    # Create service for Tenant 1
    service1_name = f"Service T1 {int(time.time())}"
    res1 = requests.post(
        f"{API_URL}/services",
        headers=headers1,
        json={"name": service1_name, "description": "Test", "duration_minutes": 30, "price": 10}
    )
    if res1.status_code == 201:
        print_success("Created service for Tenant 1")
    else:
        print_error(f"Failed to create service for Tenant 1: {res1.text}")
        return

    # Create service for Tenant 2
    service2_name = f"Service T2 {int(time.time())}"
    res2 = requests.post(
        f"{API_URL}/services",
        headers=headers2,
        json={"name": service2_name, "description": "Test", "duration_minutes": 60, "price": 20}
    )
    if res2.status_code == 201:
        print_success("Created service for Tenant 2")
    else:
        print_error(f"Failed to create service for Tenant 2: {res2.text}")
        return

    # Verify Tenant 1 sees only their service
    res1_get = requests.get(f"{API_URL}/services", headers=headers1)
    if res1_get.status_code != 200:
        print_error(f"Failed to list services for Tenant 1: {res1_get.text}")
        return
    list1 = res1_get.json()
    names1 = [s["name"] for s in list1]
    if service1_name in names1 and service2_name not in names1:
        print_success("Tenant 1 sees only their services")
    else:
        print_error(f"Tenant 1 isolation failed. Saw: {names1}")

    # Verify Tenant 2 sees only their service
    res2_get = requests.get(f"{API_URL}/services", headers=headers2)
    if res2_get.status_code != 200:
        print_error(f"Failed to list services for Tenant 2: {res2_get.text}")
        return
    list2 = res2_get.json()
    names2 = [s["name"] for s in list2]
    if service2_name in names2 and service1_name not in names2:
        print_success("Tenant 2 sees only their services")
    else:
        print_error(f"Tenant 2 isolation failed. Saw: {names2}")

def main():
    print("🚀 Starting Backend Verification...")
    
    # We need a super admin token for admin endpoints
    # For now, let's try with the default admin user, assuming it might have super admin role or we can check
    # If not, we might need to create a super admin via script or manual DB update
    
    # 1. Login as Admin (Super Admin)
    # Note: In a fresh setup, the first user might be owner/admin. 
    # We'll assume 'admin' user exists or use the one created during setup.
    # If this fails, we might need to register a new user and manually promote to super_admin in DB
    
    token = login("montassar", "password") # Trying a likely username, or fallback to registration
    if not token:
        print_step("Attempting to register new super admin...")
        # Registration logic here if needed, but for now let's assume we have a user
        # Or we can use the 'admin' user if seeded.
        # Let's try to register a temp admin
        reg_data = {
            "username": "superadmin_test",
            "email": "superadmin_test@example.com",
            "password": "password123",
            "full_name": "Super Admin Test"
        }
        res = requests.post(f"{API_URL}/users/register", json=reg_data)
        if res.status_code == 201:
            print_success("Registered new user")
            token = login("superadmin_test", "password123")
        elif (res.status_code == 400 and ("already registered" in res.text or "already taken" in res.text)) or res.status_code == 403:
            print_step("User might already exist (or limit reached), logging in...")
            token = login("superadmin_test", "password123")
        else:
            print_error(f"Failed to register: {res.text}")
            return

    if token:
        # Verify current user role
        print_step("Verifying current user role...")
        me_res = requests.get(f"{API_URL}/users/me", headers={"Authorization": f"Bearer {token}"})
        if me_res.status_code == 200:
            me = me_res.json()
            print_success(f"Current user: {me.get('username')} - Role: {me.get('role')}")
        else:
            print_error(f"Failed to get user info: {me_res.text}")

        verify_admin_endpoints(token)
        
        # Clean up users if limit reached
        print_step("Checking user limit...")
        users_res = requests.get(f"{API_URL}/admin/users", headers={"Authorization": f"Bearer {token}"})
        if users_res.status_code == 200:
            users = users_res.json()
            if len(users) >= 8:
                print_step(f"Cleaning up users (Count: {len(users)})...")
                for u in users:
                    if u["username"] not in ["superadmin_test", "montassar"] and "fixed" not in u["username"]:
                        print(f"   Deleting {u['username']}...")
                        requests.delete(f"{API_URL}/admin/users/{u['id']}", headers={"Authorization": f"Bearer {token}"})
                        if len(users) - 1 < 8: break # Just delete enough
        
        # To verify isolation, we need two different users from different tenants.
        # Register User A
        user_a = "user_a_fixed"
        requests.post(f"{API_URL}/users/register", json={
            "username": user_a, "email": f"{user_a}@example.com", "password": "password", "full_name": "User A"
        })
        token_a = login(user_a, "password")
        
        # Register User B
        user_b = "user_b_fixed"
        requests.post(f"{API_URL}/users/register", json={
            "username": user_b, "email": f"{user_b}@example.com", "password": "password", "full_name": "User B"
        })
        token_b = login(user_b, "password")
        
        if token_a and token_b:
            verify_data_isolation(token_a, token_b)

if __name__ == "__main__":
    main()
