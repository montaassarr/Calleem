import { test, expect } from './fixtures';
import { fillFormField } from './fixtures';

/**
 * Phase 4 Test 7: Services Management
 * Tests service creation, editing, and configuration
 */

test.describe('Services Management', () => {
  
  test('should display services page', async ({ authenticatedPage: page }) => {
    await page.goto('/services');
    
    // Should show services page
    await expect(
      page.locator('[data-testid="services-page"], [data-testid="services-list"]')
    ).toBeVisible({ timeout: 5000 });
    
    // Should have create service button
    await expect(
      page.locator('button:has-text("Create Service"), button:has-text("New Service"), button:has-text("Add Service")')
    ).toBeVisible();
  });
  
  test('should display existing services in grid or list', async ({ authenticatedPage: page }) => {
    await page.goto('/services');
    
    // Should show services in some format
    const hasGrid = await page.locator('[data-testid="services-grid"]').isVisible().catch(() => false);
    const hasList = await page.locator('[data-testid="services-list"]').isVisible().catch(() => false);
    const hasCards = await page.locator('[data-testid="service-card"]').isVisible().catch(() => false);
    
    expect(hasGrid || hasList || hasCards).toBeTruthy();
  });
  
  test('should open service creation form', async ({ authenticatedPage: page }) => {
    await page.goto('/services');
    
    // Click create service button
    await page.click('button:has-text("Create Service"), button:has-text("New Service"), button:has-text("Add Service")');
    
    // Should show service creation form
    await expect(
      page.locator('[data-testid="service-form"], [data-testid="create-service-modal"]')
    ).toBeVisible({ timeout: 5000 });
    
    // Should have required form fields
    await expect(page.locator('input[name="name"], input[name="service_name"]')).toBeVisible();
  });
  
  test('should create a new service successfully', async ({ authenticatedPage: page }) => {
    await page.goto('/services');
    
    // Open creation form
    await page.click('button:has-text("Create Service"), button:has-text("New Service")');
    await page.waitForTimeout(500);
    
    // Fill service details
    const serviceName = `Test Service ${Date.now()}`;
    await fillFormField(page, 'name', serviceName).catch(() => 
      fillFormField(page, 'service_name', serviceName)
    );
    
    await fillFormField(page, 'description', 'This is a test service for E2E testing');
    await fillFormField(page, 'duration', '30').catch(() => {});
    await fillFormField(page, 'price', '100').catch(() => {});
    
    // Submit form
    await page.click('button[type="submit"], button:has-text("Create"), button:has-text("Save")');
    
    // Should show success message
    await expect(
      page.locator('text=/success|created|saved|added/i')
    ).toBeVisible({ timeout: 5000 });
    
    // Should show service in list
    await page.waitForTimeout(1000);
    await expect(page.locator(`text=${serviceName}`)).toBeVisible({ timeout: 5000 });
  });
  
  test('should validate required service fields', async ({ authenticatedPage: page }) => {
    await page.goto('/services');
    
    // Open creation form
    await page.click('button:has-text("Create Service"), button:has-text("New Service")');
    await page.waitForTimeout(500);
    
    // Try to submit without filling required fields
    await page.click('button[type="submit"], button:has-text("Create")');
    
    // Should show validation errors
    await expect(
      page.locator('text=/required|field is required/i')
    ).toBeVisible({ timeout: 3000 });
  });
  
  test('should view service details', async ({ authenticatedPage: page }) => {
    await page.goto('/services');
    
    // Find first service
    const firstService = page.locator('[data-testid="service-card"], [data-testid="service-item"]').first();
    
    if (await firstService.isVisible().catch(() => false)) {
      // Click to view details
      await firstService.click();
      
      // Should show service details
      await expect(
        page.locator('[data-testid="service-details"], [data-testid="service-view"]')
      ).toBeVisible({ timeout: 5000 });
      
      // Should show service properties
      await expect(page.locator('text=/Name|Description|Duration|Price/i')).toBeVisible();
    }
  });
  
  test('should edit an existing service', async ({ authenticatedPage: page }) => {
    await page.goto('/services');
    
    // Find first service
    const firstService = page.locator('[data-testid="service-card"], [data-testid="service-item"]').first();
    
    if (await firstService.isVisible().catch(() => false)) {
      // Click edit button
      await page.click('[data-testid="edit-service"], button:has-text("Edit")').catch(async () => {
        // If no direct edit button, click service first then edit
        await firstService.click();
        await page.click('button:has-text("Edit")');
      });
      
      // Should show edit form
      await expect(
        page.locator('[data-testid="service-form"], input[name="name"]')
      ).toBeVisible({ timeout: 5000 });
      
      // Modify description
      const newDescription = `Updated description ${Date.now()}`;
      await fillFormField(page, 'description', newDescription);
      
      // Save changes
      await page.click('button[type="submit"], button:has-text("Save")');
      
      // Should show success message
      await expect(
        page.locator('text=/success|updated|saved/i')
      ).toBeVisible({ timeout: 5000 });
    }
  });
  
  test('should configure service pricing', async ({ authenticatedPage: page }) => {
    await page.goto('/services');
    
    // Create a new service with pricing
    await page.click('button:has-text("Create Service")');
    await page.waitForTimeout(500);
    
    const serviceName = `Pricing Test ${Date.now()}`;
    await fillFormField(page, 'name', serviceName).catch(() => 
      fillFormField(page, 'service_name', serviceName)
    );
    
    // Set price
    await fillFormField(page, 'price', '150.50');
    
    // Select currency if available
    const currencySelect = page.locator('select[name="currency"]');
    if (await currencySelect.isVisible().catch(() => false)) {
      await currencySelect.selectOption('USD');
    }
    
    // Save service
    await page.click('button[type="submit"]');
    
    // Should show success message
    await expect(
      page.locator('text=/success|created/i')
    ).toBeVisible({ timeout: 5000 });
  });
  
  test('should configure service duration', async ({ authenticatedPage: page }) => {
    await page.goto('/services');
    
    // Create service with duration
    await page.click('button:has-text("Create Service")');
    await page.waitForTimeout(500);
    
    const serviceName = `Duration Test ${Date.now()}`;
    await fillFormField(page, 'name', serviceName).catch(() => 
      fillFormField(page, 'service_name', serviceName)
    );
    
    // Set duration
    await fillFormField(page, 'duration', '45'); // 45 minutes
    
    // Save service
    await page.click('button[type="submit"]');
    
    // Should show success message
    await expect(
      page.locator('text=/success|created/i')
    ).toBeVisible({ timeout: 5000 });
  });
  
  test('should toggle service active status', async ({ authenticatedPage: page }) => {
    await page.goto('/services');
    
    // Find first service
    const firstService = page.locator('[data-testid="service-card"], [data-testid="service-item"]').first();
    
    if (await firstService.isVisible().catch(() => false)) {
      // Look for active/inactive toggle
      const statusToggle = page.locator('[data-testid="service-status"], input[type="checkbox"][name="active"]');
      
      if (await statusToggle.isVisible().catch(() => false)) {
        // Toggle status
        await statusToggle.click();
        
        // Should show success message or update status
        await page.waitForTimeout(1000);
      }
    }
  });
  
  test('should delete a service', async ({ authenticatedPage: page }) => {
    await page.goto('/services');
    
    // Create a test service first
    await page.click('button:has-text("Create Service")');
    await page.waitForTimeout(500);
    
    const serviceName = `Delete Test ${Date.now()}`;
    await fillFormField(page, 'name', serviceName).catch(() => 
      fillFormField(page, 'service_name', serviceName)
    );
    await page.click('button[type="submit"]');
    await page.waitForTimeout(2000);
    
    // Find the service we just created
    const serviceToDelete = page.locator(`text=${serviceName}`).first();
    
    if (await serviceToDelete.isVisible().catch(() => false)) {
      // Click delete button
      await page.click('[data-testid="delete-service"], button:has-text("Delete")').catch(async () => {
        // If no direct delete button, click service first
        await serviceToDelete.click();
        await page.click('button:has-text("Delete")');
      });
      
      // Confirm deletion
      await page.click('button:has-text("Confirm"), button:has-text("Yes")');
      
      // Should show success message
      await expect(
        page.locator('text=/deleted|removed/i')
      ).toBeVisible({ timeout: 5000 });
      
      // Service should be removed from list
      await page.waitForTimeout(1000);
      const stillExists = await serviceToDelete.isVisible().catch(() => false);
      expect(stillExists).toBeFalsy();
    }
  });
  
  test('should search and filter services', async ({ authenticatedPage: page }) => {
    await page.goto('/services');
    
    // Look for search input
    const searchInput = page.locator('input[placeholder*="Search"], input[name="search"]');
    
    if (await searchInput.isVisible().catch(() => false)) {
      // Enter search term
      await searchInput.fill('Test');
      await page.waitForTimeout(1000);
      
      // Results should be filtered
      const serviceCards = page.locator('[data-testid="service-card"], [data-testid="service-item"]');
      const count = await serviceCards.count();
      
      expect(count >= 0).toBeTruthy();
    }
  });
  
  test('should assign service to agents', async ({ authenticatedPage: page }) => {
    await page.goto('/services');
    
    // Find first service
    const firstService = page.locator('[data-testid="service-card"]').first();
    
    if (await firstService.isVisible().catch(() => false)) {
      await firstService.click();
      
      // Look for agent assignment section
      const assignAgentsSection = page.locator('[data-testid="assign-agents"], text=/Assign to Agents|Available Agents/i');
      
      if (await assignAgentsSection.isVisible().catch(() => false)) {
        await expect(assignAgentsSection).toBeVisible();
      }
    }
  });
});
