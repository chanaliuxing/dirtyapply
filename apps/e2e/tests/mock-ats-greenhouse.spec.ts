import { test, expect } from '@playwright/test';

/**
 * E2E Tests for Greenhouse-style ATS Mock
 * Tests complete application flow from job analysis to form submission
 */

test.describe('Greenhouse ATS Mock - Complete Application Flow', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to Greenhouse mock page
    await page.goto('/mock-ats/greenhouse');
    
    // Wait for page to load completely
    await page.waitForLoadState('networkidle');
  });
  
  test('should display Greenhouse application form', async ({ page }) => {
    // Test: Page loads and displays expected elements
    await expect(page).toHaveTitle(/greenhouse/i);
    
    // Check for key form elements
    await expect(page.locator('input[name="firstName"]')).toBeVisible();
    await expect(page.locator('input[name="lastName"]')).toBeVisible();
    await expect(page.locator('input[name="email"]')).toBeVisible();
    await expect(page.locator('input[name="phone"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });
  
  test('should validate required fields', async ({ page }) => {
    // Test: Form validation works correctly
    
    // Try to submit empty form
    await page.click('button[type="submit"]');
    
    // Should show validation errors
    await expect(page.locator('.error-message')).toHaveCount({ min: 1 });
    
    // Or check for HTML5 validation
    const firstNameInput = page.locator('input[name="firstName"]');
    await expect(firstNameInput).toHaveAttribute('required');
  });
  
  test('should fill form with valid data and submit successfully', async ({ page }) => {
    // Test: Complete application flow with valid data
    
    // Fill out the form
    await page.fill('input[name="firstName"]', 'Alex');
    await page.fill('input[name="lastName"]', 'Chen');
    await page.fill('input[name="email"]', 'alex.chen@email.com');
    await page.fill('input[name="phone"]', '+1-555-0123');
    
    // Fill additional fields if they exist
    const coverLetterField = page.locator('textarea[name="coverLetter"]');
    if (await coverLetterField.isVisible()) {
      await coverLetterField.fill('I am very interested in this Data Scientist position...');
    }
    
    // Handle file upload if present
    const fileInput = page.locator('input[type="file"]');
    if (await fileInput.isVisible()) {
      // In a real test, you'd upload a test resume file
      // await fileInput.setInputFiles('path/to/test-resume.pdf');
    }
    
    // Submit the form
    await page.click('button[type="submit"]');
    
    // Wait for submission to complete
    await page.waitForLoadState('networkidle');
    
    // Verify success message appears
    await expect(page.locator('.success-message, .confirmation-message')).toBeVisible();
    await expect(page.getByText(/application submitted/i)).toBeVisible();
  });
  
  test('should handle form field detection for automation', async ({ page }) => {
    // Test: Field detection for automation compatibility
    
    const formFields = [
      'input[name="firstName"]',
      'input[name="lastName"]',
      'input[name="email"]',
      'input[name="phone"]'
    ];
    
    for (const selector of formFields) {
      const field = page.locator(selector);
      await expect(field).toBeVisible();
      
      // Check that field has proper labels or placeholders for automation
      const fieldId = await field.getAttribute('id');
      const fieldName = await field.getAttribute('name');
      const placeholder = await field.getAttribute('placeholder');
      
      // Should have at least one identifier
      expect(fieldId || fieldName || placeholder).toBeTruthy();
    }
  });
  
  test('should support keyboard navigation', async ({ page }) => {
    // Test: Accessibility and keyboard navigation
    
    // Tab through form fields
    await page.keyboard.press('Tab');
    await expect(page.locator('input[name="firstName"]')).toBeFocused();
    
    await page.keyboard.press('Tab');
    await expect(page.locator('input[name="lastName"]')).toBeFocused();
    
    await page.keyboard.press('Tab');
    await expect(page.locator('input[name="email"]')).toBeFocused();
  });
  
  test('should capture screenshots for visual regression testing', async ({ page }) => {
    // Test: Visual regression testing
    
    // Take screenshot of initial form
    await expect(page).toHaveScreenshot('greenhouse-form-initial.png');
    
    // Fill some fields and take another screenshot
    await page.fill('input[name="firstName"]', 'Test');
    await page.fill('input[name="lastName"]', 'User');
    await expect(page).toHaveScreenshot('greenhouse-form-filled.png');
  });
  
  test('should measure form completion performance', async ({ page }) => {
    // Test: Performance measurement
    
    const startTime = Date.now();
    
    // Fill form quickly
    await page.fill('input[name="firstName"]', 'Speed');
    await page.fill('input[name="lastName"]', 'Test');
    await page.fill('input[name="email"]', 'speed@test.com');
    await page.fill('input[name="phone"]', '555-0123');
    
    const fillTime = Date.now() - startTime;
    
    // Should fill form reasonably quickly (under 2 seconds for automation)
    expect(fillTime).toBeLessThan(2000);
    
    console.log(`Form fill time: ${fillTime}ms`);
  });
});

test.describe('Greenhouse ATS Mock - Integration with API', () => {
  
  test('should generate job analysis via API', async ({ page, request }) => {
    // Test: Integration between UI and API
    
    // First, extract job description from the page
    await page.goto('/mock-ats/greenhouse');
    
    const jobDescription = await page.locator('.job-description, .job-details').textContent();
    
    if (jobDescription) {
      // Send to API for analysis
      const response = await request.post('http://localhost:8000/api/jtr', {
        data: {
          job_description: jobDescription,
          resume_profile: {
            name: 'Test User',
            skills: ['Python', 'SQL', 'Machine Learning']
          }
        }
      });
      
      expect(response.status()).toBe(200);
      
      const analysis = await response.json();
      expect(analysis).toHaveProperty('match_score');
      expect(analysis).toHaveProperty('analysis');
    }
  });
  
  test('should generate action plan for form filling', async ({ page, request }) => {
    // Test: Action plan generation
    
    await page.goto('/mock-ats/greenhouse');
    
    // Extract form fields
    const fields = await page.evaluate(() => {
      const inputs = Array.from(document.querySelectorAll('input, textarea, select'));
      return inputs.map(input => ({
        name: input.name || input.id,
        type: input.type,
        required: input.required,
        placeholder: input.placeholder
      }));
    });
    
    // Send to API for action plan generation
    const response = await request.post('http://localhost:8000/api/plan', {
      data: {
        fields: fields,
        page_context: 'greenhouse',
        url: page.url()
      }
    });
    
    expect(response.status()).toBe(200);
    
    const actionPlan = await response.json();
    expect(actionPlan).toHaveProperty('action_plan');
  });
});