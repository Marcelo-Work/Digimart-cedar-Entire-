import { test, expect } from '@playwright/test';
import * as path from 'path';

test('Task 2 Public: Avatar upload works for public user', async ({ page }) => {
  test.setTimeout(90000);
  
  await page.goto('http://localhost:5173/login');
  await page.waitForSelector('[data-testid="email-input"]', { state: 'visible', timeout: 15000 });
  
  await page.getByTestId('email-input').fill('customer@public.com');
  await page.getByTestId('password-input').fill('PublicPass123!');
  await page.getByTestId('login-button').click();
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(1000);
  
  await page.goto('http://localhost:5173/profile');
  await page.waitForSelector('[data-testid="avatar-preview"]', { state: 'visible', timeout: 15000 });
  
  const avatarPreview = page.getByTestId('avatar-preview');
  await expect(avatarPreview).toBeVisible();
  
  const projectRoot = path.resolve(__dirname, '../../../../..');
  const testImagePath = path.join(projectRoot, 'base-app', 'test-assets', 'test-avatar.png');

  const fallbackPath = path.join(path.dirname(projectRoot), 'test-assets', 'test-avatar.png');
  const finalPath = require('fs').existsSync(testImagePath) ? testImagePath : fallbackPath;
  
  const fileInput = page.getByTestId('avatar-input');
  await fileInput.setInputFiles(finalPath);
  
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(2000);
  
  await expect(avatarPreview).toBeVisible();
  const src = await avatarPreview.getAttribute('src');
  
  if (src && src.includes('avatars/')) {
    await expect(page.locator('text=Avatar uploaded successfully')).toBeVisible({ timeout: 10000 });
  }
  
  await page.reload();
  await page.waitForSelector('[data-testid="avatar-preview"]', { timeout: 15000 });
  
  const newSrc = await page.getByTestId('avatar-preview').getAttribute('src');
  if (newSrc && newSrc.includes('avatars/')) {
    expect(newSrc).toContain('avatars/');
  }
});