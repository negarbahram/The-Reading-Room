import { test, expect } from '@playwright/test';

test.describe('Member browser workflow', () => {
  test('member can browse catalog, view a book, and see recommendations on the dashboard', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type=email]', 'member1@library.com');
    await page.fill('input[type=password]', 'MemberPass123');
    await page.click('button[type=submit]');
    await expect(page).toHaveURL(/\/dashboard/);

    await expect(page.getByRole('heading', { name: /Welcome back/ })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Recommended for you' })).toBeVisible();

    await page.goto('/catalog');
    await page.getByRole('link').filter({ hasText: 'Frankenstein' }).first().click();
    await expect(page.getByRole('heading', { name: 'Frankenstein' })).toBeVisible();
  });

  test('member can view loans, reservations and fines pages without error', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type=email]', 'member1@library.com');
    await page.fill('input[type=password]', 'MemberPass123');
    await page.click('button[type=submit]');
    await expect(page).toHaveURL(/\/dashboard/);

    await page.goto('/loans');
    await expect(page.getByRole('heading', { name: 'My Loans' })).toBeVisible();

    await page.goto('/reservations');
    await expect(page.getByRole('heading', { name: 'Reservations' })).toBeVisible();

    await page.goto('/fines');
    await expect(page.getByRole('heading', { name: 'Fines' })).toBeVisible();
  });
});
