test('Task 9 Public: Guest Checkout Flow', async ({ page }) => {
    test.setTimeout(120000);

    // 1. Add to Cart as Guest
    await page.goto('http://localhost:5173/');
    await page.locator('[data-testid="add-to-cart-button"]').first().click();
    await page.waitForTimeout(1000);

    // 2. Go to Cart
    await page.goto('http://localhost:5173/cart');

    // 3. Click Guest Checkout
    await page.locator('[data-testid="guest-checkout"], button:has-text("Guest")').click();

    // 4. Fill Form
    await page.fill('input[type="email"]', 'guest@test.com');
    await page.fill('input[type="text"]', 'Guest User');
    await page.fill('textarea', '123 Test St');
    await page.fill('input[placeholder="City"]', 'Test City');
    await page.fill('input[placeholder="ZIP"]', '12345');

    await page.locator('[data-testid="guest-form"] button[type="submit"]').click();

    // 5. Verify Success
    await page.waitForURL(/guest\/(success|track)/);
    await expect(page.getByTestId('order-lookup')).toBeVisible({ timeout: 15000 });

    // 6. Verify Email Log
    await page.waitForTimeout(3000);
    await page.goto('http://localhost:5173/email-logs');
    await expect(page.locator('text=guest@test.com')).toBeVisible();
});