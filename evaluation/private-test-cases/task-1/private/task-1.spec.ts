import { test, expect } from '@playwright/test';

test('Task 1 Private: Global Search finds private product', async ({ page }) => {
  await page.goto('http://localhost:5173/');
  //await page.waitForLoadState('networkidle');
  await page.waitForSelector('[data-testid="search-input"]', { timeout: 10000 });
  const searchInput = page.getByTestId('search-input');
  await expect(searchInput).toBeVisible();

  await searchInput.fill('Private Gaming Mouse');
  await page.getByTestId('search-button').click();
  await page.waitForLoadState('networkidle');

  await expect(page.getByRole('heading', { name: 'Private Gaming Mouse' })).toBeVisible();
  const cards = page.getByTestId('product-card');
  await expect(cards).toHaveCount(1);
});