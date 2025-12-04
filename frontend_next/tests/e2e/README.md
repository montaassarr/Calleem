# Phase 4: Dashboard E2E Tests with Playwright

## Overview

This directory contains end-to-end tests for the AI Receptionist SaaS dashboard using Playwright. These tests validate complete user workflows through a real browser, testing both the frontend UI and backend API integration.

## Test Structure

### Test Files

1. **01-auth.spec.ts** - Authentication Flow (8 tests)
   - Login page display and validation
   - Successful login with valid credentials
   - Error handling for invalid credentials
   - Logout functionality
   - Session persistence after refresh
   - Navigation to registration and password reset

2. **02-dashboard-navigation.spec.ts** - Dashboard Navigation (12 tests)
   - Main dashboard layout and sections
   - Navigation menu functionality
   - Page navigation (Agents, Appointments, Services, Settings)
   - User menu and profile options
   - Dashboard stats and metrics
   - Active navigation highlighting
   - Responsive mobile menu
   - Recent activity display
   - Quick actions from dashboard

3. **03-onboarding.spec.ts** - Onboarding Wizard (8 tests)
   - Wizard display and progress tracking
   - Step 1: Company information
   - Step 2: API keys configuration
   - Step 3: Services setup
   - Step 4: Agent creation
   - Navigation between steps
   - Validation error handling
   - Progress saving and resuming

4. **04-agents.spec.ts** - Agent Management (10 tests)
   - Agents list page display
   - Create agent modal/form
   - Agent creation with validation
   - View agent details
   - Edit existing agent
   - Configure agent settings
   - Test agent functionality
   - Delete agent
   - Search and filter agents
   - Agent-specific operations

5. **05-appointments.spec.ts** - Appointment Management (11 tests)
   - Appointments calendar/list view
   - Toggle between views
   - Date navigation
   - View appointment details
   - Filter by status
   - Search appointments
   - Create manual appointment
   - Edit appointment
   - Cancel appointment
   - Available time slots display
   - Appointment statistics

6. **06-settings.spec.ts** - Settings and API Keys (14 tests)
   - Settings page with all sections
   - Profile information editing
   - API keys section navigation
   - Display existing keys (masked)
   - Update Vapi API key
   - Update Groq API key
   - API key format validation
   - Test API connectivity
   - Business hours configuration
   - Timezone settings
   - Password change form
   - Notification preferences
   - Calendar integration options
   - Webhook configuration

7. **07-services.spec.ts** - Services Management (12 tests)
   - Services page display
   - Display services in grid/list
   - Create service form
   - Service creation with validation
   - View service details
   - Edit existing service
   - Configure pricing
   - Configure duration
   - Toggle service status
   - Delete service
   - Search and filter services
   - Assign services to agents

8. **08-multi-tenant-ui.spec.ts** - Multi-Tenant UI Isolation (13 tests)
   - Tenant-specific agents display
   - Tenant-specific appointments
   - Tenant-specific services
   - Tenant company name display
   - URL manipulation protection
   - Tenant-specific API keys
   - Tenant-specific dashboard stats
   - Tenant context across navigation
   - Prevent cross-tenant resource creation
   - User info in profile menu
   - Clear data after logout
   - No tenant ID exposure in HTML

### Total: 88 E2E Tests

## Setup

### Prerequisites

1. **Node.js and npm** installed
2. **Backend API** running on `http://localhost:8000`
3. **Frontend** running on `http://localhost:3000`
4. **Test user** credentials configured in `.env.test`

### Installation

```bash
cd frontend_next
npm install -D @playwright/test
npx playwright install chromium
```

### Environment Configuration

Create a `.env.test` file in `frontend_next/`:

```env
# Frontend URL
FRONTEND_URL=http://localhost:3000

# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Test user credentials (must exist in database)
TEST_USER_EMAIL=test@example.com
TEST_USER_PASSWORD=TestPassword123!

# Optional: Second tenant for isolation tests
TEST_USER_EMAIL_2=tenant2@example.com
TEST_USER_PASSWORD_2=TestPassword123!

# Test tenant info
TEST_TENANT_ID=test_tenant_001
TEST_TENANT_NAME=Test Company

# API keys for testing
TEST_VAPI_KEY=test_vapi_key
TEST_GROQ_KEY=test_groq_key
```

### Create Test User

Before running tests, create a test user in the database:

```bash
cd backend
python create_admin.py \
  --email test@example.com \
  --password TestPassword123! \
  --company "Test Company"
```

## Running Tests

### Run All Tests

```bash
npm run test:e2e
```

### Run Specific Test File

```bash
npx playwright test tests/e2e/01-auth.spec.ts
```

### Run Tests in UI Mode (Interactive)

```bash
npm run test:e2e:ui
```

### Run Tests with Debug Mode

```bash
npx playwright test --debug
```

### Run Tests in Headed Mode (See Browser)

```bash
npx playwright test --headed
```

### Run Specific Test by Name

```bash
npx playwright test -g "should successfully login"
```

### Run Tests in Specific Browser

```bash
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit
```

## Test Fixtures

### Authentication Fixture

The `authenticatedPage` fixture automatically logs in before each test that needs authentication:

```typescript
test('should show dashboard', async ({ authenticatedPage: page }) => {
  await page.goto('/dashboard');
  // Already logged in!
});
```

### Utility Functions

Available in `fixtures.ts`:

- `waitForApiResponse(page, urlPattern)` - Wait for API call to complete
- `fillFormField(page, fieldName, value)` - Fill form input by name
- `clickAndWaitForNavigation(page, selector)` - Click and wait for page load
- `selectOption(page, fieldName, value)` - Select dropdown option
- `uploadFile(page, inputSelector, filePath)` - Upload file
- `waitForLoadingToFinish(page)` - Wait for loading spinners to disappear

## Test Reports

### HTML Report

After running tests, view the HTML report:

```bash
npx playwright show-report
```

The report includes:
- Test results summary
- Screenshots of failures
- Videos of failed test runs
- Trace files for debugging

### JSON Report

Results are also saved to `playwright-report/results.json` for CI/CD integration.

## Debugging Tests

### 1. Playwright Inspector

```bash
npx playwright test --debug
```

Opens the Playwright Inspector with step-by-step execution.

### 2. Trace Viewer

```bash
npx playwright show-trace trace.zip
```

View detailed trace of test execution with DOM snapshots, network calls, and console logs.

### 3. Screenshots on Failure

Screenshots are automatically captured on failure and saved to `test-results/`.

### 4. Console Logs

Add debugging logs in tests:

```typescript
console.log('Current URL:', page.url());
console.log('Element count:', await page.locator('.item').count());
```

## Best Practices

### 1. Use Test IDs

Prefer `data-testid` selectors for stability:

```typescript
await page.click('[data-testid="create-agent-button"]');
```

### 2. Wait for Elements

Always wait for elements before interacting:

```typescript
await expect(page.locator('#element')).toBeVisible();
await page.click('#element');
```

### 3. Handle Async Operations

Use `waitForResponse` for API calls:

```typescript
const response = await page.waitForResponse(
  response => response.url().includes('/api/agents') && response.status() === 200
);
```

### 4. Avoid Hard Timeouts

Use conditional waits instead of `waitForTimeout`:

```typescript
// Bad
await page.waitForTimeout(5000);

// Good
await page.waitForSelector('[data-testid="loaded"]');
```

### 5. Clean Up After Tests

Use test hooks for setup/teardown:

```typescript
test.afterEach(async ({ page }) => {
  // Clean up test data
});
```

## CI/CD Integration

### GitHub Actions Example

```yaml
- name: Run E2E Tests
  run: |
    npm run test:e2e
  env:
    TEST_USER_EMAIL: ${{ secrets.TEST_USER_EMAIL }}
    TEST_USER_PASSWORD: ${{ secrets.TEST_USER_PASSWORD }}
```

### Docker

Tests can run in Docker with headless browser:

```bash
docker run --rm -it \
  -v $(pwd):/work \
  -w /work/frontend_next \
  mcr.microsoft.com/playwright:v1.40.0-focal \
  npm run test:e2e
```

## Troubleshooting

### Tests Timeout

- Increase timeout in `playwright.config.ts`:
  ```typescript
  timeout: 60 * 1000, // 60 seconds
  ```

### Element Not Found

- Check if element is in viewport: `await page.locator('#element').scrollIntoViewIfNeeded();`
- Wait for element: `await page.waitForSelector('#element');`
- Check selector: Use Playwright Inspector to verify selectors

### Authentication Fails

- Verify test user exists in database
- Check `.env.test` has correct credentials
- Ensure backend API is running and accessible

### Flaky Tests

- Add explicit waits for dynamic content
- Use `page.waitForLoadState('networkidle')`
- Increase retries in config for CI environment

## Coverage

These E2E tests cover:

✅ Complete user authentication flow
✅ Dashboard navigation and UI
✅ Onboarding wizard (4 steps)
✅ Agent CRUD operations
✅ Appointment management
✅ Settings and API key configuration
✅ Services management
✅ Multi-tenant data isolation
✅ Responsive design (mobile/desktop)
✅ Form validation
✅ Error handling
✅ Session management

## Next Steps

After Phase 4 completion:

1. **Phase 5**: Load testing with k6
2. **Phase 6**: Production smoke tests
3. **Additional Tests**: 
   - Analytics dashboard
   - Billing and subscriptions
   - Advanced filters
   - Export functionality

## Support

For issues or questions:

1. Check Playwright documentation: https://playwright.dev
2. Review test output and screenshots in `test-results/`
3. Use trace viewer for detailed debugging
4. Check backend logs for API errors
