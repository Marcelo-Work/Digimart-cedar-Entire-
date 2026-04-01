import { test, expect } from '@playwright/test';

test('Task 7 Public: Vendor Dashboard CRUD', async ({ page }) => {
  test.setTimeout(120000);

  // 1. Login as Vendor
  await page.goto('http://localhost:5173/login');
  await page.getByTestId('email-input').fill('vendor@public.com');
  await page.getByTestId('password-input').fill('VendorPass123!');
  await page.getByTestId('login-button').click();
  await page.waitForLoadState('networkidle');

  // 2. Navigate to Dashboard
  await page.goto('http://localhost:5173/vendor/dashboard');
  await expect(page.locator('[data-testid="add-product-btn"]')).toBeVisible({ timeout: 10000 }); 
  // Note: If your button text is "Add Product", use locator('button:has-text("Add Product")') instead of testid if not added explicitly.
  // Let's assume the button in form acts as add. Or add data-testid="add-product-btn" to the submit button in Svelte when !isEditing.

  // 3. Verify Product List
  await expect(page.locator('[data-testid="vendor-product-list"]')).toBeVisible();

  // 4. Add Product
  await page.locator('input[placeholder="Title"]').fill('Test Product');
  await page.locator('textarea').fill('Test Desc');
  await page.locator('input[type="number"]').fill('99');
  await page.locator('button:has-text("Add Product")').click();
  await page.waitForTimeout(2000);
  
  // Verify persistence
  await page.reload();
  await expect(page.locator('text=Test Product')).toBeVisible();

  // 5. Edit Product
  await page.locator('[data-testid="edit-product"]').first().click();
  await page.locator('input[placeholder="Title"]').fill('Edited Product');
  await page.locator('button:has-text("Update Product")').click();
  await page.waitForTimeout(2000);
  await expect(page.locator('text=Edited Product')).toBeVisible();

  // 6. Delete Product
  await page.locator('[data-testid="delete-product"]').first().click();
  await page.waitForTimeout(1000); // Wait for confirm dialog acceptance (handled in code)
  await expect(page.locator('text=Edited Product')).not.toBeVisible();
});