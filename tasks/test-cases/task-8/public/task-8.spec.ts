import { test, expect } from '@playwright/test';

test('Task 8 Public: Async Email Notifications & Logging', async ({ page }) => {
    test.setTimeout(120000);

    // -------------------------------------------------------------------------
    // 1. LOGIN & PREPARE CART
    // -------------------------------------------------------------------------
    await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle' });
    await page.getByTestId('email-input').fill('customer@public.com');
    await page.getByTestId('password-input').fill('PublicPass123!');
    await page.getByTestId('login-button').click();
    await page.waitForLoadState('networkidle');

    // Add item to cart if empty
    await page.goto('http://localhost:5173/', { waitUntil: 'networkidle' });
    const addToCartBtn = page.locator('[data-testid="add-to-cart-button"]').first();

    // Check if cart is empty by going to cart page first
    await page.goto('http://localhost:5173/cart', { waitUntil: 'networkidle' });
    const isEmpty = await page.locator('text=Your cart is empty').isVisible().catch(() => true);

    if (isEmpty) {
        await page.goto('http://localhost:5173/');
        await addToCartBtn.click();
        await page.waitForTimeout(1000);
        await page.goto('http://localhost:5173/cart');
    }

    // -------------------------------------------------------------------------
    // 2. CHECKOUT & PERFORMANCE TEST (< 2s)
    // -------------------------------------------------------------------------
    const startTime = Date.now();

    await page.locator('button:has-text("Checkout"), button:has-text("Place Order")').click();

    // Wait for navigation to confirmation page
    await page.waitForURL(/order-confirmation/, { timeout: 10000 });

    const endTime = Date.now();
    const duration = endTime - startTime;

    // ✅ ASSERTION: Response time must be under 2 seconds (Async check)
    expect(duration).toBeLessThan(2000);
    console.log(`⏱️ Checkout completed in ${duration}ms`);

    // -------------------------------------------------------------------------
    // 3. VERIFY ORDER CONFIRMATION PAGE
    // -------------------------------------------------------------------------
    // ✅ ASSERTION: Order Confirmed Element Exists
    await expect(page.getByTestId('order-confirmed')).toBeVisible({ timeout: 10000 });

    // Extract Order ID from URL or Page
    const urlParams = new URLSearchParams(page.url().split('?')[1]);
    const orderId = urlParams.get('id');
    expect(orderId).toBeTruthy();
    console.log(`✅ Order Created: #${orderId}`);

    // -------------------------------------------------------------------------
    // 4. VERIFY EMAIL LOGS (Wait for Async Processing)
    // -------------------------------------------------------------------------
    console.log('⏳ Waiting 3 seconds for background email task...');
    await page.waitForTimeout(3500); // Give background worker time to process

    // Navigate to Email Logs
    await page.goto('http://localhost:5173/email-logs', { waitUntil: 'networkidle' });

    // ✅ ASSERTION: Email Log Entries Exist
    const logEntries = page.getByTestId('email-log-entry');
    await expect(logEntries.first()).toBeVisible({ timeout: 15000 });

    // Count entries (Should be at least 2: Customer + Vendor)
    const count = await logEntries.count();
    expect(count).toBeGreaterThanOrEqual(2);
    console.log(`📧 Found ${count} email log entries.`);

    // -------------------------------------------------------------------------
    // 5. VERIFY EMAIL CONTENT DETAILS
    // -------------------------------------------------------------------------
    // Find the customer confirmation email log
    // We look for a row containing the Order ID and "Order Confirmation"
    const customerLogRow = page.locator(`tr:has-text("${orderId}"):has-text("Order Confirmation")`).first();
    await expect(customerLogRow).toBeVisible();

    // Verify Status is 'Sent'
    await expect(customerLogRow.locator('.bg-success, text=Sent')).toBeVisible();

    // Verify Recipient
    await expect(customerLogRow).toContainText('customer@public.com');

    // -------------------------------------------------------------------------
    // 6. VENDOR NOTIFICATION CHECK
    // -------------------------------------------------------------------------
    const vendorLogRow = page.locator(`tr:has-text("${orderId}"):has-text("Vendor")`).first();
    await expect(vendorLogRow).toBeVisible();
    await expect(vendorLogRow).toContainText('vendor@public.com');
    await expect(vendorLogRow.locator('.bg-success, text=Sent')).toBeVisible();

    console.log('✅ Task 8 Public Tests Passed!');
});