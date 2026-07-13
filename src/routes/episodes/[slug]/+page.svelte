<script lang="ts">
  import MentionTimeline from '$lib/components/MentionTimeline.svelte';
  import {
    episodeSummary,
    formatDate,
    formatDuration,
    formatRate,
    formatTimestamp
  } from '$lib/format';

  let { data } = $props();
  const episode = $derived(data.episode);
</script>

<svelte:head>
  <title>{episode.title} | gRank</title>
  <meta name="description" content={`gstack mention data for ${episode.title} from Nerd Snipe.`} />
</svelte:head>

<div class="shell episode-page">
  <a class="back-link" href="/">← Back to leaderboard</a>

  <header class="episode-poster">
    {#if episode.imageUrl}
      <div class="episode-artwork"><img src={episode.imageUrl} alt="" width="520" height="520" /></div>
    {/if}
    <div class="episode-title-block">
      <span class="eyebrow">
        {episode.episodeNumber !== null ? `Episode ${episode.episodeNumber}` : 'Nerd Snipe episode'}
        / {formatDate(episode.publishedAt)}
      </span>
      <h1>{episode.title}</h1>
      <p>{episodeSummary(episode.description ?? '')}</p>
      <div class="source-links">
        <a href={episode.episodeUrl} target="_blank" rel="noreferrer">Listen to episode</a>
        {#if episode.youtube}
          <a href={episode.youtube.watchUrl} target="_blank" rel="noreferrer">Watch on YouTube</a>
        {/if}
      </div>
    </div>
  </header>

  {#if episode.review.status === 'complete'}
    <section class="episode-scoreboard" aria-label="Episode ranking metrics">
      <article>
        <span>Fastest rank</span>
        <strong>{data.fastestRank === null ? 'Not ranked' : `#${data.fastestRank}`}</strong>
      </article>
      <article>
        <span>Most mentions rank</span>
        <strong>{data.mostRank === null ? 'Not ranked' : `#${data.mostRank}`}</strong>
      </article>
      <article class="score-feature">
        <span>First mention</span>
        <strong>{formatTimestamp(episode.metrics.firstMentionMs)}</strong>
      </article>
      <article>
        <span>Mention count</span>
        <strong>{episode.metrics.mentionCount}</strong>
      </article>
      <article>
        <span>Mentions / hour</span>
        <strong>{formatRate(episode.metrics.mentionsPerHour)}</strong>
      </article>
      <article>
        <span>Runtime</span>
        <strong>{formatDuration(episode.durationSeconds)}</strong>
      </article>
    </section>

    <MentionTimeline
      mentions={episode.mentions}
      durationSeconds={episode.durationSeconds}
      youtubeUrl={episode.youtube?.watchUrl ?? null}
    />
  {:else}
    <section class="review-pending">
      <h2>Transcript review pending</h2>
      <p>
        This episode is in the catalog, but it will not receive a rank until candidate mentions have
        been checked against the audio. No zero or “no mention” result is inferred from incomplete
        work.
      </p>
    </section>
  {/if}

  <section class="provenance">
    <header>
      <h2>What this result is tied to</h2>
    </header>
    <dl>
      <div>
        <dt>Review</dt>
        <dd>{episode.review.status}</dd>
      </div>
      <div>
        <dt>Method</dt>
        <dd>
          {episode.review.method === 'automated-transcript-consensus'
            ? 'Automated transcript consensus'
            : (episode.review.method ?? 'Pending')}
        </dd>
      </div>
      <div>
        <dt>Transcript</dt>
        <dd>{episode.review.transcriptionModel ?? 'Not generated'}</dd>
      </div>
      <div>
        <dt>Audio hash</dt>
        <dd>{episode.audio.sha256 ? `${episode.audio.sha256.slice(0, 12)}...` : 'Pending'}</dd>
      </div>
      <div>
        <dt>Completed</dt>
        <dd>{episode.review.completedAt ? formatDate(episode.review.completedAt) : 'Pending'}</dd>
      </div>
    </dl>
  </section>
</div>
