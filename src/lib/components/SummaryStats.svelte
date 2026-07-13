<script lang="ts">
  import { formatTimestamp } from '$lib/format';
  import type { Episode } from '$lib/types';

  let { episodes, generatedAt }: { episodes: Episode[]; generatedAt: string } = $props();

  const complete = $derived(episodes.filter((episode) => episode.review.status === 'complete'));
  const withMentions = $derived(complete.filter((episode) => episode.metrics.mentionCount > 0));
  const fastest = $derived(
    withMentions.length
      ? Math.min(...withMentions.map((episode) => episode.metrics.firstMentionMs ?? Infinity))
      : null
  );
  const totalMentions = $derived(
    complete.reduce((sum, episode) => sum + episode.metrics.mentionCount, 0)
  );
</script>

<section class="stats" aria-label="Dataset summary">
  <article>
    <span class="stat-label">Analyzed</span>
    <strong>{complete.length}</strong>
    <span class="stat-note">of {episodes.length} episodes</span>
  </article>
  <article>
    <span class="stat-label">With gstack</span>
    <strong>{withMentions.length}</strong>
    <span class="stat-note">reviewed episodes</span>
  </article>
  <article>
    <span class="stat-label">Fastest</span>
    <strong>{fastest === null ? 'None' : formatTimestamp(fastest)}</strong>
    <span class="stat-note">first mention</span>
  </article>
  <article>
    <span class="stat-label">Total</span>
    <strong>{totalMentions}</strong>
    <span class="stat-note">accepted mentions</span>
  </article>
  <article>
    <span class="stat-label">Snapshot</span>
    <strong class="date-value"
      >{new Date(generatedAt).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric'
      })}</strong
    >
    <span class="stat-note">{new Date(generatedAt).getUTCFullYear()}</span>
  </article>
</section>
