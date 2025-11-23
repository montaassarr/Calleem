import requests
import time
import sys

def check_url(url, name, retries=5):
    print(f"Checking {name} at {url}...")
    for i in range(retries):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name} is UP!")
                return True
            else:
                print(f"⚠️  {name} returned status {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"⏳ Waiting for {name}...")
        
        time.sleep(2)
    
    print(f"❌ {name} is DOWN after {retries} retries.")
    return False

def main():
    print("🔍 Verifying AI Receptionist System...")
    
    backend_ok = check_url("http://localhost:8000/health", "Backend API")
    frontend_ok = check_url("http://localhost:5173", "Frontend Dashboard")
    
    if backend_ok and frontend_ok:
        print("\n🎉 System is fully operational!")
        print("Backend: http://localhost:8000")
        print("Frontend: http://localhost:5173")
        sys.exit(0)
    else:
        print("\n❌ System verification failed. Check logs with 'docker compose logs'.")
        sys.exit(1)

if __name__ == "__main__":
    main()
