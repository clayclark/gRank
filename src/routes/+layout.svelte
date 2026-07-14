<script lang="ts">
  import { onNavigate } from '$app/navigation';
  import { onMount } from 'svelte';
  import '../app.css';

  type Theme = 'system' | 'light' | 'dark';

  let { children } = $props();
  let theme = $state<Theme>('system');

  const nextTheme: Record<Theme, Theme> = {
    system: 'light',
    light: 'dark',
    dark: 'system'
  };

  const themeName: Record<Theme, string> = {
    system: 'System',
    light: 'Light',
    dark: 'Dark'
  };

  function resolvedTheme(selectedTheme: Theme) {
    return selectedTheme === 'system'
      ? window.matchMedia('(prefers-color-scheme: dark)').matches
        ? 'dark'
        : 'light'
      : selectedTheme;
  }

  function updateThemeColor(selectedTheme: Theme) {
    document
      .querySelector('meta[name="theme-color"]')
      ?.setAttribute('content', resolvedTheme(selectedTheme) === 'dark' ? '#111514' : '#eef0ed');
  }

  function applyTheme(selectedTheme: Theme) {
    theme = selectedTheme;

    if (selectedTheme === 'system') {
      delete document.documentElement.dataset.theme;
      localStorage.removeItem('grank-theme');
    } else {
      document.documentElement.dataset.theme = selectedTheme;
      localStorage.setItem('grank-theme', selectedTheme);
    }

    updateThemeColor(selectedTheme);
  }

  onMount(() => {
    const savedTheme = localStorage.getItem('grank-theme');
    theme = savedTheme === 'light' || savedTheme === 'dark' ? savedTheme : 'system';

    const systemTheme = window.matchMedia('(prefers-color-scheme: dark)');
    const handleSystemThemeChange = () => {
      if (theme === 'system') updateThemeColor('system');
    };

    systemTheme.addEventListener('change', handleSystemThemeChange);
    return () => systemTheme.removeEventListener('change', handleSystemThemeChange);
  });

  onNavigate((navigation) => {
    if (
      !document.startViewTransition ||
      window.matchMedia('(prefers-reduced-motion: reduce)').matches
    ) {
      return;
    }

    return new Promise((resolve) => {
      document.startViewTransition(async () => {
        resolve();
        await navigation.complete;
      });
    });
  });
</script>

<svelte:head>
  <link rel="icon" href="/favicon.svg" />
  <link
    rel="preload"
    href="/fonts/archivo-latin-variable.woff2"
    as="font"
    type="font/woff2"
    crossorigin="anonymous"
    fetchpriority="high"
  />
  <meta
    name="description"
    content="gRank ranks every Nerd Snipe episode by how quickly and how often it mentions gstack."
  />
  <meta property="og:site_name" content="gRank" />
  <meta property="og:type" content="website" />
  <meta
    property="og:description"
    content="A playful leaderboard for every Nerd Snipe gstack mention."
  />
  <meta name="twitter:card" content="summary" />
</svelte:head>

<header class="site-header">
  <div class="shell header-inner">
    <a class="wordmark" href="/" aria-label="gRank home">
      <span class="wordmark-mark" aria-hidden="true">g</span><span>Rank</span>
    </a>
    <button
      class="theme-toggle"
      type="button"
      aria-label={`Theme: ${themeName[theme]}. Switch to ${themeName[nextTheme[theme]].toLowerCase()} theme`}
      title={`Theme: ${themeName[theme]}`}
      onclick={() => applyTheme(nextTheme[theme])}
    >
      {#if theme === 'light'}
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <circle cx="12" cy="12" r="3.5"></circle>
          <path
            d="M12 2v2M12 20v2M4.93 4.93l1.42 1.42M17.65 17.65l1.42 1.42M2 12h2M20 12h2M4.93 19.07l1.42-1.42M17.65 6.35l1.42-1.42"
          ></path>
        </svg>
      {:else if theme === 'dark'}
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M20.5 14.1A8.5 8.5 0 0 1 9.9 3.5 8.5 8.5 0 1 0 20.5 14.1Z"></path>
        </svg>
      {:else}
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <circle cx="12" cy="12" r="8.5"></circle>
          <path class="theme-toggle-fill" d="M12 3.5a8.5 8.5 0 0 0 0 17Z"></path>
        </svg>
      {/if}
    </button>
  </div>
</header>

<main>
  {@render children()}
</main>

<footer>
  <div class="shell footer-inner">
    <p>An unofficial <a href="https://nerdsnipe.link/rss">Nerd Snipe</a> leaderboard.</p>
    <nav class="footer-links" aria-label="Social links">
      <a
        href="https://github.com/clayclark"
        target="_blank"
        rel="noreferrer"
        aria-label="Clay Clark on GitHub"
      >
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path
            d="M12 .7a11.5 11.5 0 0 0-3.64 22.41c.58.1.79-.25.79-.56v-2.23c-3.22.7-3.9-1.37-3.9-1.37-.52-1.34-1.28-1.7-1.28-1.7-1.05-.72.08-.7.08-.7 1.16.08 1.77 1.19 1.77 1.19 1.03 1.77 2.7 1.26 3.36.96.1-.75.4-1.26.73-1.55-2.57-.29-5.27-1.28-5.27-5.68 0-1.25.45-2.28 1.18-3.08-.12-.29-.51-1.46.11-3.04 0 0 .97-.31 3.16 1.18a10.9 10.9 0 0 1 5.76 0c2.2-1.49 3.16-1.18 3.16-1.18.63 1.58.23 2.75.12 3.04.73.8 1.17 1.83 1.17 3.08 0 4.42-2.7 5.38-5.28 5.67.42.36.79 1.07.79 2.16v3.2c0 .31.21.67.8.56A11.5 11.5 0 0 0 12 .7Z"
          />
        </svg>
        <span>Clay C.</span>
      </a>
      <a
        href="https://x.com/clayboicartii"
        target="_blank"
        rel="noreferrer"
        aria-label="Clay Clark on X"
      >
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path
            d="M18.9 2.25h3.68l-8.04 9.19L24 21.75h-7.4l-5.8-7.58-6.63 7.58H.48l8.6-9.83L0 2.25h7.59l5.23 6.92 6.08-6.92Zm-1.3 17.68h2.04L6.48 3.98H4.3L17.6 19.93Z"
          />
        </svg>
        <span>@clayboicartii</span>
      </a>
    </nav>
  </div>
</footer>
