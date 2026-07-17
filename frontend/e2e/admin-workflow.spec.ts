import { test, expect } from '@playwright/test';

test.describe('Administrator browser workflow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type=email]', 'admin@library.com');
    await page.fill('input[type=password]', 'AdminPass123');
    await page.click('button[type=submit]');
    await expect(page).toHaveURL(/\/dashboard/);
  });

  test('admin can view KPIs and navigate the console', async ({ page }) => {
    await page.goto('/admin');
    await expect(page.getByText('Total books')).toBeVisible();
    await expect(page.getByText('Outstanding fines ($)')).toBeVisible();
  });

  test('admin can view and search the book catalog', async ({ page }) => {
    await page.goto('/admin/books');
    await expect(page.getByRole('heading', { name: 'Books' })).toBeVisible();
    await page.fill('input[placeholder="Search by title…"]', 'Dune');
    await expect(page.getByRole('cell', { name: 'Dune' })).toBeVisible();
  });

  test('admin can view members and reports', async ({ page }) => {
    await page.goto('/admin/members');
    await expect(page.getByRole('heading', { name: 'Members' })).toBeVisible();

    await page.goto('/admin/reports');
    await expect(page.getByRole('heading', { name: 'Popular books' })).toBeVisible();
  });
});
