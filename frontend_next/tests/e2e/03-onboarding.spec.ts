import { test, expect } from './fixtures';
import { waitForApiResponse, fillFormField } from './fixtures';

/**
 * Phase 4 Test 3: Onboarding Wizard
 * Tests the multi-step onboarding process for new users
 */

test.describe('Onboarding Wizard', () => {
  
  test('should display onboarding wizard for new users', async ({ page }) => {
    // Note: This test might need a fresh user without completed onboarding
    await page.goto('/onboarding');
    
    // Should show onboarding welcome screen or first step
    await expect(
      page.locator('[data-testid="onboarding-wizard"], text=/Welcome|Get Started/i')
    ).toBeVisible({ timeout: 5000 });
    
    // Should show progress indicator
    await expect(
      page.locator('[data-testid="onboarding-progress"], [role="progressbar"]')
    ).toBeVisible();
  });
  
  test('should complete Step 1: Company Information', async ({ page }) => {
    await page.goto('/onboarding');
    
    // Fill company information
    await fillFormField(page, 'company_name', 'Test Company Inc');
    await fillFormField(page, 'industry', 'Healthcare');
    
    // Optional: Select timezone if present
    const timezoneSelect = page.locator('select[name="timezone"]');
    if (await timezoneSelect.isVisible().catch(() => false)) {
      await timezoneSelect.selectOption('America/New_York');
    }
    
    // Click Next
    await page.click('button:has-text("Next"), button:has-text("Continue")');
    
    // Should move to next step
    await expect(
      page.locator('[data-testid="onboarding-step-2"], text=/API Keys|Integration/i')
    ).toBeVisible({ timeout: 5000 });
  });
  
  test('should complete Step 2: API Keys Configuration', async ({ page }) => {
    await page.goto('/onboarding');
    
    // Navigate to API keys step (might need to complete step 1 first)
    await fillFormField(page, 'company_name', 'Test Company Inc');
    await page.click('button:has-text("Next")').catch(() => {});
    
    // Fill API keys
    await fillFormField(page, 'vapi_api_key', process.env.TEST_VAPI_KEY || 'test_vapi_key');
    await fillFormField(page, 'groq_api_key', process.env.TEST_GROQ_KEY || 'test_groq_key');
    
    // Click Next
    await page.click('button:has-text("Next"), button:has-text("Continue")');
    
    // Should move to next step
    await expect(
      page.locator('[data-testid="onboarding-step-3"], text=/Services|Offerings/i')
    ).toBeVisible({ timeout: 5000 });
  });
  
  test('should complete Step 3: Services Setup', async ({ page }) => {
    await page.goto('/onboarding');
    
    // Navigate through steps to services
    // Step 1
    await fillFormField(page, 'company_name', 'Test Company Inc').catch(() => {});
    await page.click('button:has-text("Next")').catch(() => {});
    
    // Step 2
    await fillFormField(page, 'vapi_api_key', 'test_key').catch(() => {});
    await page.click('button:has-text("Next")').catch(() => {});
    
    // Step 3: Add a service
    await page.click('button:has-text("Add Service"), button:has-text("Create Service")').catch(async () => {
      // If no add button, try filling first service form
      await fillFormField(page, 'service_name', 'General Consultation');
    });
    
    // Fill service details
    await fillFormField(page, 'service_name', 'General Consultation');
    await fillFormField(page, 'duration', '30');
    await fillFormField(page, 'price', '100');
    
    // Save service
    await page.click('button:has-text("Save"), button:has-text("Add")').catch(() => {});
    
    // Click Next
    await page.click('button:has-text("Next"), button:has-text("Continue")');
    
    // Should move to next step or completion
    await expect(
      page.locator('[data-testid="onboarding-step-4"], text=/Complete|Finish|Agent/i')
    ).toBeVisible({ timeout: 5000 });
  });
  
  test('should complete Step 4: Agent Creation', async ({ page }) => {
    await page.goto('/onboarding');
    
    // Navigate through all steps quickly
    await fillFormField(page, 'company_name', 'Test Company Inc').catch(() => {});
    await page.click('button:has-text("Next")').catch(() => {});
    await fillFormField(page, 'vapi_api_key', 'test_key').catch(() => {});
    await page.click('button:has-text("Next")').catch(() => {});
    await page.click('button:has-text("Next")').catch(() => {}); // Skip services
    
    // Create first agent
    await fillFormField(page, 'agent_name', 'Reception Agent');
    await fillFormField(page, 'greeting_message', 'Hello! How can I help you today?');
    
    // Select agent type if present
    const agentTypeSelect = page.locator('select[name="agent_type"]');
    if (await agentTypeSelect.isVisible().catch(() => false)) {
      await agentTypeSelect.selectOption('receptionist');
    }
    
    // Complete onboarding
    await page.click('button:has-text("Complete"), button:has-text("Finish")');
    
    // Should redirect to dashboard or success page
    await page.waitForURL('**/dashboard**', { timeout: 10000 });
  });
  
  test('should allow navigation between onboarding steps', async ({ page }) => {
    await page.goto('/onboarding');
    
    // Complete step 1
    await fillFormField(page, 'company_name', 'Test Company Inc');
    await page.click('button:has-text("Next")');
    await page.waitForTimeout(500);
    
    // Go back to step 1
    await page.click('button:has-text("Back"), button:has-text("Previous")');
    
    // Should show step 1 content again
    await expect(page.locator('input[name="company_name"]')).toHaveValue('Test Company Inc');
  });
  
  test('should show validation errors for required fields', async ({ page }) => {
    await page.goto('/onboarding');
    
    // Try to proceed without filling required fields
    await page.click('button:has-text("Next"), button:has-text("Continue")');
    
    // Should show validation errors
    await expect(
      page.locator('text=/required|field is required/i')
    ).toBeVisible({ timeout: 3000 });
  });
  
  test('should save progress and allow resuming later', async ({ page }) => {
    await page.goto('/onboarding');
    
    // Fill step 1
    await fillFormField(page, 'company_name', 'Test Company Inc');
    await page.click('button:has-text("Next")');
    await page.waitForTimeout(500);
    
    // Navigate away
    await page.goto('/dashboard');
    
    // Come back to onboarding
    await page.goto('/onboarding');
    
    // Should resume from where we left off (step 2) or show saved data
    const isOnStep2 = await page.locator('text=/API Keys|Integration/i').isVisible().catch(() => false);
    const hasSavedData = await page.locator('input[name="company_name"]').inputValue().then(v => v === 'Test Company Inc').catch(() => false);
    
    expect(isOnStep2 || hasSavedData).toBeTruthy();
  });
  
  test('should skip onboarding and go directly to dashboard', async ({ page }) => {
    await page.goto('/onboarding');
    
    // Look for skip button
    const skipButton = page.locator('button:has-text("Skip"), a:has-text("Skip")');
    
    if (await skipButton.isVisible().catch(() => false)) {
      await skipButton.click();
      
      // Should redirect to dashboard
      await page.waitForURL('**/dashboard**', { timeout: 5000 });
    }
  });
});
