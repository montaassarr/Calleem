import { test as base, expect } from '@playwright/test';
import type { Page } from '@playwright/test';

/**
 * Test fixtures for AI Receptionist Dashboard E2E tests
 * Provides authenticated user context and common utilities
 */

export interface TestUser {
  email: string;
  password: string;
  tenantId?: string;
}

export interface AuthenticatedPage extends Page {
  user: TestUser;
}

// Extend base test with authentication fixture
export const test = base.extend<{
  authenticatedPage: AuthenticatedPage;
}>({
  authenticatedPage: async ({ page }, applyFixture) => {
    // Login with test user
    const testUser: TestUser = {
      email: process.env.TEST_USER_EMAIL || 'test@example.com',
      password: process.env.TEST_USER_PASSWORD || 'TestPass123!@',
    };

    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    // Fill login form using ID selectors (the form uses id attributes)
    await page.fill('input#email, input[type="email"]', testUser.email);
    await page.fill('input#password, input[type="password"]', testUser.password);
    await page.click('button[type="submit"]');
    
    // Wait for navigation to dashboard
    await page.waitForURL(/\/(dashboard|home|admin)/, { timeout: 10000 }).catch(() => {
      // If redirect doesn't happen, wait a bit
      return page.waitForTimeout(2000);
    });
    
    // Add user info to page object
    const authenticatedPage = page as AuthenticatedPage;
    authenticatedPage.user = testUser;
    
    await applyFixture(authenticatedPage);
    
    // Cleanup: logout after test
    try {
      await page.click('[data-testid="user-menu"]');
      await page.click('[data-testid="logout-button"]');
    } catch (error) {
      // Ignore logout errors in cleanup
    }
  },
});

export { expect };

/**
 * Utility functions for E2E tests
 */

export async function waitForApiResponse(page: Page, urlPattern: string | RegExp) {
  return page.waitForResponse(
    response => {
      const url = response.url();
      const matches = typeof urlPattern === 'string' 
        ? url.includes(urlPattern)
        : urlPattern.test(url);
      return matches && response.status() === 200;
    },
    { timeout: 10000 }
  );
}

export async function fillFormField(page: Page, fieldName: string, value: string) {
  // Try multiple selector strategies to find the field
  const selectors = [
    `input[name="${fieldName}"]`,
    `textarea[name="${fieldName}"]`,
    `input#${fieldName}`,
    `textarea#${fieldName}`,
    `input[id="${fieldName}"]`,
    `textarea[id="${fieldName}"]`
  ];
  
  for (const selector of selectors) {
    const element = page.locator(selector).first();
    if (await element.isVisible().catch(() => false)) {
      await element.fill(value);
      return;
    }
  }
  
  // If nothing worked, try the first selector anyway
  await page.fill(`input[name="${fieldName}"], input#${fieldName}`, value);
}

export async function clickAndWaitForNavigation(page: Page, selector: string) {
  await Promise.all([
    page.waitForNavigation({ waitUntil: 'networkidle' }),
    page.click(selector),
  ]);
}

export async function selectOption(page: Page, fieldName: string, value: string) {
  await page.selectOption(`select[name="${fieldName}"]`, value);
}

export async function uploadFile(page: Page, inputSelector: string, filePath: string) {
  await page.setInputFiles(inputSelector, filePath);
}

export async function waitForLoadingToFinish(page: Page) {
  // Wait for common loading indicators to disappear
  await page.waitForSelector('[data-testid="loading-spinner"]', { 
    state: 'hidden', 
    timeout: 5000 
  }).catch(() => {
    // Ignore if loading spinner doesn't exist
  });
}

export async function takeScreenshotOnFailure(page: Page, testInfo: any) {
  if (testInfo.status !== testInfo.expectedStatus) {
    const screenshot = await page.screenshot();
    await testInfo.attach('screenshot', {
      body: screenshot,
      contentType: 'image/png',
    });
  }
}
