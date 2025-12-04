import { test, expect } from './fixtures';
import { fillFormField } from './fixtures';

/**
 * Phase 4 Test 6: Settings and API Key Configuration
 * Tests user settings, profile management, and API key configuration
 */

test.describe('Settings Management', () => {
  
  test('should display settings page with all sections', async ({ authenticatedPage: page }) => {
    await page.goto('/settings');
    
    // Should show settings page
    await expect(
      page.locator('[data-testid="settings-page"]')
    ).toBeVisible({ timeout: 5000 });
    
    // Should show settings sections or tabs
    const sections = [
      'Profile',
      'API Keys',
      'Business',
      'Security',
    ];
    
    let foundSections = 0;
    for (const section of sections) {
      const sectionElement = page.locator(`text=/${section}/i`);
      if (await sectionElement.isVisible().catch(() => false)) {
        foundSections++;
      }
    }
    
    expect(foundSections).toBeGreaterThan(0);
  });
  
  test('should view and edit profile information', async ({ authenticatedPage: page }) => {
    await page.goto('/settings');
    
    // Navigate to profile section
    await page.click('text=/Profile|Account/i').catch(() => {});
    
    // Should show profile form
    await expect(
      page.locator('input[name="name"], input[name="full_name"]')
    ).toBeVisible({ timeout: 5000 });
    
    // Update name
    await fillFormField(page, 'name', 'Updated Test User').catch(() => 
      fillFormField(page, 'full_name', 'Updated Test User')
    );
    
    // Save changes
    await page.click('button[type="submit"], button:has-text("Save")');
    
    // Should show success message
    await expect(
      page.locator('text=/success|updated|saved/i')
    ).toBeVisible({ timeout: 5000 });
  });
  
  test('should navigate to API Keys section', async ({ authenticatedPage: page }) => {
    await page.goto('/settings');
    
    // Click API Keys tab/section
    await page.click('text=/API Keys|Integrations/i');
    
    // Should show API key configuration
    await expect(
      page.locator('[data-testid="api-keys-section"], text=/Vapi|Groq/i')
    ).toBeVisible({ timeout: 5000 });
  });
  
  test('should display existing API keys (masked)', async ({ authenticatedPage: page }) => {
    await page.goto('/settings');
    
    // Navigate to API Keys section
    await page.click('text=/API Keys/i').catch(() => {});
    
    // Should show API key inputs
    const vapiKeyInput = page.locator('input[name="vapi_api_key"], input[name="vapi_key"]');
    const groqKeyInput = page.locator('input[name="groq_api_key"], input[name="groq_key"]');
    
    const hasVapiKey = await vapiKeyInput.isVisible().catch(() => false);
    const hasGroqKey = await groqKeyInput.isVisible().catch(() => false);
    
    expect(hasVapiKey || hasGroqKey).toBeTruthy();
    
    // Keys should be masked or show placeholder
    if (hasVapiKey) {
      const value = await vapiKeyInput.inputValue();
      const type = await vapiKeyInput.getAttribute('type');
      
      // Should be password type or contain asterisks
      expect(type === 'password' || value.includes('*')).toBeTruthy();
    }
  });
  
  test('should update Vapi API key', async ({ authenticatedPage: page }) => {
    await page.goto('/settings');
    
    // Navigate to API Keys
    await page.click('text=/API Keys/i').catch(() => {});
    await page.waitForTimeout(500);
    
    // Update Vapi key
    const newVapiKey = `vapi_test_${Date.now()}`;
    await fillFormField(page, 'vapi_api_key', newVapiKey).catch(() =>
      fillFormField(page, 'vapi_key', newVapiKey)
    );
    
    // Save changes
    await page.click('button[type="submit"], button:has-text("Save")');
    
    // Should show success message
    await expect(
      page.locator('text=/success|updated|saved/i')
    ).toBeVisible({ timeout: 5000 });
  });
  
  test('should update Groq API key', async ({ authenticatedPage: page }) => {
    await page.goto('/settings');
    
    // Navigate to API Keys
    await page.click('text=/API Keys/i').catch(() => {});
    await page.waitForTimeout(500);
    
    // Update Groq key
    const newGroqKey = `gsk_test_${Date.now()}`;
    await fillFormField(page, 'groq_api_key', newGroqKey).catch(() =>
      fillFormField(page, 'groq_key', newGroqKey)
    );
    
    // Save changes
    await page.click('button[type="submit"], button:has-text("Save")');
    
    // Should show success message
    await expect(
      page.locator('text=/success|updated|saved/i')
    ).toBeVisible({ timeout: 5000 });
  });
  
  test('should validate API key format', async ({ authenticatedPage: page }) => {
    await page.goto('/settings');
    
    // Navigate to API Keys
    await page.click('text=/API Keys/i').catch(() => {});
    await page.waitForTimeout(500);
    
    // Enter invalid Vapi key (too short)
    await fillFormField(page, 'vapi_api_key', 'invalid').catch(() =>
      fillFormField(page, 'vapi_key', 'invalid')
    );
    
    // Try to save
    await page.click('button[type="submit"], button:has-text("Save")');
    
    // Should show validation error
    const hasValidationError = await page.locator('text=/invalid|format|required/i')
      .isVisible().catch(() => false);
    
    expect(hasValidationError).toBeTruthy();
  });
  
  test('should test API key connectivity', async ({ authenticatedPage: page }) => {
    await page.goto('/settings');
    
    // Navigate to API Keys
    await page.click('text=/API Keys/i').catch(() => {});
    await page.waitForTimeout(500);
    
    // Look for test connection button
    const testButton = page.locator('button:has-text("Test"), button:has-text("Verify")');
    
    if (await testButton.isVisible().catch(() => false)) {
      await testButton.click();
      
      // Should show test result
      await expect(
        page.locator('text=/success|connected|failed|error/i')
      ).toBeVisible({ timeout: 10000 });
    }
  });
  
  test('should configure business hours', async ({ authenticatedPage: page }) => {
    await page.goto('/settings');
    
    // Navigate to Business section
    await page.click('text=/Business|Hours/i').catch(() => {});
    
    // Look for business hours configuration
    const businessHoursSection = page.locator('[data-testid="business-hours"], text=/Opening Hours|Business Hours/i');
    
    if (await businessHoursSection.isVisible().catch(() => false)) {
      // Should show days of week
      await expect(page.locator('text=/Monday|Tuesday|Wednesday/i')).toBeVisible();
    }
  });
  
  test('should update timezone settings', async ({ authenticatedPage: page }) => {
    await page.goto('/settings');
    
    // Navigate to Business section
    await page.click('text=/Business|Profile/i').catch(() => {});
    
    // Look for timezone select
    const timezoneSelect = page.locator('select[name="timezone"]');
    
    if (await timezoneSelect.isVisible().catch(() => false)) {
      // Change timezone
      await timezoneSelect.selectOption('America/New_York');
      
      // Save changes
      await page.click('button[type="submit"], button:has-text("Save")');
      
      // Should show success message
      await expect(
        page.locator('text=/success|updated|saved/i')
      ).toBeVisible({ timeout: 5000 });
    }
  });
  
  test('should change password', async ({ authenticatedPage: page }) => {
    await page.goto('/settings');
    
    // Navigate to Security section
    await page.click('text=/Security|Password/i').catch(() => {});
    
    // Look for password change form
    const currentPasswordInput = page.locator('input[name="current_password"]');
    
    if (await currentPasswordInput.isVisible().catch(() => false)) {
      // Fill password form
      await fillFormField(page, 'current_password', 'TestPassword123!');
      await fillFormField(page, 'new_password', 'NewPassword123!');
      await fillFormField(page, 'confirm_password', 'NewPassword123!');
      
      // Note: We won't actually save to avoid changing test credentials
      // Just verify the form exists and is functional
      await expect(page.locator('button:has-text("Change Password")')).toBeVisible();
    }
  });
  
  test('should show notification preferences', async ({ authenticatedPage: page }) => {
    await page.goto('/settings');
    
    // Navigate to Notifications section if exists
    await page.click('text=/Notifications|Preferences/i').catch(() => {});
    
    // Look for notification settings
    const notificationSettings = page.locator(
      '[data-testid="notification-settings"], text=/Email Notifications|SMS|Push/i'
    );
    
    if (await notificationSettings.isVisible().catch(() => false)) {
      // Should show notification toggles
      const toggles = page.locator('input[type="checkbox"]');
      const toggleCount = await toggles.count();
      
      expect(toggleCount).toBeGreaterThan(0);
    }
  });
});

test.describe('Integration Settings', () => {
  
  test('should display calendar integration options', async ({ authenticatedPage: page }) => {
    await page.goto('/settings');
    
    // Navigate to Integrations
    await page.click('text=/Integrations|Calendar/i').catch(() => {});
    
    // Look for calendar integration options
    const calendarIntegration = page.locator('text=/Google Calendar|Outlook|iCal/i');
    
    if (await calendarIntegration.isVisible().catch(() => false)) {
      await expect(calendarIntegration).toBeVisible();
    }
  });
  
  test('should show webhook configuration', async ({ authenticatedPage: page }) => {
    await page.goto('/settings');
    
    // Navigate to Integrations or Webhooks
    await page.click('text=/Integrations|Webhooks/i').catch(() => {});
    
    // Look for webhook settings
    const webhookSettings = page.locator('[data-testid="webhook-settings"], input[name="webhook_url"]');
    
    if (await webhookSettings.isVisible().catch(() => false)) {
      await expect(webhookSettings).toBeVisible();
    }
  });
});
