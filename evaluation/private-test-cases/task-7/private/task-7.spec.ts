import { test, expect } from '@playwright/test';

test('Task 7 Private: Role Based Access Control', async ({ page }) => {
  test.setTimeout(120000);

  // 1. Customer tries to access Vendor Dashboard
  await page.goto('http://localhost:5173/login');
  await page.getByTestId('email-input').fill('customer@public.com');
  await page.getByTestId('password-input').fill('PublicPass123!');
  await page.getByTestId('login-button').click();
  await page.waitForLoadState('networkidle');

  await page.goto('http://localhost:5173/vendor/dashboard');
  // Should show Access Denied or redirect
  await expect(page.locator('text=Access Denied')).toBeVisible({ timeout: 10000 });

  // 2. API Check (Customer trying to call Vendor API)
  const res = await page.request.get('http://localhost:3000/api/vendor/products/');
  expect(res.status()).toBe(403); // Or 401 depending on auth flow

  // 3. Admin Access (View Only)
  // Login as Admin, verify can see list but Edit/Delete buttons might be disabled or fail for non-owned products
  // (Implementation dependent on specific criteria nuance)
});