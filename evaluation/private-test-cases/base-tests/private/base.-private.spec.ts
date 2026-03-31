import { test, expect } from '@playwright/test';

test('Base Private: Health Check', async ({ request }) => {
  const response = await request.get('http://localhost:3000/health/');
  expect(response.ok()).toBeTruthy();
  const data = await response.json();
  expect(data.status).toBe('healthy');
});

test('Base Private: Home Page Loads', async ({ page }) => {
  test.setTimeout(60000);
  await page.goto('http://localhost:5173/');
  await page.waitForSelector('[data-testid="product-card"]', { state: 'visible', timeout: 10000 });
  
  const cards = page.locator('[data-testid="product-card"]');
  const count = await cards.count();
  expect(count).toBeGreaterThanOrEqual(3);
  await expect(page.getByRole('heading', { name: 'Private Gaming Mouse' })).toBeVisible();
});

// TASK 2: Private profile test
test('Base Private: Profile Page Loads for Authenticated Private User', async ({ page }) => {
  test.setTimeout(60000);
  
  await page.goto('http://localhost:5173/login');
  await page.getByTestId('email-input').fill('customer@private.com');
  await page.getByTestId('password-input').fill('PrivateCustomerPass99!');
  await page.getByTestId('login-button').click();
  await page.waitForLoadState('networkidle');
  
  await page.goto('http://localhost:5173/profile');
  await page.waitForSelector('[data-testid="avatar-preview"]', { timeout: 10000 });
  
  await expect(page.getByTestId('avatar-preview')).toBeVisible();
  await expect(page.getByTestId('avatar-input')).toBeVisible();
  await expect(page.locator('text=My Profile')).toBeVisible();
});