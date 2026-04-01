import { test, expect } from '@playwright/test';

test('Task 6 Private: Review validation, purchase check, and average calculation', async ({ page }) => {
  test.setTimeout(150000);

  // -------------------------------------------------------------------------
  // PART 1: GUEST USER VALIDATION
  // -------------------------------------------------------------------------
  await page.context().clearCookies();
  await page.goto('http://localhost:5173/', { waitUntil: 'networkidle' });
  await page.evaluate(() => localStorage.clear());
  await page.reload({ waitUntil: 'networkidle' });
  
  // Click first product
  await page.locator('[data-testid="product-card"]').first().locator('button').first().click();
  await page.waitForURL(/\/product\?id=\d+/);
  
  // ✅ CRITICAL FIX: Wait for "Please login" text FIRST
  // This guarantees the component has finished loading and determined the user is a guest
  const loginPrompt = page.locator('text=Please login to write a review');
  await expect(loginPrompt).toBeVisible({ timeout: 20000 }); // Increased timeout

  // ✅ NOW verify stars are NOT visible
  // Since we confirmed the login prompt is there, the stars MUST be gone
  const stars = page.getByTestId('rating-stars');
  await expect(stars).not.toBeVisible({ timeout: 5000 });
  
  const textarea = page.locator('textarea');
  await expect(textarea).not.toBeVisible();

  // -------------------------------------------------------------------------
  // PART 2: PURCHASE VALIDATION (Admin)
  // -------------------------------------------------------------------------
  await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle' });
  await page.getByTestId('email-input').fill('admin@public.com');
  await page.getByTestId('password-input').fill('AdminPass123!');
  await page.getByTestId('login-button').click();
  await page.waitForLoadState('networkidle');

  await page.goto('http://localhost:5173/', { waitUntil: 'networkidle' });
  await page.locator('[data-testid="product-card"]').first().locator('button').first().click();
  await page.waitForURL(/\/product\?id=\d+/);
  await page.waitForSelector('[data-testid="review-section"]', { timeout: 15000 });

  const adminStars = page.getByTestId('rating-stars').locator('span');
  await adminStars.nth(4).click();
  await page.locator('textarea').fill('I am an admin testing this.');
  await page.locator('button:has-text("Submit Review")').click();

  await expect(page.locator('.alert-danger')).toBeVisible({ timeout: 10000 });
  const purchaseError = await page.locator('.alert-danger').textContent();
  expect(purchaseError?.toLowerCase()).toContain('purchased');

  // -------------------------------------------------------------------------
  // PART 3: AVERAGE RECALCULATION (Customer)
  // -------------------------------------------------------------------------
  await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle' });
  await page.getByTestId('email-input').fill('customer@public.com');
  await page.getByTestId('password-input').fill('PublicPass123!');
  await page.getByTestId('login-button').click();
  await page.waitForLoadState('networkidle');

  await page.goto('http://localhost:5173/', { waitUntil: 'networkidle' });
  await page.locator('[data-testid="product-card"]').first().locator('button').first().click();
  await page.waitForURL(/\/product\?id=\d+/);
  await page.waitForSelector('[data-testid="review-section"]', { timeout: 15000 });

  const custStars = page.getByTestId('rating-stars').locator('span');
  await custStars.nth(4).click(); 
  await page.locator('textarea').fill('Perfect product! Giving it 5 stars.');
  await page.locator('button:has-text("Submit Review")').click();

  await expect(page.locator('.alert-success')).toBeVisible({ timeout: 10000 });
  await page.waitForTimeout(1500);

  const avgText = await page.getByTestId('average-rating').textContent();
  expect(avgText).toContain('5'); 

  await expect(page.getByTestId('review-item').first()).toBeVisible();
});