import { test, expect } from '@playwright/test';

test.describe('Route guards', () => {
  test('anonymous user is redirected to login from a protected route', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/\/login/);
  });

  test('anonymous user is redirected to login from an admin route', async ({ page }) => {
    await page.goto('/admin');
    await expect(page).toHaveURL(/\/login/);
  });

  test('a member is redirected away from the admin console', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type=email]', 'member1@library.com');
    await page.fill('input[type=password]', 'MemberPass123');
    await page.click('button[type=submit]');
    await expect(page).toHaveURL(/\/dashboard/);

    await page.goto('/admin');
    await expect(page).toHaveURL(/\/dashboard/);
  });

  test('an admin can reach the admin console', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type=email]', 'admin@library.com');
    await page.fill('input[type=password]', 'AdminPass123');
    await page.click('button[type=submit]');
    await expect(page).toHaveURL(/\/dashboard/);
    await page.goto('/admin');
    await expect(page.getByRole('heading', { name: 'Librarian Dashboard' })).toBeVisible();
  });

  test('public pages remain reachable without logging in', async ({ page }) => {
    await page.goto('/catalog');
    await expect(page.getByRole('heading', { name: 'Catalog' })).toBeVisible();
  });
});
