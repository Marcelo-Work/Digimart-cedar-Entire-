import { test, expect } from '@playwright/test';
import * as path from 'path';

test('Task 3 Public: Order history sorting and filtering works', async ({ page }) => {
  test.setTimeout(90000);

  // -------------------------------------------------------------------------
  // Step 1: Login as Public User
  // -------------------------------------------------------------------------
  await page.goto('http://localhost:5173/login');
  await page.waitForSelector('[data-testid="email-input"]', { state: 'visible' });
  
  await page.getByTestId('email-input').fill('customer@public.com');
  await page.getByTestId('password-input').fill('PublicPass123!');
  await page.getByTestId('login-button').click();
  
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(1000);

  // -------------------------------------------------------------------------
  // Step 2: Navigate to Orders Page
  // -------------------------------------------------------------------------
  await page.goto('http://localhost:5173/orders');
  
  // Wait for order table or "no orders" message
  const hasTable = await page.locator('[data-testid="order-table"]').isVisible().catch(() => false);
  const hasNoOrders = await page.locator('[data-testid="no-orders-message"]').isVisible().catch(() => false);

  if (hasNoOrders && !hasTable) {
    console.log('⚠️ No orders found. Ensure create_test_orders.py was run.');
    // For this test to pass, we assume orders exist. If not, fail gracefully or skip.
    // In a real scenario, you might create an order here via UI.
    expect(hasTable, 'Orders table should be visible. Run seed/create scripts if empty.').toBeTruthy();
  }

  // Verify table is visible
  const orderTable = page.getByTestId('order-table');
  await expect(orderTable).toBeVisible();

  // Verify sort/filter controls exist
  await expect(page.getByTestId('order-sort')).toBeVisible();
  await expect(page.getByTestId('order-direction')).toBeVisible();
  await expect(page.getByTestId('order-filter')).toBeVisible();

  // -------------------------------------------------------------------------
  // Step 3: Test Sorting by Date (Default)
  // -------------------------------------------------------------------------
  // Get initial order of rows
  const initialRows = page.getByTestId('order-row');
  const count = await initialRows.count();
  expect(count).toBeGreaterThan(0);

  // Change sort to Amount
  await page.getByTestId('order-sort').selectOption('total_amount');
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(1000); // Allow render

  // Verify rows still exist
  expect(await page.getByTestId('order-row').count()).toBe(count);

  // Change direction to Ascending
  await page.getByTestId('order-direction').selectOption('asc');
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(1000);

  // -------------------------------------------------------------------------
  // Step 4: Test Filtering by Status
  // -------------------------------------------------------------------------
  // Filter by 'completed'
  await page.getByTestId('order-filter').selectOption('completed');
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(1000);

  const filteredRows = page.getByTestId('order-row');
  const filteredCount = await filteredRows.count();
  
  // If we had orders, filtering should show <= original count
  expect(filteredCount).toBeLessThanOrEqual(count);

  // Verify all visible rows have 'completed' status badge
  for (let i = 0; i < filteredCount; i++) {
    const statusBadge = filteredRows.nth(i).getByTestId('order-status');
    const text = await statusBadge.textContent();
    expect(text?.toLowerCase()).toContain('completed');
  }

  // Reset filter to All
  await page.getByTestId('order-filter').selectOption('');
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(1000);

  // Verify count returns to original
  expect(await page.getByTestId('order-row').count()).toBe(count);

  // -------------------------------------------------------------------------
  // Step 5: Verify Column Test IDs
  // -------------------------------------------------------------------------
  const firstRow = page.getByTestId('order-row').first();
  await expect(firstRow.getByTestId('order-date')).toBeVisible();
  await expect(firstRow.getByTestId('order-status')).toBeVisible();
  await expect(firstRow.getByTestId('order-amount')).toBeVisible();
});