import { expect, test } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import type { GrankDataset } from '../../src/lib/types';

test('renders and filters the leaderboard', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Fastest to gstack' })).toBeVisible();
  await expect(page.getByRole('link', { name: 'Dataset' })).toBeVisible();
  await expect(page.getByRole('list', { name: /episodes ranked by/i })).toBeVisible();
  await page.getByPlaceholder('Search episodes').fill('gstack');
  await expect(page).toHaveURL(/q=gstack/);
  await expect(page.getByRole('listitem').filter({ hasText: /We need to talk about gstack/i })).toBeVisible();
  await expect(page.getByRole('listitem').filter({ hasText: /Theo Almost Lost/i })).toHaveCount(0);
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(
    await page.evaluate(() => document.documentElement.clientWidth)
  );
});

test('restores URL-backed ranking controls', async ({ page }) => {
  await page.goto('/?rank=most&q=gstack&mentions=present');
  await expect(page.getByRole('button', { name: 'Most gstack' })).toHaveAttribute(
    'aria-pressed',
    'true'
  );
  await expect(page.getByPlaceholder('Search episodes')).toHaveValue('gstack');
  await expect(page.getByLabel('Filter by mention status')).toHaveValue('present');
  await expect(page.getByRole('listitem').filter({ hasText: /We need to talk about gstack/i })).toBeVisible();
});

test('exposes the dataset and methodology', async ({ page, request }) => {
  const response = await request.get('/data/grank.json');
  expect(response.ok()).toBeTruthy();
  const dataset = (await response.json()) as GrankDataset;
  expect(dataset.source.catalogEpisodeCount).toBe(16);
  expect(dataset.status).toBe('published');
  expect(dataset.episodes.every((episode) => episode.review.status === 'complete')).toBeTruthy();
  expect(
    dataset.episodes.every((episode) => episode.review.method === 'automated-transcript-consensus')
  ).toBeTruthy();
  await page.goto('/methodology');
  await expect(page.getByRole('heading', { name: 'Source priority' })).toBeVisible();
});

test('has no automatically detectable accessibility violations', async ({ page }) => {
  await page.goto('/');
  const results = await new AxeBuilder({ page }).analyze();
  expect(results.violations).toEqual([]);
});

test('timeline markers reveal the matching evidence row', async ({ page }) => {
  await page.goto('/episodes/2-we-need-to-talk-about-gstack');
  await page.getByRole('button', { name: /^Mention 1 at/ }).click();
  await expect(page.locator('.mention-list li').first()).toBeFocused();
});
