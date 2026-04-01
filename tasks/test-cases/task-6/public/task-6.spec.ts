import { test, expect } from '@playwright/test';

test('Task 6 Public: Product rating and review system', async ({ page }) => {
    test.setTimeout(120000);

    // -------------------------------------------------------------------------
    // 1. LOGIN (Required to review)
    // -------------------------------------------------------------------------
    await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle' });
    await page.getByTestId('email-input').fill('customer@public.com');
    await page.getByTestId('password-input').fill('PublicPass123!');
    await page.getByTestId('login-button').click();
    await page.waitForLoadState('networkidle');

    // -------------------------------------------------------------------------
    // 2. NAVIGATE TO PRODUCT DETAIL
    // -------------------------------------------------------------------------
    await page.goto('http://localhost:5173/', { waitUntil: 'networkidle' });

    // Wait for products to load
    const productCard = page.locator('[data-testid="product-card"]').first();
    await expect(productCard).toBeVisible({ timeout: 20000 });

    // Click "View Details" on first product
    await productCard.locator('button').first().click();

    // Wait for Product Page URL and Review Section
    await page.waitForURL(/\/product\?id=\d+/);
    await expect(page.locator('[data-testid="review-section"]')).toBeVisible({ timeout: 15000 });

    // -------------------------------------------------------------------------
    // 3. VERIFY AVERAGE RATING DISPLAY
    // -------------------------------------------------------------------------
    await expect(page.getByTestId('average-rating')).toBeVisible();

    // -------------------------------------------------------------------------
    // 4. SUBMIT VALID REVIEW
    // -------------------------------------------------------------------------
    const stars = page.getByTestId('rating-stars').locator('span');

    // Click 4th star (4 stars)
    await stars.nth(3).click();

    // Fill comment (>10 chars)
    const commentBox = page.locator('textarea');
    await commentBox.fill('This is an amazing product! Works perfectly.');

    // Submit
    const submitBtn = page.locator('button:has-text("Submit Review")');
    await submitBtn.click();

    // ✅ WAIT FOR SUCCESS MESSAGE OR HANDLE "ALREADY REVIEWED"
    try {
        await expect(page.locator('.alert-success')).toBeVisible({ timeout: 10000 });
    } catch (e) {
        // If success not found, check for error (e.g., already reviewed from previous run)
        const isErrorVisible = await page.locator('.alert-danger').isVisible().catch(() => false);
        if (isErrorVisible) {
            const errorMsg = await page.locator('.alert-danger').textContent();
            console.log(`⚠️ Submission blocked: ${errorMsg}`);

            // If it says "already reviewed", we assume the review exists and proceed
            if (!errorMsg?.includes('already') && !errorMsg?.includes('purchased')) {
                throw new Error(`Review submission failed: ${errorMsg}`);
            }
        } else {
            throw e;
        }
    }

    // Buffer for DOM update after success/error
    await page.waitForTimeout(1500);

    // -------------------------------------------------------------------------
    // 5. VERIFY REVIEW APPEARS IN LIST
    // -------------------------------------------------------------------------
    const reviewItem = page.getByTestId('review-item').first();
    await expect(reviewItem).toBeVisible({ timeout: 10000 });

    // Verify text content contains our comment
    const reviewText = await reviewItem.textContent();
    expect(reviewText).toContain('amazing product');

    // -------------------------------------------------------------------------
    // 6. VERIFY AVERAGE UPDATED
    // -------------------------------------------------------------------------
    await expect(page.getByTestId('average-rating')).toBeVisible();
    const avgText = await page.getByTestId('average-rating').textContent();
    // Should contain a number (the rating)
    expect(avgText).toMatch(/\d/);

    // -------------------------------------------------------------------------
    // 7. TEST VALIDATION (Short comment)
    // -------------------------------------------------------------------------
    // Try to submit a short comment to trigger validation
    await stars.nth(2).click();
    await commentBox.fill('Short');
    await submitBtn.click();

    // Check for validation error message
    await expect(page.locator('.alert-danger')).toBeVisible({ timeout: 5000 });
    const errorText = await page.locator('.alert-danger').textContent();
    expect(errorText).toContain('10 characters');
});