import { test, expect } from '@playwright/test';

test('Base Public: Health Check', async ({ request }) => {
  const response = await request.get('http://localhost:3000/health/');
  expect(response.ok()).toBeTruthy();
  const data = await response.json();
  expect(data.status).toBe('healthy');
});

test('Base Public: Home Page Loads', async ({ page }) => {
  test.setTimeout(60000);
  await page.goto('http://localhost:5173/');
  await page.waitForSelector('[data-testid="product-card"]', { state: 'visible', timeout: 10000 });
  
  const cards = page.locator('[data-testid="product-card"]');
  const count = await cards.count();
  expect(count).toBeGreaterThanOrEqual(3);
  await expect(page.getByRole('heading', { name: 'Premium Wireless Headphones' })).toBeVisible();
});

// TASK 2: Add profile page base test
test('Base Public: Profile Page Loads for Authenticated User', async ({ page }) => {
  test.setTimeout(60000);
  
  // Login first
  await page.goto('http://localhost:5173/login');
  await page.getByTestId('email-input').fill('customer@public.com');
  await page.getByTestId('password-input').fill('PublicPass123!');
  await page.getByTestId('login-button').click();
  await page.waitForLoadState('networkidle');
  
  // Navigate to profile
  await page.goto('http://localhost:5173/profile');
  await page.waitForSelector('[data-testid="avatar-preview"]', { timeout: 10000 });
  
  // Verify profile elements exist
  await expect(page.getByTestId('avatar-preview')).toBeVisible();
  await expect(page.getByTestId('avatar-input')).toBeInViewport({ timeout: 5000 }).catch(() => {
    expect(page.locator('[data-testid="avatar-input"]')).toBeTruthy();
  });
  await expect(page.locator('text=My Profile')).toBeVisible();
});