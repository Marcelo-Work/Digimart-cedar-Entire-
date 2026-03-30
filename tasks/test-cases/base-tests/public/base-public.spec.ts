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
  
 
  await page.waitForSelector('[data-testid="product-card"]', { 
    state: 'visible',
    timeout: 10000 
  });
  

  const cards = page.locator('[data-testid="product-card"]');
  const count = await cards.count();
  expect(count).toBeGreaterThanOrEqual(3);

  await expect(
    page.getByRole('heading', { name: 'Premium Wireless Headphones' })
  ).toBeVisible();
});