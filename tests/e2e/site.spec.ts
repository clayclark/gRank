import { expect, test } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import type { GrankDataset } from '../../src/lib/types';

test('renders and searches the leaderboard', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Fastest to gstack' })).toBeVisible();
  await expect(page.getByRole('link', { name: 'Dataset' })).toHaveCount(0);
  await expect(page.getByRole('link', { name: 'Methodology' })).toHaveCount(0);
  await expect(page.getByRole('link', { name: 'Clay Clark on GitHub' })).toHaveAttribute(
    'href',
    'https://github.com/clayclark'
  );
  await expect(page.getByRole('link', { name: 'Clay Clark on X' })).toHaveAttribute(
    'href',
    'https://x.com/clayboicartii'
  );
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

test('switches and persists the theme preference', async ({ page }) => {
  await page.emulateMedia({ colorScheme: 'dark' });
  await page.goto('/');

  const root = page.locator('html');
  await expect(page.getByRole('button', { name: /Theme: System/i })).toBeVisible();
  await expect(root).not.toHaveAttribute('data-theme');

  await page.getByRole('button', { name: /Theme: System/i }).click();
  await expect(root).toHaveAttribute('data-theme', 'light');
  await expect(page.getByRole('button', { name: /Theme: Light/i })).toBeVisible();
  expect(await page.evaluate(() => localStorage.getItem('grank-theme'))).toBe('light');

  await page.reload();
  await expect(root).toHaveAttribute('data-theme', 'light');
  await expect(page.getByRole('button', { name: /Theme: Light/i })).toBeVisible();

  await page.getByRole('button', { name: /Theme: Light/i }).click();
  await expect(root).toHaveAttribute('data-theme', 'dark');
  await expect(page.getByRole('button', { name: /Theme: Dark/i })).toBeVisible();

  await page.getByRole('button', { name: /Theme: Dark/i }).click();
  await expect(root).not.toHaveAttribute('data-theme');
  await expect(page.getByRole('button', { name: /Theme: System/i })).toBeVisible();
  expect(await page.evaluate(() => localStorage.getItem('grank-theme'))).toBeNull();
});

test('animates rank changes and preserves the episode title across navigation', async ({
  page
}) => {
  await page.goto('/');

  const firstResult = page.locator('.signal-list li').first();
  await expect(firstResult).toContainText('We (mostly) like Claude Opus 4.8');
  await expect(firstResult.locator('number-flow-svelte')).toHaveCount(1);

  await page.getByRole('button', { name: 'Most gstack' }).click();
  await expect(page).toHaveURL(/rank=most/);
  await expect(page.locator('.signal-list li').first()).toContainText(
    'Theo Almost Lost $1 Million'
  );

  const episodeLink = page.getByRole('link', { name: 'We need to talk about gstack' });
  await expect(episodeLink).toHaveCSS(
    'view-transition-name',
    'episode-2-we-need-to-talk-about-gstack'
  );
  await episodeLink.click();

  const episodeHeading = page.getByRole('heading', { name: 'We need to talk about gstack' });
  await expect(episodeHeading).toBeVisible();
  await expect(episodeHeading).toHaveCSS(
    'view-transition-name',
    'episode-2-we-need-to-talk-about-gstack'
  );
});

test('honors the reduced-motion preference', async ({ page }) => {
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.addInitScript(() => {
    const browserWindow = window as typeof window & { viewTransitionsStarted: number };
    browserWindow.viewTransitionsStarted = 0;
    Object.defineProperty(document, 'startViewTransition', {
      configurable: true,
      value: () => {
        browserWindow.viewTransitionsStarted += 1;
      }
    });
  });

  await page.goto('/');
  await page.getByRole('button', { name: 'Most gstack' }).click();
  await expect(page.locator('.signal-list li').first()).toContainText(
    'Theo Almost Lost $1 Million'
  );

  const activeAnimations = await page
    .locator('.signal-list li')
    .evaluateAll((rows) => rows.reduce((count, row) => count + row.getAnimations().length, 0));
  expect(activeAnimations).toBe(0);

  await page.getByRole('link', { name: 'We need to talk about gstack' }).click();
  await expect(page.getByRole('heading', { name: 'We need to talk about gstack' })).toBeVisible();
  expect(
    await page.evaluate(
      () => (window as typeof window & { viewTransitionsStarted: number }).viewTransitionsStarted
    )
  ).toBe(0);
});

test('runs without content security policy violations', async ({ page }) => {
  const cspViolations: string[] = [];
  page.on('console', (message) => {
    if (message.type() === 'error' && message.text().includes('Content Security Policy')) {
      cspViolations.push(message.text());
    }
  });

  await page.goto('/');
  await page.getByRole('button', { name: 'Most gstack' }).click();
  await page.getByRole('link', { name: 'We need to talk about gstack' }).click();
  await expect(page.getByRole('heading', { name: 'We need to talk about gstack' })).toBeVisible();

  expect(cspViolations).toEqual([]);
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
