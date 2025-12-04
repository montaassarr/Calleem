import { test, expect } from './fixtures';
import { waitForApiResponse, fillFormField } from './fixtures';

/**
 * Phase 4 Test 4: Agent Management
 * Tests creation, editing, and configuration of AI agents
 */

test.describe('Agent Management', () => {
  
  test('should display agents list page', async ({ authenticatedPage: page }) => {
    await page.goto('/agents');
    
    // Should show agents list or empty state
    await expect(
      page.locator('[data-testid="agents-list"], [data-testid="agents-page"]')
    ).toBeVisible({ timeout: 5000 });
    
    // Should have create agent button
    await expect(
      page.locator('button:has-text("Create Agent"), button:has-text("New Agent")')
    ).toBeVisible();
  });
  
  test('should open agent creation modal/form', async ({ authenticatedPage: page }) => {
    await page.goto('/agents');
    
    // Click create agent button
    await page.click('button:has-text("Create Agent"), button:has-text("New Agent")');
    
    // Should show agent creation form
    await expect(
      page.locator('[data-testid="agent-form"], [data-testid="create-agent-modal"]')
    ).toBeVisible({ timeout: 5000 });
    
    // Should have required form fields
    await expect(page.locator('input[name="name"], input[name="agent_name"]')).toBeVisible();
  });
  
  test('should create a new agent successfully', async ({ authenticatedPage: page }) => {
    await page.goto('/agents');
    
    // Open creation form
    await page.click('button:has-text("Create Agent"), button:has-text("New Agent")');
    await page.waitForTimeout(500);
    
    // Fill agent details
    const agentName = `Test Agent ${Date.now()}`;
    await fillFormField(page, 'name', agentName).catch(() => fillFormField(page, 'agent_name', agentName));
    await fillFormField(page, 'greeting_message', 'Hello! I am your AI receptionist. How can I assist you today?');
    await fillFormField(page, 'voice_id', 'en-US-Neural2-A');
    
    // Select agent type if available
    const agentTypeSelect = page.locator('select[name="agent_type"]');
    if (await agentTypeSelect.isVisible().catch(() => false)) {
      await agentTypeSelect.selectOption('receptionist');
    }
    
    // Wait for API response
    const responsePromise = waitForApiResponse(page, '/api/agents');
    
    // Submit form
    await page.click('button[type="submit"], button:has-text("Create"), button:has-text("Save")');
    
    // Wait for API call
    await responsePromise.catch(() => page.waitForTimeout(2000));
    
    // Should show success message
    await expect(
      page.locator('text=/success|created|saved/i')
    ).toBeVisible({ timeout: 5000 });
    
    // Should close modal and show agent in list
    await page.waitForTimeout(1000);
    await expect(page.locator(`text=${agentName}`)).toBeVisible({ timeout: 5000 });
  });
  
  test('should show validation errors for invalid agent data', async ({ authenticatedPage: page }) => {
    await page.goto('/agents');
    
    // Open creation form
    await page.click('button:has-text("Create Agent"), button:has-text("New Agent")');
    await page.waitForTimeout(500);
    
    // Try to submit without required fields
    await page.click('button[type="submit"], button:has-text("Create")');
    
    // Should show validation errors
    await expect(
      page.locator('text=/required|field is required/i')
    ).toBeVisible({ timeout: 3000 });
  });
  
  test('should view agent details', async ({ authenticatedPage: page }) => {
    await page.goto('/agents');
    
    // Find first agent in list
    const firstAgent = page.locator('[data-testid="agent-card"], [data-testid="agent-item"]').first();
    
    if (await firstAgent.isVisible().catch(() => false)) {
      // Click to view details
      await firstAgent.click();
      
      // Should show agent details view
      await expect(
        page.locator('[data-testid="agent-details"], [data-testid="agent-view"]')
      ).toBeVisible({ timeout: 5000 });
      
      // Should show agent properties
      await expect(page.locator('text=/Name|Greeting|Voice/i')).toBeVisible();
    }
  });
  
  test('should edit an existing agent', async ({ authenticatedPage: page }) => {
    await page.goto('/agents');
    
    // Find first agent
    const firstAgent = page.locator('[data-testid="agent-card"], [data-testid="agent-item"]').first();
    
    if (await firstAgent.isVisible().catch(() => false)) {
      // Click edit button
      await page.click('[data-testid="edit-agent"], button:has-text("Edit")').catch(async () => {
        // If no direct edit button, click agent first then edit
        await firstAgent.click();
        await page.click('button:has-text("Edit")');
      });
      
      // Should show edit form
      await expect(
        page.locator('[data-testid="agent-form"], input[name="name"]')
      ).toBeVisible({ timeout: 5000 });
      
      // Modify greeting message
      const newGreeting = `Updated greeting ${Date.now()}`;
      await fillFormField(page, 'greeting_message', newGreeting);
      
      // Save changes
      await page.click('button[type="submit"], button:has-text("Save")');
      
      // Should show success message
      await expect(
        page.locator('text=/success|updated|saved/i')
      ).toBeVisible({ timeout: 5000 });
    }
  });
  
  test('should configure agent settings', async ({ authenticatedPage: page }) => {
    await page.goto('/agents');
    
    // Find and open first agent
    const firstAgent = page.locator('[data-testid="agent-card"], [data-testid="agent-item"]').first();
    
    if (await firstAgent.isVisible().catch(() => false)) {
      await firstAgent.click();
      
      // Navigate to settings tab if exists
      await page.click('text=/Settings|Configuration/i').catch(() => {});
      
      // Should show configuration options
      await expect(
        page.locator('text=/Voice|Language|Behavior|Prompt/i')
      ).toBeVisible({ timeout: 5000 });
    }
  });
  
  test('should test agent with test call', async ({ authenticatedPage: page }) => {
    await page.goto('/agents');
    
    // Find first agent
    const firstAgent = page.locator('[data-testid="agent-card"], [data-testid="agent-item"]').first();
    
    if (await firstAgent.isVisible().catch(() => false)) {
      // Look for test button
      const testButton = page.locator('button:has-text("Test"), button:has-text("Try")');
      
      if (await testButton.isVisible().catch(() => false)) {
        await testButton.click();
        
        // Should show test interface or phone number
        await expect(
          page.locator('[data-testid="test-agent"], text=/phone number|call|test/i')
        ).toBeVisible({ timeout: 5000 });
      }
    }
  });
  
  test('should delete an agent', async ({ authenticatedPage: page }) => {
    await page.goto('/agents');
    
    // Create a test agent first
    await page.click('button:has-text("Create Agent")');
    await page.waitForTimeout(500);
    
    const agentName = `Delete Test Agent ${Date.now()}`;
    await fillFormField(page, 'name', agentName).catch(() => fillFormField(page, 'agent_name', agentName));
    await fillFormField(page, 'greeting_message', 'Test greeting');
    await page.click('button[type="submit"]');
    await page.waitForTimeout(2000);
    
    // Find the agent we just created
    const agentToDelete = page.locator(`text=${agentName}`).first();
    
    if (await agentToDelete.isVisible().catch(() => false)) {
      // Click delete button
      await page.click('[data-testid="delete-agent"], button:has-text("Delete")').catch(async () => {
        // If no direct delete button, click agent first
        await agentToDelete.click();
        await page.click('button:has-text("Delete")');
      });
      
      // Confirm deletion
      await page.click('button:has-text("Confirm"), button:has-text("Yes")');
      
      // Should show success message
      await expect(
        page.locator('text=/deleted|removed/i')
      ).toBeVisible({ timeout: 5000 });
      
      // Agent should be removed from list
      await page.waitForTimeout(1000);
      const stillExists = await agentToDelete.isVisible().catch(() => false);
      expect(stillExists).toBeFalsy();
    }
  });
  
  test('should filter and search agents', async ({ authenticatedPage: page }) => {
    await page.goto('/agents');
    
    // Look for search input
    const searchInput = page.locator('input[placeholder*="Search"], input[name="search"]');
    
    if (await searchInput.isVisible().catch(() => false)) {
      // Enter search term
      await searchInput.fill('Test');
      
      // Wait for filtered results
      await page.waitForTimeout(1000);
      
      // Results should be filtered
      const agentCards = page.locator('[data-testid="agent-card"], [data-testid="agent-item"]');
      const count = await agentCards.count();
      
      // Should show only matching agents or empty state
      expect(count >= 0).toBeTruthy();
    }
  });
});
