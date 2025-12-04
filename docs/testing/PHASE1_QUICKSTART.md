# 🧪 Phase 1 Test Execution - Quick Start

## 🚀 Run Phase 1 Tests

### Prerequisites Check
```bash
# 1. Backend running?
curl http://localhost:8000/docs

# 2. MongoDB running?
mongosh mongodb://localhost:27017 --eval "db.version()"

# 3. Environment configured?
cat backend/.env | grep "JWT_SECRET_KEY\|MONGODB_URL\|MASTER_KEY"
```

### Run All Tests
```bash
./scripts/testing/run_phase1_tests.sh
```

### Run Individual Test Suites
```bash
# Authentication tests
pytest tests/integration/test_auth.py -v -s

# Tenant isolation tests (CRITICAL)
pytest tests/integration/test_tenant_isolation.py -v -s

# API key tests
pytest tests/integration/test_api_keys.py -v -s

# AI proxy tests
pytest tests/integration/test_ai_proxy.py -v -s

# Onboarding tests
pytest tests/integration/test_onboarding.py -v -s
```

## 📊 Expected Output

```
🧪 Phase 1: Backend API & Tenant Isolation Tests
================================================

✅ Backend is running
✅ MongoDB is running
✅ Test database cleaned

==========================================
Phase 1.1: Authentication & Authorization
==========================================
test_auth.py::TestAuthentication::test_user_registration PASSED
test_auth.py::TestAuthentication::test_user_login PASSED
test_auth.py::TestAuthentication::test_multiple_users_different_tokens PASSED
test_auth.py::TestAuthentication::test_protected_route_without_token PASSED
test_auth.py::TestAuthentication::test_protected_route_with_invalid_token PASSED
test_auth.py::TestAuthentication::test_protected_route_with_valid_token PASSED
test_auth.py::TestAuthentication::test_token_expiration PASSED
test_auth.py::TestAuthorization::test_user_cannot_access_admin_routes PASSED
✅ Authentication tests passed

==========================================
Phase 1.2: Tenant Isolation (CRITICAL) ⭐
==========================================
test_tenant_isolation.py::TestTenantIsolation::test_api_key_isolation PASSED
test_tenant_isolation.py::TestTenantIsolation::test_cross_tenant_api_key_access_blocked PASSED
test_tenant_isolation.py::TestTenantIsolation::test_cross_tenant_api_key_delete_blocked PASSED
test_tenant_isolation.py::TestTenantIsolation::test_agent_isolation PASSED
test_tenant_isolation.py::TestTenantIsolation::test_appointment_isolation PASSED
test_tenant_isolation.py::TestTenantIsolation::test_conversation_isolation PASSED
✅✅✅ Tenant isolation tests passed (CRITICAL)

==========================================
Phase 1.3: API Key Management
==========================================
[9 tests passed]
✅ API key tests passed

==========================================
Phase 1.4: AI Proxy Service
==========================================
[9 tests passed]
✅ AI Proxy tests passed

==========================================
Phase 1.5: Onboarding Wizard
==========================================
[12 tests passed]
✅ Onboarding tests passed

==========================================
📊 Phase 1 Test Summary
==========================================
✅ All Phase 1 tests passed!

Tests completed:
  ✅ Authentication & Authorization
  ✅ Tenant Isolation (CRITICAL)
  ✅ API Key Management
  ✅ AI Proxy Service (3-tier strategy)
  ✅ Onboarding Wizard

🎉 Phase 1 Complete - Backend API & Tenant Isolation Verified!
```

## 🐛 Common Issues

### Backend Not Running
```bash
cd backend
uvicorn main:app --reload
```

### MongoDB Not Running
```bash
docker-compose up -d mongodb
```

### Missing Dependencies
```bash
pip install -r tests/requirements.txt
```

### Test Database Not Clean
```bash
mongosh mongodb://localhost:27017/ai_receptionist_test --eval "db.dropDatabase()"
```

## 📝 What's Being Tested?

1. **Authentication** (8 tests)
   - User registration with JWT tokens
   - Login flow
   - Token validation
   - Protected routes

2. **Tenant Isolation** (6 tests) ⭐ CRITICAL
   - API key isolation
   - Cross-tenant access prevention
   - Agent isolation
   - Appointment isolation
   - Conversation isolation

3. **API Key Management** (9 tests)
   - CRUD operations
   - Encryption
   - Multiple providers
   - Validation

4. **AI Proxy Service** (9 tests)
   - REQUIRED provider handling (Vapi)
   - OPTIONAL provider handling (OpenAI)
   - PLATFORM provider handling (Twilio)
   - Fallback logic

5. **Onboarding Wizard** (12 tests)
   - Voice provider setup
   - Key validation
   - Mandatory flow enforcement
   - Status tracking

## ✅ Success Criteria

- [ ] All 44 tests pass
- [ ] No tenant isolation breaches
- [ ] Coverage >80%
- [ ] No security issues

## 🎯 Next Steps

After Phase 1 passes:
1. Review coverage report: `open htmlcov/index.html`
2. Document any issues
3. Proceed to Phase 2: Voice Provider Integration

**Full Guide**: `docs/testing/PHASE1_EXECUTION_GUIDE.md`
