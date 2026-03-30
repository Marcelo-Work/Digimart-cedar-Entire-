import { test, expect } from '@playwright/test';

test.describe('Base App Private Tests', () => {
  test('health endpoint returns 200', async ({ request }) => {
    const response = await request.get('/health');
    expect(response.status()).toBe(200);
  });

  test('home page loads with private seed', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('text=DigiMart')).toBeVisible();
    await expect(page.locator('[data-testid="product-card"]')).toHaveCount({ min: 1 });
  });
});