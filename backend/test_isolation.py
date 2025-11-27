import requests
import sys

BASE_URL = "http://localhost:8000/api/v1"

def login(username, password):
    response = requests.post(f"{BASE_URL}/users/token", data={
        "username": username,
        "password": password
    })
    if response.status_code != 200:
        print(f"❌ Login failed for {username}: {response.text}")
        sys.exit(1)
    return response.json()["access_token"]

def test_isolation():
    print("🧪 Starting Isolation Test...")
    
    # 1. Login as Tenant 1
    token1 = login("tenant1", "password123")
    print("✅ Logged in as Tenant 1")
    
    # 2. Fetch Tenant 1 Services
    headers1 = {"Authorization": f"Bearer {token1}"}
    resp1 = requests.get(f"{BASE_URL}/services/", headers=headers1)
    services1 = resp1.json()
    print(f"✅ Tenant 1 has {len(services1)} services")
    
    if len(services1) == 0:
        print("❌ Tenant 1 should have services!")
        sys.exit(1)
        
    service1_id = services1[0]["id"]
    print(f"   Service ID: {service1_id}")

    # 3. Login as Tenant 2
    token2 = login("tenant2", "password123")
    print("✅ Logged in as Tenant 2")
    
    # 4. Fetch Tenant 2 Services
    headers2 = {"Authorization": f"Bearer {token2}"}
    resp2 = requests.get(f"{BASE_URL}/services/", headers=headers2)
    services2 = resp2.json()
    print(f"✅ Tenant 2 has {len(services2)} services")
    
    # 5. Verify IDs are different
    service2_ids = [s["id"] for s in services2]
    if service1_id in service2_ids:
        print("❌ DATA LEAK! Tenant 2 can see Tenant 1's service in list!")
        sys.exit(1)
    else:
        print("✅ Tenant 2 list does not contain Tenant 1's service")

    # 6. Try to access Tenant 1's service as Tenant 2
    print(f"🕵️  Attempting to access Tenant 1's service ({service1_id}) as Tenant 2...")
    resp_hack = requests.get(f"{BASE_URL}/services/{service1_id}", headers=headers2)
    
    if resp_hack.status_code == 404:
        print("✅ Access Denied (404 Not Found) - Isolation Working!")
    else:
        print(f"❌ SECURITY FAILURE! Status: {resp_hack.status_code}")
        print(resp_hack.json())
        sys.exit(1)

    print("\n🎉 ALL ISOLATION TESTS PASSED!")

if __name__ == "__main__":
    test_isolation()
