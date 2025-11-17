#!/usr/bin/env python3
"""
Installation Verification Script
Checks that all required dependencies and modules are properly installed
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def verify_dependencies():
    """Verify all key AI dependencies are installed"""
    print("🔍 Checking AI Framework Dependencies...\n")
    
    dependencies = {
        "groq": "Groq AI client",
        "langchain": "LangChain framework",
        "crewai": "CrewAI multi-agent",
        "litellm": "LiteLLM abstraction",
        "instructor": "Instructor structured outputs",
        "openai": "OpenAI client",
        "pydantic": "Pydantic validation",
        "fastapi": "FastAPI framework",
        "motor": "MongoDB async driver",
    }
    
    results = []
    for package, description in dependencies.items():
        try:
            module = __import__(package)
            version = getattr(module, "__version__", "N/A")
            results.append((package, version, description, True))
            print(f"✅ {package:20} {version:15} - {description}")
        except ImportError as e:
            results.append((package, "Missing", description, False))
            print(f"❌ {package:20} {'Missing':15} - {description}")
    
    return all(r[3] for r in results)

def verify_brain_modules():
    """Verify AI Brain modules can be imported"""
    print("\n🧠 Checking AI Brain Modules...\n")
    
    modules = {
        "ai.brain.prompt_builder": "Dynamic Prompt Builder",
        "ai.brain.memory_engine": "Conversation Memory Engine",
        "ai.brain.appointment_reasoning": "Appointment Reasoning System",
        "ai.brain.intent_classifier": "Intent Classification Engine",
    }
    
    results = []
    for module_path, description in modules.items():
        try:
            __import__(module_path)
            results.append((module_path, description, True))
            print(f"✅ {module_path:40} - {description}")
        except ImportError as e:
            results.append((module_path, description, False))
            print(f"❌ {module_path:40} - {description}")
            print(f"   Error: {e}")
    
    return all(r[2] for r in results)

def verify_models():
    """Verify data models can be imported"""
    print("\n📦 Checking Data Models...\n")
    
    models = {
        "models.business_config": "Business Configuration Model",
        "models.appointment": "Appointment Model",
        "models.conversation": "Conversation Model",
        "models.service": "Service Model",
        "models.user": "User Model",
    }
    
    results = []
    for model_path, description in models.items():
        try:
            __import__(model_path)
            results.append((model_path, description, True))
            print(f"✅ {model_path:30} - {description}")
        except ImportError as e:
            results.append((model_path, description, False))
            print(f"❌ {model_path:30} - {description}")
            print(f"   Error: {e}")
    
    return all(r[2] for r in results)

def verify_services():
    """Verify services can be imported"""
    print("\n⚙️  Checking Services...\n")
    
    services = {
        "services.config_loader": "Dynamic Configuration Loader",
        "services.whatsapp_cloud": "WhatsApp Cloud Service",
    }
    
    results = []
    for service_path, description in services.items():
        try:
            __import__(service_path)
            results.append((service_path, description, True))
            print(f"✅ {service_path:30} - {description}")
        except ImportError as e:
            results.append((service_path, description, False))
            print(f"❌ {service_path:30} - {description}")
            print(f"   Error: {e}")
    
    return all(r[2] for r in results)

def verify_fastapi_app():
    """Verify FastAPI application loads"""
    print("\n🚀 Checking FastAPI Application...\n")
    
    try:
        from main import app
        print(f"✅ FastAPI app loaded successfully")
        print(f"   Routes: {len(app.routes)} routes registered")
        return True
    except Exception as e:
        print(f"❌ FastAPI app failed to load")
        print(f"   Error: {e}")
        return False

def main():
    """Run all verification checks"""
    print("=" * 80)
    print("AI RECEPTIONIST - INSTALLATION VERIFICATION")
    print("=" * 80)
    print()
    
    checks = [
        ("Dependencies", verify_dependencies),
        ("Brain Modules", verify_brain_modules),
        ("Data Models", verify_models),
        ("Services", verify_services),
        ("FastAPI App", verify_fastapi_app),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} verification failed with error: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    print()
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10} - {name}")
    
    all_passed = all(r[1] for r in results)
    
    print("\n" + "=" * 80)
    if all_passed:
        print("🎉 ALL CHECKS PASSED! Installation is complete and working.")
        print("\nNext steps:")
        print("1. Configure MongoDB connection in backend/.env")
        print("2. Set up WhatsApp Business API credentials")
        print("3. Run: cd backend && uvicorn main:app --reload")
        print("4. Access API docs at: http://localhost:8000/docs")
    else:
        print("⚠️  SOME CHECKS FAILED. Please review the errors above.")
        return 1
    
    print("=" * 80)
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
