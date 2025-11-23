import requests
import json

BASE_URL = "http://localhost:8000/api/v1"
# User's number (assuming Tunisia +216 based on format)
USER_PHONE = "21692034689" 

def test_send_message():
    print("\n📤 Testing Outbound WhatsApp Message...")
    payload = {
        "to": USER_PHONE,
        "message": "Hello! This is a test message from your AI Receptionist debugger."
    }
    try:
        response = requests.post(f"{BASE_URL}/webhook/test-whatsapp", json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_simulate_webhook():
    print("\n📥 Testing Inbound Webhook Simulation...")
    # Simulate a message FROM the user TO the business
    payload = {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {
                        "display_phone_number": "15556441379",
                        "phone_number_id": "123456789"
                    },
                    "contacts": [{"profile": {"name": "Montassar"}, "wa_id": USER_PHONE}],
                    "messages": [{
                        "from": USER_PHONE,
                        "id": "wamid.test",
                        "timestamp": "1700000000",
                        "text": {"body": "Hello AI, are you working?"},
                        "type": "text"
                    }]
                },
                "field": "messages"
            }]
        }]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/webhook/sms", json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_send_message()
    test_simulate_webhook()
