import { test, expect } from '@playwright/test';

/**
 * Setup Test User
 * This test creates a test user account that will be used by other tests
 */

test.describe('Setup Test User', () => {
  
  test('should create a test user account via signup', async ({ page }) => {
    await page.goto('/signup');
    await page.waitForLoadState('networkidle');
    
    // Fill signup form
    const testUser = {
      name: 'Test User',
      businessName: 'Test Business',
      phone: '+1234567890',
      email: 'test@example.com',
      password: 'TestPass123!@'
    };
    
    // Fill all required fields
    await page.fill('input#name', testUser.name);
    await page.fill('input#business_name', testUser.businessName);
    await page.fill('input#phone', testUser.phone);
    await page.fill('input#signup-email', testUser.email);
    await page.fill('input#signup-password', testUser.password);
    await page.fill('input#signup-confirm-password', testUser.password);
    
    // Wait a moment for password validation
    await page.waitForTimeout(500);
    
    // Submit form
    await page.click('button[type="submit"]');
    
    // Wait for success or navigation
    await page.waitForTimeout(3000);
    
    // Check if we got to success page or dashboard
    const url = page.url();
    const isSuccess = url.includes('success') || url.includes('dashboard') || !url.includes('signup');
    
    expect(isSuccess).toBeTruthy();
    
    console.log('✅ Test user created successfully:', testUser.email);
  });
  
});
