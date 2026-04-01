test('Task 9 Private: Security & Validation', async ({ page }) => {
  // 1. Test Invalid Email
  await page.goto('http://localhost:5173/guest/checkout');
  await page.fill('input[type="email"]', 'invalid-email');
  await page.click('button[type="submit"]');
  await expect(page.locator('[data-testid="guest-error"]')).toBeVisible();

  // 2. Test Dashboard Access (Should fail)
  await page.goto('http://localhost:5173/dashboard');
  await expect(page.locator('text=Login')).toBeVisible(); // Redirected

  // 3. Test ID Manipulation (Fake Token)
  await page.goto('http://localhost:5173/guest/track/fake-uuid-token');
  await expect(page.locator('text=not found')).toBeVisible();
});