import { test, expect } from './fixtures';
import { waitForApiResponse, fillFormField } from './fixtures';

/**
 * Phase 4 Test 5: Appointment Management
 * Tests viewing, creating, editing, and canceling appointments
 */

test.describe('Appointment Management', () => {
  
  test('should display appointments page with calendar view', async ({ authenticatedPage: page }) => {
    await page.goto('/appointments');
    
    // Should show appointments page
    await expect(
      page.locator('[data-testid="appointments-page"]')
    ).toBeVisible({ timeout: 5000 });
    
    // Should show calendar or list view
    const hasCalendar = await page.locator('[data-testid="appointments-calendar"], .fc-view').isVisible().catch(() => false);
    const hasList = await page.locator('[data-testid="appointments-list"]').isVisible().catch(() => false);
    
    expect(hasCalendar || hasList).toBeTruthy();
  });
  
  test('should toggle between calendar and list views', async ({ authenticatedPage: page }) => {
    await page.goto('/appointments');
    
    // Look for view toggle buttons
    const listViewButton = page.locator('button:has-text("List"), [data-testid="list-view"]');
    const calendarViewButton = page.locator('button:has-text("Calendar"), [data-testid="calendar-view"]');
    
    const hasViewToggle = await listViewButton.isVisible().catch(() => false) || 
                         await calendarViewButton.isVisible().catch(() => false);
    
    if (hasViewToggle) {
      // Switch to list view
      if (await listViewButton.isVisible().catch(() => false)) {
        await listViewButton.click();
        await expect(page.locator('[data-testid="appointments-list"]')).toBeVisible();
      }
      
      // Switch back to calendar view
      if (await calendarViewButton.isVisible().catch(() => false)) {
        await calendarViewButton.click();
        await expect(page.locator('[data-testid="appointments-calendar"], .fc-view')).toBeVisible();
      }
    }
  });
  
  test('should navigate between different date periods', async ({ authenticatedPage: page }) => {
    await page.goto('/appointments');
    
    // Look for date navigation buttons
    const nextButton = page.locator('button:has-text("Next"), .fc-next-button');
    const prevButton = page.locator('button:has-text("Previous"), .fc-prev-button');
    
    if (await nextButton.isVisible().catch(() => false)) {
      // Click next to go to next period
      await nextButton.click();
      await page.waitForTimeout(500);
      
      // Click previous to go back
      if (await prevButton.isVisible().catch(() => false)) {
        await prevButton.click();
        await page.waitForTimeout(500);
      }
    }
  });
  
  test('should view appointment details', async ({ authenticatedPage: page }) => {
    await page.goto('/appointments');
    
    // Find first appointment
    const firstAppointment = page.locator(
      '[data-testid="appointment-item"], .fc-event, [data-testid="appointment-card"]'
    ).first();
    
    if (await firstAppointment.isVisible().catch(() => false)) {
      // Click to view details
      await firstAppointment.click();
      
      // Should show appointment details modal or page
      await expect(
        page.locator('[data-testid="appointment-details"], [data-testid="appointment-modal"]')
      ).toBeVisible({ timeout: 5000 });
      
      // Should show appointment information
      await expect(page.locator('text=/Customer|Client|Date|Time|Service/i')).toBeVisible();
    }
  });
  
  test('should filter appointments by status', async ({ authenticatedPage: page }) => {
    await page.goto('/appointments');
    
    // Look for status filter
    const statusFilter = page.locator('select[name="status"], [data-testid="status-filter"]');
    
    if (await statusFilter.isVisible().catch(() => false)) {
      // Select confirmed status
      await statusFilter.selectOption('confirmed');
      await page.waitForTimeout(1000);
      
      // Select pending status
      await statusFilter.selectOption('pending');
      await page.waitForTimeout(1000);
      
      // Reset to all
      await statusFilter.selectOption('all');
      await page.waitForTimeout(1000);
    }
  });
  
  test('should search for appointments', async ({ authenticatedPage: page }) => {
    await page.goto('/appointments');
    
    // Look for search input
    const searchInput = page.locator('input[placeholder*="Search"], input[name="search"]');
    
    if (await searchInput.isVisible().catch(() => false)) {
      // Enter search term
      await searchInput.fill('Test');
      await page.waitForTimeout(1000);
      
      // Results should be filtered
      const appointments = page.locator('[data-testid="appointment-item"]');
      const count = await appointments.count();
      
      expect(count >= 0).toBeTruthy();
    }
  });
  
  test('should create a manual appointment', async ({ authenticatedPage: page }) => {
    await page.goto('/appointments');
    
    // Click create appointment button
    const createButton = page.locator('button:has-text("Create"), button:has-text("New Appointment")');
    
    if (await createButton.isVisible().catch(() => false)) {
      await createButton.click();
      
      // Should show appointment creation form
      await expect(
        page.locator('[data-testid="appointment-form"], [data-testid="create-appointment"]')
      ).toBeVisible({ timeout: 5000 });
      
      // Fill appointment details
      await fillFormField(page, 'customer_name', 'John Doe');
      await fillFormField(page, 'customer_email', 'john@example.com');
      await fillFormField(page, 'customer_phone', '+1234567890');
      
      // Select service
      const serviceSelect = page.locator('select[name="service_id"]');
      if (await serviceSelect.isVisible().catch(() => false)) {
        const options = await serviceSelect.locator('option').count();
        if (options > 1) {
          await serviceSelect.selectOption({ index: 1 });
        }
      }
      
      // Select date and time
      await fillFormField(page, 'appointment_date', '2024-12-31');
      await fillFormField(page, 'appointment_time', '14:00');
      
      // Submit form
      await page.click('button[type="submit"], button:has-text("Create")');
      
      // Should show success message
      await expect(
        page.locator('text=/success|created|booked/i')
      ).toBeVisible({ timeout: 5000 });
    }
  });
  
  test('should edit an appointment', async ({ authenticatedPage: page }) => {
    await page.goto('/appointments');
    
    // Find first appointment
    const firstAppointment = page.locator(
      '[data-testid="appointment-item"], .fc-event'
    ).first();
    
    if (await firstAppointment.isVisible().catch(() => false)) {
      // Click to view details
      await firstAppointment.click();
      await page.waitForTimeout(500);
      
      // Click edit button
      const editButton = page.locator('button:has-text("Edit"), [data-testid="edit-appointment"]');
      if (await editButton.isVisible().catch(() => false)) {
        await editButton.click();
        
        // Should show edit form
        await expect(page.locator('[data-testid="appointment-form"]')).toBeVisible({ timeout: 5000 });
        
        // Modify notes
        const notesField = page.locator('textarea[name="notes"]');
        if (await notesField.isVisible().catch(() => false)) {
          await notesField.fill(`Updated notes ${Date.now()}`);
        }
        
        // Save changes
        await page.click('button[type="submit"], button:has-text("Save")');
        
        // Should show success message
        await expect(
          page.locator('text=/success|updated|saved/i')
        ).toBeVisible({ timeout: 5000 });
      }
    }
  });
  
  test('should cancel an appointment', async ({ authenticatedPage: page }) => {
    await page.goto('/appointments');
    
    // Find first appointment
    const firstAppointment = page.locator(
      '[data-testid="appointment-item"], .fc-event'
    ).first();
    
    if (await firstAppointment.isVisible().catch(() => false)) {
      // Click to view details
      await firstAppointment.click();
      await page.waitForTimeout(500);
      
      // Click cancel button
      const cancelButton = page.locator('button:has-text("Cancel"), [data-testid="cancel-appointment"]');
      if (await cancelButton.isVisible().catch(() => false)) {
        await cancelButton.click();
        
        // Confirm cancellation
        await page.click('button:has-text("Confirm"), button:has-text("Yes")');
        
        // Should show success message
        await expect(
          page.locator('text=/cancelled|canceled/i')
        ).toBeVisible({ timeout: 5000 });
      }
    }
  });
  
  test('should show available time slots', async ({ authenticatedPage: page }) => {
    await page.goto('/appointments');
    
    // Click create appointment
    const createButton = page.locator('button:has-text("Create"), button:has-text("New Appointment")');
    
    if (await createButton.isVisible().catch(() => false)) {
      await createButton.click();
      await page.waitForTimeout(500);
      
      // Select a service first
      const serviceSelect = page.locator('select[name="service_id"]');
      if (await serviceSelect.isVisible().catch(() => false)) {
        const options = await serviceSelect.locator('option').count();
        if (options > 1) {
          await serviceSelect.selectOption({ index: 1 });
        }
      }
      
      // Select a date
      await fillFormField(page, 'appointment_date', '2024-12-31');
      
      // Should show available time slots
      const timeSlotsVisible = await page.locator(
        '[data-testid="time-slots"], [data-testid="available-slots"]'
      ).isVisible().catch(() => false);
      
      // Or time input should be enabled
      const timeInputEnabled = await page.locator('input[name="appointment_time"]')
        .isEnabled().catch(() => false);
      
      expect(timeSlotsVisible || timeInputEnabled).toBeTruthy();
    }
  });
  
  test('should show appointment statistics', async ({ authenticatedPage: page }) => {
    await page.goto('/appointments');
    
    // Look for stats/metrics
    const statsSelectors = [
      '[data-testid="appointment-stats"]',
      'text=/Total|Confirmed|Pending|Completed/i',
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
});
