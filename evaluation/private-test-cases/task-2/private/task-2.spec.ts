import { test, expect } from '@playwright/test';
import * as path from 'path';

test('Task 2 Private: Avatar upload works for private user', async ({ page }) => {
  test.setTimeout(90000);
  
  console.log('Step 1: Navigate to login');
  await page.goto('http://localhost:5173/login');
  
  console.log('Step 2: Wait for and fill login form');
  await page.waitForSelector('[data-testid="email-input"]', { timeout: 20000 });
  await page.getByTestId('email-input').fill('customer@private.com');
  await page.getByTestId('password-input').fill('PrivatePass123!');
  await page.getByTestId('login-button').click();
  
  console.log('Step 3: Wait for navigation after login');
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(2000);
  
  console.log('Current URL:', page.url());
  const pageContent = await page.content();
  console.log('Page has avatar-preview:', pageContent.includes('avatar-preview'));
  console.log('Page has login form:', pageContent.includes('email-input'));
  
  if (page.url().includes('/login')) {
    console.log('❌ Still on login page - login failed');
    const error = await page.locator('[data-testid="error-message"]').textContent();
    console.log('Login error:', error);
  }
  
  console.log('Step 4: Navigate to profile');
  await page.goto('http://localhost:5173/profile');
  
  await page.screenshot({ path: 'debug-private-profile.png', fullPage: true });
  
  console.log('Step 5: Wait for avatar-preview');
  try {
    await page.waitForSelector('[data-testid="avatar-preview"]', { 
      state: 'visible',
      timeout: 20000  
    });
    console.log('✅ avatar-preview found!');
  } catch (e) {
    console.log('❌ avatar-preview NOT found');
    console.log('Final URL:', page.url());
    console.log('Page title:', await page.title());
    throw e;
  }
  
  const avatarPreview = page.getByTestId('avatar-preview');
  await expect(avatarPreview).toBeVisible();
  
  const projectRoot = process.cwd();
  const testImagePath = path.join(projectRoot, 'test-assets', 'test-avatar.png');
  
  const fileInput = page.getByTestId('avatar-input');
  await fileInput.setInputFiles(testImagePath);
  
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(2000);
  
  const src = await avatarPreview.getAttribute('src');
  if (src && src.includes('avatars/')) {
    await expect(page.locator('text=Avatar uploaded successfully')).toBeVisible({ timeout: 10000 });
  }
});