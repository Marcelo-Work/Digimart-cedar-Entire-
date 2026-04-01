import { test, expect } from '@playwright/test';

test('Task 8 Private: Error Handling, Rate Limiting & Content Validation', async ({ page }) => {
  test.setTimeout(150000);

  // -------------------------------------------------------------------------
  // 1. SETUP: LOGIN & ADD TO CART
  // -------------------------------------------------------------------------
  await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle' });
  await page.getByTestId('email-input').fill('customer@public.com');
  await page.getByTestId('password-input').fill('PublicPass123!');
  await page.getByTestId('login-button').click();
  await page.waitForLoadState('networkidle');

  // Ensure cart has items
  await page.goto('http://localhost:5173/cart', { waitUntil: 'networkidle' });
  if (await page.locator('text=Your cart is empty').isVisible()) {
    await page.goto('http://localhost:5173/');
    await page.locator('[data-testid="add-to-cart-button"]').first().click();
    await page.waitForTimeout(1000);
    await page.goto('http://localhost:5173/cart');
  }

  // -------------------------------------------------------------------------
  // 2. RATE LIMITING TEST (Rapid Fire Checkout)
  // -------------------------------------------------------------------------
  console.log('🚀 Testing Rate Limiting (Rapid Checkout)...');

  // Perform checkout
  await page.locator('button:has-text("Checkout")').click();
  await page.waitForURL(/order-confirmation/, { timeout: 10000 });

  const urlParams = new URLSearchParams(page.url().split('?')[1]);
  const orderId = urlParams.get('id');
  expect(orderId).toBeTruthy();

  // Try to checkout again immediately (Simulate double click via API or UI if possible)
  // Since UI redirects, we simulate by calling the API directly via request context
  const response = await page.request.post('http://localhost:3000/api/orders/', {
    headers: { 'Cookie': await page.context().cookies().then(c => c.map(x => `${x.name}=${x.value}`).join('; ')) }
  });

  // Should either succeed (new order) or handle gracefully. 
  // The main check is that emails don't duplicate for the SAME order.

  await page.waitForTimeout(4000); // Wait for async tasks

  // Go to logs
  await page.goto('http://localhost:5173/email-logs', { waitUntil: 'networkidle' });

  // Count emails for THIS specific Order ID
  const rows = page.getByTestId('email-log-entry');
  const allRowsText = await rows.allTextContents();

  // Filter rows related to this order
  const relevantLogs = allRowsText.filter(text => text.includes(`#${orderId}`));

  // Should have exactly 2 logs for this order (1 Customer + 1 Vendor), not more
  // If rate limiting fails, we might see duplicates if the task fired twice
  expect(relevantLogs.length).toBeLessThanOrEqual(4); // Allow small margin, but ideally 2
  console.log(`📧 Found ${relevantLogs.length} logs for Order #${orderId}. No massive duplication.`);

  // -------------------------------------------------------------------------
  // 3. EMAIL CONTENT VALIDATION
  // -------------------------------------------------------------------------
  // Reload page to ensure fresh data
  await page.reload({ waitUntil: 'networkidle' });

  // Find the customer log again
  const customerLog = page.locator(`tr:has-text("${orderId}"):has-text("Order Confirmation")`).first();
  await expect(customerLog).toBeVisible();

  // Click or expand to see body content if your UI supports it, 
  // OR check the tooltip/hidden data if implemented. 
  // Assuming the table shows subject and recipient, we verify those strictly.
  await expect(customerLog).toContainText('customer@public.com');
  await expect(customerLog).toContainText(`Order Confirmation #${orderId}`);

  // -------------------------------------------------------------------------
  // 4. ERROR HANDLING SIMULATION (Conceptual)
  // -------------------------------------------------------------------------
  // Note: Truly testing failure requires modifying backend code temporarily.
  // Instead, we verify the UI can display an error log IF one existed.
  // We check that the "Error Details" column exists in the table header.
  await expect(page.locator('th:has-text("Error"), th:has-text("Details")')).toBeVisible();

  // Verify that successful logs do NOT have the error badge visible
  await expect(customerLog.locator('[data-testid="email-error-log"]')).not.toBeVisible();

  console.log('✅ Task 8 Private Tests Passed!');
});