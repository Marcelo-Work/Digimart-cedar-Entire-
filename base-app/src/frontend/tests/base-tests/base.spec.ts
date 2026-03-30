import { test, expect } from '@playwright/test';

test.describe('Base App Tests', () => {
  test('health endpoint returns 200', async ({ request }) => {
    const response = await request.get('/health');
    expect(response.status()).toBe(200);
    const json = await response.json();
    expect(json.status).toBe('healthy');
  });

  test('home page loads', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('text=DigiMart')).toBeVisible();
  });

  test('login page loads', async ({ page }) => {
    await page.goto('/login');
    await expect(page.locator('[data-testid="login-email"]')).toBeVisible();
  });

  test('signup page loads', async ({ page }) => {
    await page.goto('/signup');
    await expect(page.locator('text=Sign Up')).toBeVisible();
  });

  test('products load on home page', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('[data-testid="product-card"]')).toHaveCount({ min: 1 });
  });
});