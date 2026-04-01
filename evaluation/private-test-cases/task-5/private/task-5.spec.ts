import { test, expect } from '@playwright/test';

test('Task 5 Public: Discount coupon application at checkout', async ({ page }) => {
  test.setTimeout(120000); // Increase timeout to 2 minutes

  // -------------------------------------------------------------------------
  // Step 1: Login
  // -------------------------------------------------------------------------
  await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle' });
  
  await page.getByTestId('email-input').fill('customer@public.com');
  await page.getByTestId('password-input').fill('PublicPass123!');
  await page.getByTestId('login-button').click();
  
  // Wait for dashboard or home redirect
  await page.waitForURL(/\/(dashboard|home)/, { timeout: 10000 });
  await page.waitForLoadState('networkidle');

  // -------------------------------------------------------------------------
  // Step 2: Go to Home and Ensure Products Load
  // -------------------------------------------------------------------------
  await page.goto('http://localhost:5173/', { waitUntil: 'networkidle' });
  
  // Wait specifically for the add-to-cart button to be visible
  const addToCartBtn = page.locator('[data-testid="add-to-cart-button"]').first();
  await expect(addToCartBtn).toBeVisible({ timeout: 15000 });

  // Click Add to Cart
  await addToCartBtn.click();
  
  // Wait for success alert or network response
  await page.waitForEvent('dialog', { timeout: 5000 }).then(dialog => dialog.accept()).catch(() => {});
  await page.waitForTimeout(2000); // Allow cart API to settle

  // -------------------------------------------------------------------------
  // Step 3: Navigate to Cart
  // -------------------------------------------------------------------------
  await page.goto('http://localhost:5173/cart', { waitUntil: 'networkidle' });
  
  // Verify cart has content (wait for total)
  const cartTotalLocator = page.getByTestId('cart-total');
  await expect(cartTotalLocator).toBeVisible({ timeout: 15000 });
  
  const initialTotalText = await cartTotalLocator.textContent();
  const initialTotal = parseFloat(initialTotalText?.replace(/[^0-9.-]+/g, '') || '0');
  
  if (initialTotal === 0) {
    console.error("❌ Cart total is 0. Items might not have been added.");
    // Optional: Take screenshot for debugging
    await page.screenshot({ path: 'test-results/empty-cart.png' });
  }
  expect(initialTotal).toBeGreaterThan(0);

  // -------------------------------------------------------------------------
  // Step 4: Apply Valid Coupon (WELCOME10)
  // -------------------------------------------------------------------------
  const couponInput = page.getByTestId('coupon-input');
  await couponInput.fill('WELCOME10');
  
  const applyBtn = page.getByTestId('coupon-apply');
  await applyBtn.click();
  
  // Wait for discount to appear
  const discountLocator = page.getByTestId('discount-amount');
  await expect(discountLocator).toBeVisible({ timeout: 10000 });
  
  const discountText = await discountLocator.textContent();
  expect(discountText).toContain('-');
  
  const newTotalText = await cartTotalLocator.textContent();
  const newTotal = parseFloat(newTotalText?.replace(/[^0-9.-]+/g, '') || '0');
  expect(newTotal).toBeLessThan(initialTotal);

  // -------------------------------------------------------------------------
  // Step 5: Test Invalid Coupon
  // -------------------------------------------------------------------------
  // Remove current coupon first
  const removeBtn = page.locator('button:has-text("Remove")');
  if (await removeBtn.isVisible()) {
    await removeBtn.click();
    await page.waitForTimeout(1000);
    await expect(discountLocator).not.toBeVisible();
  }

  await couponInput.fill('INVALIDCODEXYZ');
  await applyBtn.click();
  
  const errorLocator = page.getByTestId('coupon-error');
  await expect(errorLocator).toBeVisible({ timeout: 5000 });
  const errorText = await errorLocator.textContent();
  expect(errorText?.toLowerCase()).toContain('invalid');

  // -------------------------------------------------------------------------
  // Step 6: Remove Coupon & Verify Revert
  // -------------------------------------------------------------------------
  // Re-apply valid
  await couponInput.fill('WELCOME10');
  await applyBtn.click();
  await expect(discountLocator).toBeVisible();
  
  const discountedTotal = parseFloat((await cartTotalLocator.textContent())?.replace(/[^0-9.-]+/g, '') || '0');
  
  // Remove
  await page.locator('button:has-text("Remove")').click();
  await page.waitForTimeout(1000);
  
  await expect(discountLocator).not.toBeVisible();
  
  const revertedTotal = parseFloat((await cartTotalLocator.textContent())?.replace(/[^0-9.-]+/g, '') || '0');
  expect(revertedTotal).toBeGreaterThanOrEqual(initialTotal * 0.98); // Allow small float variance
});