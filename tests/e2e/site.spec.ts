import { expect, test } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('renders and filters the leaderboard', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: /How long until they mention/ })).toBeVisible();
  await expect(page.getByRole('table')).toBeVisible();
  await page.getByPlaceholder('Search episodes').fill('gstack');
  await expect(page).toHaveURL(/q=gstack/);
  await expect(page.getByRole('row', { name: /We need to talk about gstack/i })).toBeVisible();
  await expect(page.getByRole('row', { name: /Theo Almost Lost/i })).toHaveCount(0);
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(
    await page.evaluate(() => document.documentElement.clientWidth)
  );
});

test('restores URL-backed ranking controls', async ({ page }) => {
  await page.goto('/?rank=most&q=gstack&mentions=pending');
  await expect(page.getByRole('button', { name: 'Most gstack' })).toHaveAttribute(
    'aria-pressed',
    'true'
  );
  await expect(page.getByPlaceholder('Search episodes')).toHaveValue('gstack');
  await expect(page.getByLabel('Filter by mention status')).toHaveValue('pending');
  await expect(page.getByRole('row', { name: /We need to talk about gstack/i })).toBeVisible();
});

test('exposes the dataset and methodology', async ({ page, request }) => {
  const response = await request.get('/data/grank.json');
  expect(response.ok()).toBeTruthy();
  expect((await response.json()).source.catalogEpisodeCount).toBe(16);
  await page.goto('/methodology');
  await expect(page.getByRole('heading', { name: 'Source priority' })).toBeVisible();
});

test('has no automatically detectable accessibility violations', async ({ page }) => {
  await page.goto('/');
  const results = await new AxeBuilder({ page }).analyze();
  expect(results.violations).toEqual([]);
});
