import { test, expect } from '@playwright/test';

test('Task 5 Public: Discount coupon application at checkout', async ({ page }) => {
  test.setTimeout(120000); // 2 minutes total timeout

  // -------------------------------------------------------------------------
  // 1. LOGIN
  // -------------------------------------------------------------------------
  await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle' });
  await page.getByTestId('email-input').fill('customer@public.com');
  await page.getByTestId('password-input').fill('PublicPass123!');
  await page.getByTestId('login-button').click();
  await page.waitForLoadState('networkidle');

  // -------------------------------------------------------------------------
  // 2. ADD ITEM TO CART
  // -------------------------------------------------------------------------
  await page.goto('http://localhost:5173/', { waitUntil: 'networkidle' });
  
  // Wait for products to load
  const productCard = page.locator('[data-testid="product-card"]').first();
  await expect(productCard).toBeVisible({ timeout: 20000 });

  // Click "View Details" (or whatever the first button is)
  await productCard.locator('button').first().click();
  
  // Wait for Product Detail Page to load
  await page.waitForURL(/\/product\?id=\d+/);
  await page.waitForLoadState('networkidle');

  // Find "Add to Cart" button by text content (more reliable than testid if missing)
  const addToCartBtn = page.locator('button:has-text("Add to Cart"), button:has-text("add to cart")');
  await expect(addToCartBtn).toBeVisible({ timeout: 10000 });

  // Handle the Alert Dialog explicitly
  let alertMessage = '';
  page.once('dialog', async (dialog) => {
    alertMessage = dialog.message();
    await dialog.accept(); // Click OK
  });

  await addToCartBtn.click();
  
  // Wait for the dialog to be processed
  await page.waitForTimeout(1500); 

  // Check if the alert indicated failure
  if (alertMessage.includes('Failed') || alertMessage.includes('error')) {
    console.error('❌ UI reported failure:', alertMessage);
    // Take a screenshot for debugging
    await page.screenshot({ path: 'test-results/add-to-cart-failure.png' });
    throw new Error(`Add to cart failed in test: ${alertMessage}. Check backend CSRF or logs.`);
  }

  // -------------------------------------------------------------------------
  // 3. NAVIGATE TO CART & VERIFY CONTENT
  // -------------------------------------------------------------------------
  await page.goto('http://localhost:5173/cart', { waitUntil: 'networkidle' });
  
  // DEBUG: Screenshot of cart page
  await page.screenshot({ path: 'test-results/cart-page-loaded.png' });

  // Check if cart is empty (sometimes happens if session didn't persist)
  const emptyText = page.locator('text=Your cart is empty');
  if (await emptyText.isVisible({ timeout: 5000 })) {
    console.error('❌ Cart is empty in test despite successful add.');
    throw new Error('Cart is empty. Session/Cookie issue in test environment?');
  }

  // Wait for Cart Total to appear
  const cartTotal = page.getByTestId('cart-total');
  await expect(cartTotal).toBeVisible({ timeout: 15000 });
  
  const initialTotalStr = await cartTotal.textContent();
  const initialTotal = parseFloat(initialTotalStr?.replace(/[^0-9.-]+/g, '') || '0');
  
  if (initialTotal === 0) {
    throw new Error('Cart total is $0. Items not added correctly.');
  }

  // -------------------------------------------------------------------------
  // 4. APPLY VALID COUPON
  // -------------------------------------------------------------------------
  const couponInput = page.getByTestId('coupon-input');
  const applyBtn = page.getByTestId('coupon-apply');
  
  await couponInput.fill('WELCOME10');
  await applyBtn.click();
  
  // Wait for Discount Amount to appear
  const discountAmount = page.getByTestId('discount-amount');
  await expect(discountAmount).toBeVisible({ timeout: 10000 });
  
  const newTotalStr = await cartTotal.textContent();
  const newTotal = parseFloat(newTotalStr?.replace(/[^0-9.-]+/g, '') || '0');
  
  expect(newTotal).toBeLessThan(initialTotal);

  // -------------------------------------------------------------------------
  // 5. TEST INVALID COUPON
  // -------------------------------------------------------------------------
  // Remove current coupon
  const removeBtn = page.locator('button:has-text("Remove"), button:has-text("remove")');
  if (await removeBtn.isVisible()) {
    await removeBtn.click();
    await page.waitForTimeout(1000);
  }
  
  // Ensure discount disappeared
  await expect(discountAmount).not.toBeVisible({ timeout: 5000 });

  // Try invalid code
  await couponInput.fill('INVALID_CODE_123');
  await applyBtn.click();
  
  const errorMsg = page.getByTestId('coupon-error');
  await expect(errorMsg).toBeVisible({ timeout: 5000 });
  const errorText = await errorMsg.textContent();
  expect(errorText?.toLowerCase()).toContain('invalid');

  // -------------------------------------------------------------------------
  // 6. CLEANUP: REMOVE COUPON
  // -------------------------------------------------------------------------
  // Re-apply valid to test removal
  await couponInput.fill('WELCOME10');
  await applyBtn.click();
  await expect(discountAmount).toBeVisible();
  
  await removeBtn.click();
  await page.waitForTimeout(1000);
  
  await expect(discountAmount).not.toBeVisible();
});