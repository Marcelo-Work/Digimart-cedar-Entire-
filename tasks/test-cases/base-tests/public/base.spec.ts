import { test, expect } from '@playwright/test';

test.describe('Base App Public Tests', () => {
  test('health endpoint returns 200', async ({ request }) => {
    const response = await request.get('/health');
    expect(response.status()).toBe(200);
  });

  test('home page loads', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('text=DigiMart')).toBeVisible();
  });
});