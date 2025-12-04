"""
Fixtures for E2E tests

This conftest overrides the mock API keys from tests/conftest.py with real keys from .env
"""

import pytest
import os
from pathlib import Path
from dotenv import load_dotenv


@pytest.fixture(scope="session", autouse=True)
def load_real_api_keys():
    """
    Load real API keys from .env for E2E tests.
    This MUST override the mock keys set in tests/conftest.py
    """
    env_path = Path(__file__).parent.parent.parent / ".env"
    
    # Force load and OVERRIDE any existing environment variables
    load_dotenv(env_path, override=True)
    
    # Verify critical keys are loaded (and not mocks)
    groq_key = os.getenv("GROQ_API_KEY")
    vapi_key = os.getenv("VAPI_PRIVATE_API_KEY")
    
    print("\n" + "="*60)
    print("🔑 E2E Test API Key Verification")
    print("="*60)
    
    if groq_key and not groq_key.startswith("gsk_test"):
        print(f"✅ GROQ_API_KEY loaded (real): {groq_key[:20]}... (len={len(groq_key)})")
    elif groq_key and groq_key.startswith("gsk_test"):
        print(f"⚠️  GROQ_API_KEY is mock: {groq_key}")
        print("❌ E2E tests require real API keys in .env file!")
        pytest.fail("Mock API key detected - E2E tests need real keys")
    else:
        print("❌ GROQ_API_KEY not found in environment")
        pytest.fail("GROQ_API_KEY missing from .env file")
    
    if vapi_key and not vapi_key.startswith("vapi_test"):
        print(f"✅ VAPI_PRIVATE_API_KEY loaded (real): {vapi_key[:20]}...")
    else:
        print(f"⚠️  VAPI_PRIVATE_API_KEY: {vapi_key[:20] if vapi_key else 'NOT FOUND'}...")
    
    print("="*60 + "\n")
