<script lang="ts">
  import NumberFlow from '@number-flow/svelte';
  import { formatTimestamp } from '$lib/format';
  import type { Episode } from '$lib/types';

  let { episodes }: { episodes: Episode[] } = $props();

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

<section class="stats" aria-label="Leaderboard summary">
  <article>
    <span class="stat-label">Episodes with gstack</span>
    <strong><NumberFlow value={withMentions.length} /></strong>
  </article>
  <article>
    <span class="stat-label">Fastest mention</span>
    <strong>{fastest === null ? 'None' : formatTimestamp(fastest)}</strong>
  </article>
  <article>
    <span class="stat-label">Total mentions</span>
    <strong><NumberFlow value={totalMentions} /></strong>
  </article>
</section>
