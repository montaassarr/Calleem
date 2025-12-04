# 🧪 Testing Documentation

Complete testing strategy and implementation for AI Receptionist Voice-First BYOK architecture.

---

## 📚 Documentation Index

### Strategy & Planning
- **[TESTING_STRATEGY.md](./TESTING_STRATEGY.md)** - Complete 4-phase testing strategy
  - Phase 1: Backend API & Tenant Isolation
  - Phase 2: Voice Provider Integration  
  - Phase 3: End-to-End Workflows
  - Phase 4: AWS Deployment Readiness

### Phase 1: Backend & Tenant Isolation (Current)
- **[PHASE1_QUICKSTART.md](./PHASE1_QUICKSTART.md)** - Quick start guide ⭐ START HERE
- **[PHASE1_EXECUTION_GUIDE.md](./PHASE1_EXECUTION_GUIDE.md)** - Detailed execution guide
- **[PHASE1_IMPLEMENTATION_SUMMARY.md](./PHASE1_IMPLEMENTATION_SUMMARY.md)** - What was built

### Future Phases (Coming Soon)
- **Phase 2**: Voice Provider Integration (Vapi/Retell)
- **Phase 3**: End-to-End Workflows (Complete user journeys)
- **Phase 4**: AWS Deployment Readiness (Performance, security, Docker)

---

## 🚀 Quick Start

### 1. Setup Test Environment
```bash
./scripts/testing/setup_test_env.sh
```

This will:
- Create virtual environment
- Install dependencies
- Configure MongoDB
- Setup test database
- Validate backend configuration

### 2. Start Backend
```bash
cd backend
uvicorn main:app --reload
```

### 3. Run Phase 1 Tests
```bash
./scripts/testing/run_phase1_tests.sh
```

---

## 📊 Test Coverage

### Phase 1: Backend API & Tenant Isolation (✅ Ready)

| Test Suite | File | Tests | Priority | Status |
|------------|------|-------|----------|--------|
| Authentication | `test_auth.py` | 8 | 🔴 Critical | ✅ Ready |
| **Tenant Isolation** | `test_tenant_isolation.py` | **6** | **🔴 CRITICAL** | ✅ Ready |
| API Keys | `test_api_keys.py` | 9 | 🟡 High | ✅ Ready |
| AI Proxy | `test_ai_proxy.py` | 9 | 🟡 High | ✅ Ready |
| Onboarding | `test_onboarding.py` | 12 | 🟡 High | ✅ Ready |
| **Total** | **5 files** | **44 tests** | **Phase 1** | ✅ **Ready** |

---

## 🎯 What's Being Tested?

### 1. Authentication & Authorization
- User registration with JWT tokens
- Login flow and token validation
- Protected routes enforcement
- Token expiration
- Role-based access control

**Critical Check**: JWT tokens contain `tenant_id`

### 2. Tenant Isolation ⭐ MOST IMPORTANT
- API key isolation between tenants
- Cross-tenant access prevention (403/404)
- Agent isolation per tenant
- Appointment isolation per tenant
- Conversation isolation per tenant

**Critical Check**: ZERO data leakage between tenants

### 3. API Key Management
- CRUD operations for API keys
- Encryption at rest
- Multiple providers support
- Key validation
- Secure key storage (never exposed)

**Critical Check**: API keys encrypted, never exposed

### 4. AI Proxy Service (3-Tier Strategy)
- **REQUIRED** providers (Vapi/Retell) - User MUST have key, no fallback, 428 if missing
- **OPTIONAL** providers (OpenAI/Groq) - Platform fallback available
- **PLATFORM** providers (Twilio/n8n) - Always use platform key

**Critical Check**: Voice providers enforce BYOK

### 5. Onboarding Wizard
- Mandatory voice provider setup
- Key validation during onboarding
- Status tracking
- Agent configuration flow
- Cannot skip without voice key (428)

**Critical Check**: Users cannot create agents without voice provider

---

## 🔒 Security Validations

### Critical Security Checks
- [ ] JWT tokens contain tenant_id
- [ ] All database queries filter by tenant_id
- [ ] API keys encrypted at rest
- [ ] API keys never exposed in plain text
- [ ] Cross-tenant access returns 403/404
- [ ] Cross-tenant delete returns 403/404
- [ ] Expired tokens rejected (401)
- [ ] Invalid tokens rejected (401)
- [ ] Protected routes require authentication

**If ANY security check fails, this is a CRITICAL ISSUE**

---

## 📁 Test Files Structure

```
tests/
├── requirements.txt                # Test dependencies
├── conftest.py                     # Pytest configuration
├── integration/                    # Phase 1 tests
│   ├── test_auth.py               # Authentication (8 tests)
│   ├── test_tenant_isolation.py   # Tenant isolation (6 tests) ⭐
│   ├── test_api_keys.py           # API keys (9 tests)
│   ├── test_ai_proxy.py           # AI proxy (9 tests)
│   └── test_onboarding.py         # Onboarding (12 tests)
├── e2e/                           # Phase 3 tests (coming soon)
└── unit/                          # Unit tests (optional)
```

---

## 🛠️ Test Scripts

### Setup & Execution
```bash
# Setup test environment (one-time)
./scripts/testing/setup_test_env.sh

# Run all Phase 1 tests
./scripts/testing/run_phase1_tests.sh

# Run specific test suite
pytest tests/integration/test_tenant_isolation.py -v -s

# Run with coverage
pytest tests/integration/ --cov=backend --cov-report=html
```

### Database Management
```bash
# Clean test database
mongosh mongodb://localhost:27017/ai_receptionist_test --eval "db.dropDatabase()"

# Create indexes
mongosh mongodb://localhost:27017/ai_receptionist_test --eval "
db.users.createIndex({ email: 1 }, { unique: true });
db.api_keys.createIndex({ tenant_id: 1, provider: 1 });
"
```

---

## 📊 Expected Results

### Successful Phase 1 Run
```
🧪 Phase 1: Backend API & Tenant Isolation Tests
================================================

✅ Backend is running
✅ MongoDB is running
✅ Test database cleaned

==========================================
Phase 1.1: Authentication & Authorization
==========================================
✅ 8 tests passed

==========================================
Phase 1.2: Tenant Isolation (CRITICAL) ⭐
==========================================
✅ 6 tests passed

==========================================
Phase 1.3: API Key Management
==========================================
✅ 9 tests passed

==========================================
Phase 1.4: AI Proxy Service
==========================================
✅ 9 tests passed

==========================================
Phase 1.5: Onboarding Wizard
==========================================
✅ 12 tests passed

==========================================
📊 Phase 1 Test Summary
==========================================
✅ All Phase 1 tests passed!

🎉 Phase 1 Complete - Backend API & Tenant Isolation Verified!
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

## 🐛 Common Issues

### Backend Not Running
```bash
# Check if backend is running
curl http://localhost:8000/docs

# Start backend
cd backend
uvicorn main:app --reload
```

### MongoDB Not Running
```bash
# Check if MongoDB is running
nc -z localhost 27017

# Start MongoDB via Docker
docker-compose up -d mongodb
```

### Missing Dependencies
```bash
# Install all dependencies
pip install -r tests/requirements.txt
```

### Environment Variables Not Set
```bash
# Check .env file
cat backend/.env

# Required variables:
# - JWT_SECRET_KEY
# - MONGODB_URL
# - MASTER_KEY
```

### Test Database Contaminated
```bash
# Clean test database
mongosh mongodb://localhost:27017/ai_receptionist_test --eval "db.dropDatabase()"
```

---

## 📝 Test Data

### Test Tenants
```json
{
  "tenant_a": {
    "email": "tenant_a@test.com",
    "password": "Test123!@#",
    "business_name": "Barber Shop A"
  },
  "tenant_b": {
    "email": "tenant_b@test.com",
    "password": "Test456!@#",
    "business_name": "Salon B"
  }
}
```

### Required API Keys
For complete testing, you'll need:
- 2 Vapi test accounts (for tenant isolation tests)
- 1 OpenAI test key (optional, for fallback tests)
- Platform keys configured in `backend/.env`

---

## ✅ Success Criteria

### Phase 1 Complete When:
- [ ] All 44 tests pass
- [ ] **Zero tenant isolation breaches** ⭐
- [ ] API keys encrypted and secure
- [ ] 3-tier AI proxy strategy enforced
- [ ] Onboarding wizard mandatory
- [ ] Coverage >80%
- [ ] No security vulnerabilities

---

## 🎓 Key Learnings

### Multi-Tenant SaaS Testing:
1. **Tenant isolation is CRITICAL** - Test extensively with multiple tenants
2. **JWT must contain tenant_id** - Essential for data filtering
3. **All DB queries must filter by tenant** - No exceptions
4. **Cross-tenant access must be blocked** - Always return 403/404
5. **Test with real multi-tenant scenarios** - Don't just test single tenant

### Voice-First BYOK Testing:
1. **REQUIRED = no fallback** - Must enforce with 428 status code
2. **OPTIONAL = graceful degradation** - Platform fallback available
3. **PLATFORM = always platform** - Ignore user keys
4. **Onboarding must be mandatory** - Block all features until complete
5. **Test key validation early** - Reject invalid keys before saving

---

## 📅 Testing Timeline

| Day | Phase | Duration | Focus |
|-----|-------|----------|-------|
| Day 1 | Phase 1 | 2-3 hours | Backend & tenant isolation |
| Day 2 | Phase 2 | 2-3 hours | Voice provider integration |
| Day 3 | Phase 3 | 3-4 hours | End-to-end workflows |
| Day 4 | Phase 4 | 2-3 hours | AWS deployment readiness |

---

## 🔜 Next Steps

### After Phase 1 Passes:
1. ✅ Review coverage report: `open htmlcov/index.html`
2. ✅ Document any issues or improvements
3. ✅ Verify all security checks passed
4. ✅ Proceed to Phase 2: Voice Provider Integration

### Phase 2 Will Test:
- Vapi agent creation with user keys
- Retell integration
- Tool schema injection
- Real voice call flows
- Voice provider key validation

---

## 📞 Support

### Documentation
- **Strategy**: [TESTING_STRATEGY.md](./TESTING_STRATEGY.md)
- **Quick Start**: [PHASE1_QUICKSTART.md](./PHASE1_QUICKSTART.md)
- **Detailed Guide**: [PHASE1_EXECUTION_GUIDE.md](./PHASE1_EXECUTION_GUIDE.md)

### Issues & Questions
- Check troubleshooting section in execution guide
- Review common issues above
- Verify environment setup is complete

---

## 📊 Test Metrics

### Coverage Goals
- **Backend Services**: >85%
- **Routers**: >90%
- **Models**: >80%
- **Overall**: >85%

### Quality Metrics
- **Security**: 100% of security checks pass
- **Tenant Isolation**: 100% pass rate (zero tolerance)
- **Performance**: API response time <500ms
- **Reliability**: Zero flaky tests

---

**Current Status**: ✅ Phase 1 Ready for Execution  
**Next Phase**: Phase 2 - Voice Provider Integration  
**Architecture**: Voice-First BYOK  
**Last Updated**: December 2, 2025
