<script lang="ts">
  import '../app.css';
  let { children } = $props();
</script>

<svelte:head>
  <link rel="icon" href="/favicon.svg" />
  <meta
    name="description"
    content="gRank ranks every Nerd Snipe episode by how quickly and how often it mentions gstack."
  />
  <meta property="og:site_name" content="gRank" />
  <meta property="og:type" content="website" />
</svelte:head>

<header class="site-header">
  <div class="shell header-inner">
    <a class="wordmark" href="/" aria-label="gRank home"><span>g</span>Rank</a>
    <nav aria-label="Main navigation">
      <a href="/">Leaderboard</a>
      <a href="/methodology">Methodology</a>
      <a href="/data/grank.json">Dataset</a>
    </nav>
  </div>
</header>

<main>
  {@render children()}
</main>

<footer>
  <div class="shell footer-inner">
    <p>An independent index of <a href="https://nerdsnipe.link/rss">Nerd Snipe</a>.</p>
    <p>Built from reviewed, timestamped audio evidence.</p>
  </div>
</footer>
