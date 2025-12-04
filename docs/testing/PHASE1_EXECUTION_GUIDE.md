# 🧪 Phase 1 Test Execution Guide

**Phase**: Backend API & Tenant Isolation  
**Priority**: 🔴 CRITICAL  
**Duration**: 2-3 hours  
**Date**: December 2, 2025

---

## 📋 Prerequisites

### 1. Backend Running
```bash
cd backend
uvicorn main:app --reload
```

Backend should be accessible at: http://localhost:8000

### 2. MongoDB Running
```bash
# Using Docker
docker-compose up -d mongodb

# Or standalone MongoDB
mongod --dbpath /path/to/data
```

MongoDB should be running on: localhost:27017

### 3. Environment Variables
```bash
# Backend .env file
JWT_SECRET_KEY=REDACTED
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=ai_receptionist_test
MASTER_KEY=REDACTED
```

### 4. Test Dependencies
```bash
# Install test requirements
pip install -r tests/requirements.txt

# Key packages:
# - pytest
# - pytest-asyncio
# - httpx
# - PyJWT
```

---

## 🚀 Quick Start

### Run All Phase 1 Tests
```bash
./scripts/testing/run_phase1_tests.sh
```

This will:
1. ✅ Check backend is running
2. ✅ Check MongoDB is running
3. ✅ Clean test database
4. ✅ Run all Phase 1 tests in order
5. ✅ Generate coverage report

---

## 📝 Test Execution Steps

### Step 1: Verify Environment
```bash
# Check backend
curl http://localhost:8000/docs

# Check MongoDB
mongosh mongodb://localhost:27017 --eval "db.version()"

# Check test dependencies
pytest --version
```

### Step 2: Clean Test Database
```bash
# Drop test database
mongosh mongodb://localhost:27017/ai_receptionist_test --eval "db.dropDatabase()"
```

### Step 3: Run Tests One by One

#### 3.1 Authentication Tests
```bash
pytest tests/integration/test_auth.py -v -s
```

**Expected Results**:
- ✅ User registration creates JWT with tenant_id
- ✅ User login returns valid token
- ✅ Different users get different tokens with different tenant_ids
- ✅ Protected routes reject requests without token
- ✅ Protected routes reject invalid tokens
- ✅ Protected routes accept valid tokens
- ✅ Expired tokens are rejected

**Key Verification**: JWT tokens contain `tenant_id` field

#### 3.2 Tenant Isolation Tests ⭐ CRITICAL
```bash
pytest tests/integration/test_tenant_isolation.py -v -s
```

**Expected Results**:
- ✅ Tenant A adds API key → Only Tenant A sees it
- ✅ Tenant B adds API key → Only Tenant B sees it
- ✅ Tenant B cannot access Tenant A's API key (403/404)
- ✅ Tenant B cannot delete Tenant A's API key (403/404)
- ✅ Agents isolated per tenant
- ✅ Appointments isolated per tenant
- ✅ Conversations isolated per tenant

**Critical**: If ANY tenant isolation test fails, this is a **SECURITY BREACH** and must be fixed immediately.

#### 3.3 API Key Management Tests
```bash
pytest tests/integration/test_api_keys.py -v -s
```

**Expected Results**:
- ✅ Create REQUIRED provider key (Vapi)
- ✅ Create OPTIONAL provider key (OpenAI)
- ✅ Create multiple keys for same provider
- ✅ Retrieve all API keys
- ✅ Retrieve specific API key
- ✅ Delete API key
- ✅ API keys encrypted (not exposed in responses)

**Key Verification**: API keys are never exposed in plain text in API responses

#### 3.4 AI Proxy Service Tests
```bash
pytest tests/integration/test_ai_proxy.py -v -s
```

**Expected Results**:
- ✅ REQUIRED provider with user key → Uses user key
- ✅ REQUIRED provider without user key → Returns 428 (no fallback)
- ✅ OPTIONAL provider with user key → Uses user key
- ✅ OPTIONAL provider without user key → Falls back to platform key
- ✅ PLATFORM provider → Always uses platform key
- ✅ Multiple voice providers supported

**Key Verification**: 3-tier strategy enforced correctly

#### 3.5 Onboarding Wizard Tests
```bash
pytest tests/integration/test_onboarding.py -v -s
```

**Expected Results**:
- ✅ New user has incomplete onboarding status
- ✅ Voice provider options retrieved
- ✅ Setup Vapi key → Success
- ✅ Setup invalid Vapi key → Rejected (400/422)
- ✅ Cannot skip onboarding without voice key (428)
- ✅ Configure agent after key setup → Success (or 400 with test key)
- ✅ Onboarding status updates correctly

**Key Verification**: Users cannot create agents without voice provider key

---

## 📊 Test Results Tracking

### Test Execution Checklist

#### Phase 1.1: Authentication ✅
- [ ] test_user_registration
- [ ] test_user_login
- [ ] test_multiple_users_different_tokens
- [ ] test_protected_route_without_token
- [ ] test_protected_route_with_invalid_token
- [ ] test_protected_route_with_valid_token
- [ ] test_token_expiration
- [ ] test_user_cannot_access_admin_routes

**Status**: ___________  
**Notes**: ___________

#### Phase 1.2: Tenant Isolation ⭐ CRITICAL
- [ ] test_api_key_isolation
- [ ] test_cross_tenant_api_key_access_blocked
- [ ] test_cross_tenant_api_key_delete_blocked
- [ ] test_agent_isolation
- [ ] test_appointment_isolation
- [ ] test_conversation_isolation

**Status**: ___________  
**Critical Issues**: ___________

#### Phase 1.3: API Key Management ✅
- [ ] test_create_required_provider_key
- [ ] test_create_optional_provider_key
- [ ] test_create_multiple_keys_same_provider
- [ ] test_retrieve_all_api_keys
- [ ] test_retrieve_specific_api_key
- [ ] test_retrieve_nonexistent_key
- [ ] test_delete_api_key
- [ ] test_delete_nonexistent_key
- [ ] test_api_key_encryption

**Status**: ___________  
**Notes**: ___________

#### Phase 1.4: AI Proxy Service ✅
- [ ] test_required_provider_with_user_key
- [ ] test_required_provider_without_user_key
- [ ] test_optional_provider_with_user_key
- [ ] test_optional_provider_without_user_key
- [ ] test_platform_provider_always_platform_key
- [ ] test_multiple_voice_providers
- [ ] test_provider_type_validation
- [ ] test_onboarding_checks_voice_provider
- [ ] test_agent_creation_uses_livekit_defaults

**Status**: ___________  
**Notes**: ___________

#### Phase 1.5: Onboarding Wizard ✅
- [ ] test_new_user_onboarding_incomplete
- [ ] test_get_voice_provider_options
- [ ] test_enable_livekit_voice_agent
- [ ] test_livekit_preview_session_errors
- [ ] test_setup_retell_key_success
- [ ] test_cannot_skip_onboarding_without_voice_key
- [ ] test_configure_agent_after_key_setup
- [ ] test_onboarding_complete_user
- [ ] test_update_voice_key_after_onboarding
- [ ] test_onboarding_without_authentication
- [ ] test_setup_voice_key_missing_fields
- [ ] test_setup_unsupported_voice_provider

**Status**: ___________  
**Notes**: ___________

---

## 🐛 Troubleshooting

### Backend Not Running
```bash
# Check if process is running
ps aux | grep uvicorn

# Restart backend
cd backend
uvicorn main:app --reload
```

### MongoDB Not Running
```bash
# Check MongoDB status
docker ps | grep mongo

# Start MongoDB
docker-compose up -d mongodb
```

### Test Failures

#### JWT Decode Error
**Issue**: `jwt.exceptions.InvalidSignatureError`  
**Fix**: Set `JWT_SECRET_KEY` environment variable

#### Database Connection Error
**Issue**: `pymongo.errors.ServerSelectionTimeoutError`  
**Fix**: Ensure MongoDB is running and accessible

#### 428 Errors in Tests
**Issue**: Tests return 428 Precondition Required  
**Fix**: This is expected for REQUIRED providers without keys. Check test logic.

#### Tenant Isolation Failures ⚠️
**Issue**: Cross-tenant data access detected  
**Fix**: **CRITICAL SECURITY ISSUE** - Review tenant filtering in database queries

---

## 📈 Success Criteria

### Phase 1 Complete When:
- [ ] All authentication tests pass
- [ ] **All tenant isolation tests pass** ⭐ CRITICAL
- [ ] All API key management tests pass
- [ ] All AI proxy tests pass
- [ ] All onboarding tests pass
- [ ] Coverage report shows >80% backend coverage
- [ ] No data leakage between tenants
- [ ] No security vulnerabilities detected

---

## 🎯 Expected Results

### Test Summary
```
Phase 1.1: Authentication & Authorization
  ✅ 8 tests passed

Phase 1.2: Tenant Isolation (CRITICAL)
  ✅ 6 tests passed
  
Phase 1.3: API Key Management
  ✅ 9 tests passed
  
Phase 1.4: AI Proxy Service
  ✅ 9 tests passed
  
Phase 1.5: Onboarding Wizard
  ✅ 12 tests passed

Total: 44 tests passed
Coverage: >80%
```

### Coverage Report
```
Name                              Stmts   Miss  Cover
-----------------------------------------------------
backend/services/ai_proxy.py        150     15    90%
backend/routers/api_keys.py         120     12    90%
backend/routers/onboarding.py       100     10    90%
backend/routers/users.py             80      8    90%
-----------------------------------------------------
TOTAL                              450     45    90%
```

---

## 🔒 Security Validations

### Critical Security Checks
- [ ] JWT tokens contain tenant_id
- [ ] All database queries filter by tenant_id
- [ ] API keys encrypted at rest
- [ ] API keys never exposed in plain text
- [ ] Cross-tenant access blocked (403/404)
- [ ] Cross-tenant delete blocked (403/404)
- [ ] Expired tokens rejected
- [ ] Invalid tokens rejected
- [ ] Protected routes require authentication

**Sign-off**: ___________  
**Date**: ___________

---

## 📝 Test Report Template

```markdown
# Phase 1 Test Execution Report

**Date**: December 2, 2025
**Tester**: [Your Name]
**Environment**: Local Development

## Results Summary
- Total Tests: 44
- Passed: __
- Failed: __
- Skipped: __
- Duration: __ minutes

## Phase Breakdown

### Phase 1.1: Authentication
- Status: ✅ PASS / ❌ FAIL
- Tests: 8/8 passed
- Issues: None

### Phase 1.2: Tenant Isolation ⭐
- Status: ✅ PASS / ❌ FAIL
- Tests: 6/6 passed
- Critical Issues: None / [Describe]

### Phase 1.3: API Key Management
- Status: ✅ PASS / ❌ FAIL
- Tests: 9/9 passed
- Issues: None

### Phase 1.4: AI Proxy Service
- Status: ✅ PASS / ❌ FAIL
- Tests: 9/9 passed
- Issues: None

### Phase 1.5: Onboarding Wizard
- Status: ✅ PASS / ❌ FAIL
- Tests: 12/12 passed
- Issues: None

## Issues Found
1. [Issue Title]
   - Severity: Critical/High/Medium/Low
   - Test: [test_name]
   - Description: [details]
   - Fix: [action taken]

## Security Validation
- [ ] Tenant isolation verified
- [ ] API keys encrypted
- [ ] Cross-tenant access blocked
- [ ] No security vulnerabilities

## Coverage
- Overall: __%
- Critical Modules: __%

## Sign-off
- Tester: ___________
- Date: ___________
- Ready for Phase 2: YES / NO
```

---

## 🚀 Next Steps

After Phase 1 passes:
1. Document any issues found and fixed
2. Generate final coverage report
3. Create test data summary
4. Proceed to **Phase 2: Voice Provider Integration**

**Phase 2 File**: `docs/testing/PHASE2_VOICE_INTEGRATION.md`

---

**Ready to Start?**
```bash
./scripts/testing/run_phase1_tests.sh
```
