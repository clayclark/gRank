import { expect, test } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import type { GrankDataset } from '../../src/lib/types';

test('renders and searches the leaderboard', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Fastest to gstack' })).toBeVisible();
  await expect(page.getByRole('link', { name: 'Dataset' })).toHaveCount(0);
  await expect(page.getByRole('link', { name: 'Methodology' })).toHaveCount(0);
  await expect(page.getByRole('list', { name: /episodes ranked by/i })).toBeVisible();
  await page.getByLabel('Find an episode').fill('gstack');
  await expect(page).not.toHaveURL(/q=gstack/);
  await expect(
    page.getByRole('listitem').filter({ hasText: /We need to talk about gstack/i })
  ).toBeVisible();
  await expect(page.getByRole('listitem').filter({ hasText: /Theo Almost Lost/i })).toHaveCount(0);
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(
    await page.evaluate(() => document.documentElement.clientWidth)
  );
});

test('restores the URL-backed ranking mode', async ({ page }) => {
  await page.goto('/?rank=most');
  await expect(page.getByRole('button', { name: 'Most gstack' })).toHaveAttribute(
    'aria-pressed',
    'true'
  );
  await expect(page.getByLabel('Find an episode')).toHaveValue('');
});

test('keeps the machine-readable dataset available', async ({ request }) => {
  const response = await request.get('/data/grank.json');
  expect(response.ok()).toBeTruthy();
  const dataset = (await response.json()) as GrankDataset;
  expect(dataset.source.catalogEpisodeCount).toBe(16);
  expect(dataset.status).toBe('published');
  expect(dataset.episodes.every((episode) => episode.review.status === 'complete')).toBeTruthy();
  expect(
    dataset.episodes.every((episode) => episode.review.method === 'automated-transcript-consensus')
  ).toBeTruthy();
});

test('has no automatically detectable accessibility violations', async ({ page }) => {
  await page.goto('/');
  const results = await new AxeBuilder({ page }).analyze();
  expect(results.violations).toEqual([]);
});

test('shows timestamped transcript moments without artwork or timeline controls', async ({
  page
}) => {
  await page.goto('/episodes/2-we-need-to-talk-about-gstack');
  await expect(page.getByRole('heading', { name: 'Every gstack moment' })).toBeVisible();
  await expect(page.locator('.mention-list li').first()).toContainText(/\d+:\d{2}/);
  await expect(page.getByRole('button', { name: /^Mention 1 at/ })).toHaveCount(0);
  await expect(page.locator('main img')).toHaveCount(0);
});
