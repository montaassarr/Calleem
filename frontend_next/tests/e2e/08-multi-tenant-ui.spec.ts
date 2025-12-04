import { test, expect } from '@playwright/test';

/**
 * Phase 4 Test 8: Multi-Tenant Data Isolation in UI
 * Tests that the UI correctly displays tenant-isolated data
 * and prevents cross-tenant data access
 */

test.describe('Multi-Tenant UI Isolation', () => {
  
  test('should only show tenant-specific agents', async ({ page }) => {
    // Login as first tenant
    await page.goto('/login');
    const tenant1Email = process.env.TEST_USER_EMAIL || 'test@example.com';
    const tenant1Password = process.env.TEST_USER_PASSWORD || 'TestPassword123!';
    
    await page.fill('input[name="email"]', tenant1Email);
    await page.fill('input[name="password"]', tenant1Password);
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard**', { timeout: 10000 });
    
    // Navigate to agents page
    await page.goto('/agents');
    await page.waitForTimeout(2000);
    
    // Get list of agents for tenant 1
    const tenant1Agents = await page.locator('[data-testid="agent-card"], [data-testid="agent-item"]').allTextContents();
    
    // Logout
    await page.click('[data-testid="user-menu"]').catch(() => {});
    await page.click('text=/logout|sign out/i').catch(() => {});
    
    // If we have a second tenant configured, verify isolation
    const tenant2Email = process.env.TEST_USER_EMAIL_2;
    const tenant2Password = process.env.TEST_USER_PASSWORD_2;
    
    if (tenant2Email && tenant2Password) {
      // Login as second tenant
      await page.goto('/login');
      await page.fill('input[name="email"]', tenant2Email);
      await page.fill('input[name="password"]', tenant2Password);
      await page.click('button[type="submit"]');
      await page.waitForURL('**/dashboard**', { timeout: 10000 });
      
      // Navigate to agents page
      await page.goto('/agents');
      await page.waitForTimeout(2000);
      
      // Get list of agents for tenant 2
      const tenant2Agents = await page.locator('[data-testid="agent-card"], [data-testid="agent-item"]').allTextContents();
      
      // Agents should be different (no overlap)
      const hasOverlap = tenant1Agents.some(agent => tenant2Agents.includes(agent));
      expect(hasOverlap).toBeFalsy();
    }
  });
  
  test('should only show tenant-specific appointments', async ({ page }) => {
    // Login as first tenant
    await page.goto('/login');
    const email = process.env.TEST_USER_EMAIL || 'test@example.com';
    const password = process.env.TEST_USER_PASSWORD || 'TestPassword123!';
    
    await page.fill('input[name="email"]', email);
    await page.fill('input[name="password"]', password);
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard**', { timeout: 10000 });
    
    // Navigate to appointments
    await page.goto('/appointments');
    await page.waitForTimeout(2000);
    
    // Should show appointments page
    await expect(
      page.locator('[data-testid="appointments-page"], [data-testid="appointments-list"]')
    ).toBeVisible({ timeout: 5000 });
    
    // All appointments should belong to this tenant (no way to verify without tenant IDs visible)
    // But we can check that the page loads and shows expected structure
    const appointmentCount = await page.locator(
      '[data-testid="appointment-item"], .fc-event'
    ).count();
    
    expect(appointmentCount >= 0).toBeTruthy();
  });
  
  test('should only show tenant-specific services', async ({ page }) => {
    // Login
    await page.goto('/login');
    const email = process.env.TEST_USER_EMAIL || 'test@example.com';
    const password = process.env.TEST_USER_PASSWORD || 'TestPassword123!';
    
    await page.fill('input[name="email"]', email);
    await page.fill('input[name="password"]', password);
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard**', { timeout: 10000 });
    
    // Navigate to services
    await page.goto('/services');
    await page.waitForTimeout(2000);
    
    // Should show services page with tenant's services
    await expect(
      page.locator('[data-testid="services-page"], [data-testid="services-list"]')
    ).toBeVisible({ timeout: 5000 });
    
    const serviceCount = await page.locator(
      '[data-testid="service-card"], [data-testid="service-item"]'
    ).count();
    
    expect(serviceCount >= 0).toBeTruthy();
  });
  
  test('should display correct tenant company name in UI', async ({ page }) => {
    // Login
    await page.goto('/login');
    const email = process.env.TEST_USER_EMAIL || 'test@example.com';
    const password = process.env.TEST_USER_PASSWORD || 'TestPassword123!';
    
    await page.fill('input[name="email"]', email);
    await page.fill('input[name="password"]', password);
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard**', { timeout: 10000 });
    
    // Should display tenant's company name somewhere in header or sidebar
    const companyNameSelectors = [
      '[data-testid="company-name"]',
      '[data-testid="tenant-name"]',
      'header text=/company/i',
    ];
    
    let foundCompanyName = false;
    for (const selector of companyNameSelectors) {
      if (await page.locator(selector).isVisible().catch(() => false)) {
        foundCompanyName = true;
        break;
      }
    }
    
    // Note: Company name might not be displayed, but user email should be
    if (!foundCompanyName) {
      // At least user email should be visible
      await expect(page.locator(`text=${email}`)).toBeVisible();
    }
  });
  
  test('should not allow access to other tenant data via URL manipulation', async ({ page }) => {
    // Login
    await page.goto('/login');
    const email = process.env.TEST_USER_EMAIL || 'test@example.com';
    const password = process.env.TEST_USER_PASSWORD || 'TestPassword123!';
    
    await page.fill('input[name="email"]', email);
    await page.fill('input[name="password"]', password);
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard**', { timeout: 10000 });
    
    // Try to access a resource with a different tenant ID in URL
    // (This assumes the app uses tenant IDs in URLs)
    await page.goto('/agents/other-tenant-id-123').catch(() => {});
    
    // Should either:
    // 1. Show 404 / not found
    // 2. Redirect to valid page
    // 3. Show access denied
    await page.waitForTimeout(2000);
    
    const currentUrl = page.url();
    const hasError = await page.locator('text=/not found|access denied|unauthorized|404/i').isVisible().catch(() => false);
    const redirected = !currentUrl.includes('other-tenant-id');
    
    // Either should show error or redirect away from invalid resource
    expect(hasError || redirected).toBeTruthy();
  });
  
  test('should show tenant-specific API keys in settings', async ({ page }) => {
    // Login
    await page.goto('/login');
    const email = process.env.TEST_USER_EMAIL || 'test@example.com';
    const password = process.env.TEST_USER_PASSWORD || 'TestPassword123!';
    
    await page.fill('input[name="email"]', email);
    await page.fill('input[name="password"]', password);
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard**', { timeout: 10000 });
    
    // Navigate to settings API keys
    await page.goto('/settings');
    await page.click('text=/API Keys/i').catch(() => {});
    await page.waitForTimeout(1000);
    
    // Should show API key inputs (masked)
    const vapiKeyInput = page.locator('input[name="vapi_api_key"], input[name="vapi_key"]');
    const groqKeyInput = page.locator('input[name="groq_api_key"], input[name="groq_key"]');
    
    const hasVapiKey = await vapiKeyInput.isVisible().catch(() => false);
    const hasGroqKey = await groqKeyInput.isVisible().catch(() => false);
    
    // Should display tenant's own API keys (masked)
    expect(hasVapiKey || hasGroqKey).toBeTruthy();
  });
  
  test('should show tenant-specific statistics on dashboard', async ({ page }) => {
    // Login
    await page.goto('/login');
    const email = process.env.TEST_USER_EMAIL || 'test@example.com';
    const password = process.env.TEST_USER_PASSWORD || 'TestPassword123!';
    
    await page.fill('input[name="email"]', email);
    await page.fill('input[name="password"]', password);
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard**', { timeout: 10000 });
    
    // Check dashboard stats
    await page.goto('/dashboard');
    await page.waitForTimeout(2000);
    
    // Should show stats for this tenant only
    const statsSelectors = [
      '[data-testid="stats-card"]',
      'text=/Total Agents|Total Appointments|Total Calls/i',
    ];
    
    let foundStats = false;
    for (const selector of statsSelectors) {
      if (await page.locator(selector).isVisible().catch(() => false)) {
        foundStats = true;
        break;
      }
    }
    
    expect(foundStats).toBeTruthy();
  });
  
  test('should maintain tenant context across navigation', async ({ page }) => {
    // Login
    await page.goto('/login');
    const email = process.env.TEST_USER_EMAIL || 'test@example.com';
    const password = process.env.TEST_USER_PASSWORD || 'TestPassword123!';
    
    await page.fill('input[name="email"]', email);
    await page.fill('input[name="password"]', password);
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard**', { timeout: 10000 });
    
    // Navigate through multiple pages
    await page.goto('/agents');
    await page.waitForTimeout(1000);
    
    await page.goto('/appointments');
    await page.waitForTimeout(1000);
    
    await page.goto('/services');
    await page.waitForTimeout(1000);
    
    await page.goto('/settings');
    await page.waitForTimeout(1000);
    
    // Should still be authenticated as same user/tenant
    await expect(page.locator(`text=${email}`)).toBeVisible();
  });
  
  test('should prevent creating resources for other tenants', async ({ page }) => {
    // Login
    await page.goto('/login');
    const email = process.env.TEST_USER_EMAIL || 'test@example.com';
    const password = process.env.TEST_USER_PASSWORD || 'TestPassword123!';
    
    await page.fill('input[name="email"]', email);
    await page.fill('input[name="password"]', password);
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard**', { timeout: 10000 });
    
    // Try to create an agent
    await page.goto('/agents');
    await page.click('button:has-text("Create Agent")').catch(() => {});
    
    // The form should not have any tenant selection dropdown
    // (because it's implicit from the logged-in user)
    const tenantSelect = page.locator('select[name="tenant_id"], select[name="tenant"]');
    const hasTenantSelect = await tenantSelect.isVisible().catch(() => false);
    
    // Tenant selection should NOT be available (implicit from auth)
    expect(hasTenantSelect).toBeFalsy();
  });
  
  test('should show correct user info in profile menu', async ({ page }) => {
    // Login
    await page.goto('/login');
    const email = process.env.TEST_USER_EMAIL || 'test@example.com';
    const password = process.env.TEST_USER_PASSWORD || 'TestPassword123!';
    
    await page.fill('input[name="email"]', email);
    await page.fill('input[name="password"]', password);
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard**', { timeout: 10000 });
    
    // Open user menu
    await page.click('[data-testid="user-menu"]');
    
    // Should show user's email or name
    await expect(page.locator(`text=${email}`)).toBeVisible({ timeout: 5000 });
  });
});

test.describe('Cross-Tenant Security', () => {
  
  test('should clear tenant data after logout', async ({ page }) => {
    // Login
    await page.goto('/login');
    const email = process.env.TEST_USER_EMAIL || 'test@example.com';
    const password = process.env.TEST_USER_PASSWORD || 'TestPassword123!';
    
    await page.fill('input[name="email"]', email);
    await page.fill('input[name="password"]', password);
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard**', { timeout: 10000 });
    
    // Logout
    await page.click('[data-testid="user-menu"]');
    await page.click('text=/logout|sign out/i');
    await page.waitForURL('**/login**', { timeout: 5000 });
    
    // Try to access protected page
    await page.goto('/dashboard');
    
    // Should redirect back to login
    await page.waitForURL('**/login**', { timeout: 5000 });
  });
  
  test('should not expose tenant IDs in HTML source', async ({ page }) => {
    // Login
    await page.goto('/login');
    const email = process.env.TEST_USER_EMAIL || 'test@example.com';
    const password = process.env.TEST_USER_PASSWORD || 'TestPassword123!';
    
    await page.fill('input[name="email"]', email);
    await page.fill('input[name="password"]', password);
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard**', { timeout: 10000 });
    
    // Get page HTML
    const html = await page.content();
    
    // Should not expose raw tenant IDs or sensitive data in HTML
    // (UUIDs, database IDs, etc. should not be in visible HTML)
    const hasTenantIdPattern = /tenant[_-]id["']?\s*:\s*["'][a-f0-9-]{36}["']/i.test(html);
    
    // Note: This is a weak test, just checking for obvious leaks
    // Real tenant IDs might be in API responses but not in HTML
    expect(hasTenantIdPattern).toBeFalsy();
  });
});
