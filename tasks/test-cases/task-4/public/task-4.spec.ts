import { test, expect } from '@playwright/test';

test('Task 4 Public: Contact support form validation and submission', async ({ page }) => {
  test.setTimeout(60000);

  // 1. Navigate to Contact Support page
  await page.goto('http://localhost:5173/support');
  await page.waitForSelector('[data-testid="contact-name"]', { state: 'visible' });

  // 2. Submit empty form and verify errors
  await page.getByRole('button', { name: /send message/i }).click();
  
  // Wait for errors to appear
  await expect(page.getByTestId('field-error').first()).toBeVisible();
  
  // Verify specific required errors exist (count should be 4: name, email, subject, message)
  const errorCount = await page.getByTestId('field-error').count();
  expect(errorCount).toBeGreaterThanOrEqual(4);

  // 3. Test Invalid Email
  await page.getByTestId('contact-name').fill('John Doe');
  await page.getByTestId('contact-email').fill('invalid-email');
  await page.getByTestId('contact-subject').fill('Help');
  await page.getByTestId('contact-message').fill('This is a long enough message to pass length validation.');
  
  await page.getByRole('button', { name: /send message/i }).click();
  
  // Check for email specific error
  const emailError = page.locator('[data-testid="contact-email"] + [data-testid="field-error"]');
  await expect(emailError).toBeVisible();
  expect(await emailError.textContent()).toContain('valid email');

  // 4. Test Valid Submission
  await page.getByTestId('contact-email').fill('john.doe@example.com');
  
  // Ensure message length is valid (already filled above)
  const msgLength = await page.getByTestId('contact-message').inputValue();
  expect(msgLength.length).toBeGreaterThanOrEqual(10);
  expect(msgLength.length).toBeLessThanOrEqual(500);

  await page.getByRole('button', { name: /send message/i }).click();

  // 5. Verify Success
  await expect(page.getByTestId('submit-success')).toBeVisible({ timeout: 10000 });
  expect(await page.getByTestId('submit-success').textContent()).toContain('successfully');

  // 6. Verify Form Cleared
  expect(await page.getByTestId('contact-name').inputValue()).toBe('');
  expect(await page.getByTestId('contact-email').inputValue()).toBe('');
  expect(await page.getByTestId('contact-subject').inputValue()).toBe('');
  expect(await page.getByTestId('contact-message').inputValue()).toBe('');

  // 7. Verify Accessibility (Guest vs Auth) - Already tested as guest by default
  // Optional: Login and test again to ensure it still works for auth users
});