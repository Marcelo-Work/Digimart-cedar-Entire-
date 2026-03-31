import { test, expect } from '@playwright/test';

test('Task 3 Private: Order history sorting and filtering works for private user', async ({ page }) => {
    test.setTimeout(90000);

    // -------------------------------------------------------------------------
    // Step 1: Login as Private User
    // -------------------------------------------------------------------------
    await page.goto('http://localhost:5173/login');
    await page.waitForSelector('[data-testid="email-input"]', { state: 'visible' });

    // Use PRIVATE credentials
    await page.getByTestId('email-input').fill('customer@private.com');
    await page.getByTestId('password-input').fill('PrivatePass123!');
    await page.getByTestId('login-button').click();

    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    // -------------------------------------------------------------------------
    // Step 2: Navigate to Orders Page
    // -------------------------------------------------------------------------
    await page.goto('http://localhost:5173/orders');

    // Check for table
    const hasTable = await page.locator('[data-testid="order-table"]').isVisible().catch(() => false);
    const hasNoOrders = await page.locator('[data-testid="no-orders-message"]').isVisible().catch(() => false);

    if (hasNoOrders && !hasTable) {
        console.log('⚠️ No orders found for private user. Ensure seed_private.py + create_test_orders.py were run.');
        expect(hasTable, 'Orders table should be visible.').toBeTruthy();
    }

    const orderTable = page.getByTestId('order-table');
    await expect(orderTable).toBeVisible();

    // Verify controls
    await expect(page.getByTestId('order-sort')).toBeVisible();
    await expect(page.getByTestId('order-direction')).toBeVisible();
    await expect(page.getByTestId('order-filter')).toBeVisible();

    // Get initial count
    const initialRows = page.getByTestId('order-row');
    const count = await initialRows.count();
    expect(count).toBeGreaterThan(0);

    // -------------------------------------------------------------------------
    // Step 3: Test Sorting by Status
    // -------------------------------------------------------------------------
    await page.getByTestId('order-sort').selectOption('status');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    // Verify rows still exist
    expect(await page.getByTestId('order-row').count()).toBe(count);

    // Change direction
    await page.getByTestId('order-direction').selectOption('asc');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    // -------------------------------------------------------------------------
    // Step 4: Test Filtering by 'pending'
    // -------------------------------------------------------------------------
    await page.getByTestId('order-filter').selectOption('pending');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    const pendingRows = page.getByTestId('order-row');
    const pendingCount = await pendingRows.count();

    expect(pendingCount).toBeLessThanOrEqual(count);

    // Verify all visible rows are 'pending'
    for (let i = 0; i < pendingCount; i++) {
        const statusBadge = pendingRows.nth(i).getByTestId('order-status');
        const text = await statusBadge.textContent();
        expect(text?.toLowerCase()).toContain('pending');
    }

    // Reset filter
    await page.getByTestId('order-filter').selectOption('');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    // Verify count returns
    expect(await page.getByTestId('order-row').count()).toBe(count);

    // -------------------------------------------------------------------------
    // Step 5: Verify Data Integrity (Amounts are visible)
    // -------------------------------------------------------------------------
    const firstRow = page.getByTestId('order-row').first();
    const amountCell = firstRow.getByTestId('order-amount');
    await expect(amountCell).toBeVisible();

    const amountText = await amountCell.textContent();
    expect(amountText).toContain('$');
});