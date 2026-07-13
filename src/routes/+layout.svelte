<script lang="ts">
  import { page } from '$app/state';
  import '../app.css';
  let { children } = $props();

  const navItems = [{ href: '/', label: 'Leaderboard' }];

  function isActive(href: string) {
    if (href === '/')
      return page.url.pathname === '/' || page.url.pathname.startsWith('/episodes/');
    return page.url.pathname === href;
  }
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
    content="A forensic leaderboard for every Nerd Snipe gstack mention."
  />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="theme-color" content="#eef0ed" media="(prefers-color-scheme: light)" />
  <meta name="theme-color" content="#111514" media="(prefers-color-scheme: dark)" />
</svelte:head>

<header class="site-header">
  <div class="shell header-inner">
    <a class="wordmark" href="/" aria-label="gRank home">
      <span class="wordmark-mark" aria-hidden="true">g</span><span>Rank</span>
    </a>
    <nav aria-label="Main navigation">
      {#each navItems as item}
        <a
          href={item.href}
          class:active={isActive(item.href)}
          aria-current={isActive(item.href) ? 'page' : undefined}
        >
          {item.label}
        </a>
      {/each}
    </nav>
  </div>
</header>

<main>
  {@render children()}
</main>

<footer>
  <div class="shell footer-inner">
    <div class="footer-copy">
      <p>An independent index of <a href="https://nerdsnipe.link/rss">Nerd Snipe</a>.</p>
      <p>Built from timestamped transcript evidence.</p>
    </div>
    <nav class="footer-links" aria-label="Supporting information">
      <a href="/methodology">Methodology</a>
      <a href="/data/grank.json">Dataset</a>
    </nav>
  </div>
</footer>
