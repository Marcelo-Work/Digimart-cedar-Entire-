import { test, expect } from '@playwright/test';

test('Task 4 Private: Contact form boundary validation and authenticated access', async ({ page }) => {
  test.setTimeout(60000);

  await page.goto('http://localhost:5173/support');
  await page.waitForSelector('[data-testid="contact-name"]');

  // 1. Test Message Length < 10 chars
  await page.getByTestId('contact-name').fill('User');
  await page.getByTestId('contact-email').fill('user@test.com');
  await page.getByTestId('contact-subject').fill('Test');
  await page.getByTestId('contact-message').fill('Short'); // 5 chars
  
  await page.getByRole('button', { name: /send message/i }).click();
  
  const shortMsgError = page.locator('[data-testid="contact-message"] + [data-testid="field-error"]');
  await expect(shortMsgError).toBeVisible();
  expect(await shortMsgError.textContent()).toContain('10 characters');

  // 2. Test Message Length > 500 chars
  const longMessage = 'a'.repeat(501);
  await page.getByTestId('contact-message').fill(longMessage);
  
  await page.getByRole('button', { name: /send message/i }).click();
  
  const longMsgError = page.locator('[data-testid="contact-message"] + [data-testid="field-error"]');
  await expect(longMsgError).toBeVisible();
  expect(await longMsgError.textContent()).toContain('500 characters');

  // 3. Test Authenticated User Access
  await page.goto('http://localhost:5173/login');
  await page.getByTestId('email-input').fill('customer@public.com');
  await page.getByTestId('password-input').fill('PublicPass123!');
  await page.getByTestId('login-button').click();
  await page.waitForLoadState('networkidle');

  await page.goto('http://localhost:5173/support');
  await expect(page.getByTestId('contact-name')).toBeVisible(); // Form should still be accessible
  
  // Submit as auth user
  await page.getByTestId('contact-name').fill('Authenticated User');
  await page.getByTestId('contact-email').fill('auth@user.com');
  await page.getByTestId('contact-subject').fill('Auth Test');
  await page.getByTestId('contact-message').fill('This is a valid message from an authenticated user.');
  
  await page.getByRole('button', { name: /send message/i }).click();
  await expect(page.getByTestId('submit-success')).toBeVisible();
});