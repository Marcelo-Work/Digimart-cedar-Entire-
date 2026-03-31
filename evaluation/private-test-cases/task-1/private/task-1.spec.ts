import { test, expect } from '@playwright/test';

test('Task 1 Private: Global Search finds private product', async ({ page }) => {
  test.setTimeout(60000);
  
  await page.goto('http://localhost:5173/');
  await page.waitForSelector('[data-testid="search-input"]', { state: 'visible', timeout: 10000 });
  
  const searchInput = page.getByTestId('search-input');
  await expect(searchInput).toBeVisible();

  await searchInput.fill('Private Gaming Mouse');
  await page.getByTestId('search-button').click();
  
  await page.waitForSelector('[data-testid="product-card"]', { state: 'visible', timeout: 10000 });

  await expect(
    page.getByRole('heading', { name: 'Private Gaming Mouse' })
  ).toBeVisible();
  
  const cards = page.getByTestId('product-card');
  const count = await cards.count();
  expect(count).toBeGreaterThanOrEqual(1);
});