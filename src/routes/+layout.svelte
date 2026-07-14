<script lang="ts">
  import '../app.css';
  let { children } = $props();
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
  <meta name="theme-color" content="#eef0ed" media="(prefers-color-scheme: light)" />
  <meta name="theme-color" content="#111514" media="(prefers-color-scheme: dark)" />
</svelte:head>

<header class="site-header">
  <div class="shell header-inner">
    <a class="wordmark" href="/" aria-label="gRank home">
      <span class="wordmark-mark" aria-hidden="true">g</span><span>Rank</span>
    </a>
  </div>
</header>

<main>
  {@render children()}
</main>

<footer>
  <div class="shell footer-inner">
    <p>An unofficial <a href="https://nerdsnipe.link/rss">Nerd Snipe</a> leaderboard.</p>
  </div>
</footer>
