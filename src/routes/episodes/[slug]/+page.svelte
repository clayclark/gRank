<script lang="ts">
  import MentionList from '$lib/components/MentionList.svelte';
  import { formatDate, formatTimestamp } from '$lib/format';

  let { data } = $props();
  const episode = $derived(data.episode);
</script>

<svelte:head>
  <title>{episode.title} | gRank</title>
  <meta name="description" content={`gstack mention data for ${episode.title} from Nerd Snipe.`} />
</svelte:head>

<div class="shell episode-page">
  <a class="back-link" href="/">← Back to leaderboard</a>

  <header class="episode-header">
    <div class:long-title={episode.title.length > 48} class="episode-title-block">
      <span class="episode-meta-line">
        {episode.episodeNumber !== null ? `Episode ${episode.episodeNumber}` : 'Nerd Snipe episode'}
        / {formatDate(episode.publishedAt)}
      </span>
      <h1>{episode.title}</h1>
      <div class="source-links">
        <a href={episode.episodeUrl} target="_blank" rel="noreferrer">Listen to episode</a>
        {#if episode.youtube}
          <a href={episode.youtube.watchUrl} target="_blank" rel="noreferrer">Watch on YouTube</a>
        {/if}
      </div>
    </div>
  </header>

  <section class="episode-scoreboard" aria-label="Episode ranking metrics">
    <article class="metric-primary">
      <span>First mention</span>
      <strong>{formatTimestamp(episode.metrics.firstMentionMs)}</strong>
    </article>
    <article class="metric-primary">
      <span>Total mentions</span>
      <strong>{episode.metrics.mentionCount}</strong>
    </article>
    <article>
      <span>First mention rank</span>
      <strong>{data.fastestRank === null ? 'No gstack' : `#${data.fastestRank}`}</strong>
    </article>
    <article>
      <span>Mention count rank</span>
      <strong>{data.mostRank === null ? 'Unavailable' : `#${data.mostRank}`}</strong>
    </article>
  </section>

  <MentionList mentions={episode.mentions} youtubeUrl={episode.youtube?.watchUrl ?? null} />
</div>
