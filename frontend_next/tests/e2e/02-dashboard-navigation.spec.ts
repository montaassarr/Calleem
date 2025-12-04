import { test, expect } from './fixtures';

/**
 * Phase 4 Test 2: Dashboard Navigation and Layout
 * Tests main dashboard UI, navigation menu, and layout components
 */

test.describe('Dashboard Navigation', () => {
  
  test('should display dashboard with all main sections', async ({ authenticatedPage: page }) => {
    await page.goto('/dashboard');
    
    // Check main dashboard elements
    await expect(page.locator('[data-testid="dashboard-header"]')).toBeVisible();
    await expect(page.locator('[data-testid="sidebar"], nav')).toBeVisible();
    
    // Check navigation menu items
    const navItems = [
      /Dashboard|Home/i,
      /Agents/i,
      /Appointments/i,
      /Services/i,
      /Settings/i,
    ];
    
    for (const item of navItems) {
      await expect(page.locator(`nav >> text=${item}`)).toBeVisible();
    }
  });
  
  test('should navigate to Agents page', async ({ authenticatedPage: page }) => {
    await page.goto('/dashboard');
    
    // Click Agents in nav
    await page.click('nav >> text=/Agents/i');
    
    // Should navigate to agents page
    await page.waitForURL('**/agents**', { timeout: 5000 });
    
    // Should show agents list or empty state
    await expect(
      page.locator('[data-testid="agents-list"], [data-testid="empty-agents"]')
    ).toBeVisible({ timeout: 5000 });
  });
  
  test('should navigate to Appointments page', async ({ authenticatedPage: page }) => {
    await page.goto('/dashboard');
    
    // Click Appointments in nav
    await page.click('nav >> text=/Appointments/i');
    
    // Should navigate to appointments page
    await page.waitForURL('**/appointments**', { timeout: 5000 });
    
    // Should show calendar or appointments list
    await expect(
      page.locator('[data-testid="appointments-calendar"], [data-testid="appointments-list"]')
    ).toBeVisible({ timeout: 5000 });
  });
  
  test('should navigate to Services page', async ({ authenticatedPage: page }) => {
    await page.goto('/dashboard');
    
    // Click Services in nav
    await page.click('nav >> text=/Services/i');
    
    // Should navigate to services page
    await page.waitForURL('**/services**', { timeout: 5000 });
    
    // Should show services list or empty state
    await expect(
      page.locator('[data-testid="services-list"], [data-testid="empty-services"]')
    ).toBeVisible({ timeout: 5000 });
  });
  
  test('should navigate to Settings page', async ({ authenticatedPage: page }) => {
    await page.goto('/dashboard');
    
    // Click Settings in nav
    await page.click('nav >> text=/Settings/i');
    
    // Should navigate to settings page
    await page.waitForURL('**/settings**', { timeout: 5000 });
    
    // Should show settings tabs or sections
    await expect(
      page.locator('[data-testid="settings-content"], text=/API Keys|Profile/i')
    ).toBeVisible({ timeout: 5000 });
  });
  
  test('should display user menu with profile options', async ({ authenticatedPage: page }) => {
    await page.goto('/dashboard');
    
    // Open user menu
    await page.click('[data-testid="user-menu"]');
    
    // Should show menu items
    await expect(page.locator('text=/Profile|Account/i')).toBeVisible();
    await expect(page.locator('text=/Settings/i')).toBeVisible();
    await expect(page.locator('text=/Logout|Sign Out/i')).toBeVisible();
  });
  
  test('should show dashboard stats and metrics', async ({ authenticatedPage: page }) => {
    await page.goto('/dashboard');
    
    // Should show some stats cards (exact content may vary)
    const statsSelectors = [
      '[data-testid="stats-card"]',
      '[data-testid="metrics-card"]',
      'text=/Total Appointments|Active Agents|Total Calls/i',
    ];
    
    let foundStats = false;
    for (const selector of statsSelectors) {
      const element = page.locator(selector).first();
      if (await element.isVisible().catch(() => false)) {
        foundStats = true;
        break;
      }
    }
    
    // At least one stats indicator should be visible
    expect(foundStats).toBeTruthy();
  });
  
  test('should highlight active navigation item', async ({ authenticatedPage: page }) => {
    await page.goto('/dashboard');
    
    // Navigate to Agents
    await page.click('nav >> text=/Agents/i');
    await page.waitForURL('**/agents**', { timeout: 5000 });
    
    // Agents nav item should be highlighted/active
    const agentsNav = page.locator('nav >> text=/Agents/i').first();
    await expect(agentsNav).toHaveClass(/active|selected|current/i);
  });
  
  test('should be responsive and show mobile menu', async ({ authenticatedPage: page }) => {
    await page.goto('/dashboard');
    
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Desktop nav might be hidden
    const desktopNav = page.locator('[data-testid="sidebar"]').first();
    const isDesktopNavVisible = await desktopNav.isVisible().catch(() => false);
    
    if (!isDesktopNavVisible) {
      // Should show mobile menu button
      await expect(
        page.locator('[data-testid="mobile-menu-button"], [aria-label*="menu"]')
      ).toBeVisible();
    }
  });
});

test.describe('Dashboard Overview', () => {
  
  test('should show recent activity or appointments', async ({ authenticatedPage: page }) => {
    await page.goto('/dashboard');
    
    // Should show some activity section
    const activitySelectors = [
      '[data-testid="recent-activity"]',
      '[data-testid="recent-appointments"]',
      'text=/Recent|Upcoming|Latest/i',
    ];
    
    let foundActivity = false;
    for (const selector of activitySelectors) {
      const element = page.locator(selector).first();
      if (await element.isVisible().catch(() => false)) {
        foundActivity = true;
        break;
      }
    }
    
    expect(foundActivity).toBeTruthy();
  });
  
  test('should allow quick actions from dashboard', async ({ authenticatedPage: page }) => {
    await page.goto('/dashboard');
    
    // Should have quick action buttons
    const quickActionSelectors = [
      'text=/Create Agent|New Agent/i',
      'text=/Add Appointment|New Appointment/i',
      'text=/Add Service|New Service/i',
    ];
    
    let foundQuickActions = false;
    for (const selector of quickActionSelectors) {
      const element = page.locator(selector).first();
      if (await element.isVisible().catch(() => false)) {
        foundQuickActions = true;
        break;
      }
    }
    
    expect(foundQuickActions).toBeTruthy();
  });
});
