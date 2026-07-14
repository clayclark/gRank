<script lang="ts">
  import { formatDate, formatTimestamp } from '$lib/format';
  import { metricRank } from '$lib/ranking';
  import type { Episode, RankMode } from '$lib/types';

  let {
    episodes,
    allEpisodes,
    mode
  }: { episodes: Episode[]; allEpisodes: Episode[]; mode: RankMode } = $props();
</script>

<div class="leaderboard-wrap">
  <ol
    class="signal-list"
    aria-label={`Nerd Snipe episodes ranked by ${mode === 'fastest' ? 'first gstack mention' : 'total gstack mentions'}`}
  >
    {#each episodes as episode (episode.guid)}
      {@const rank = metricRank(allEpisodes, episode, mode)}
      <li>
        <span class="rank">{rank === null ? 'No gstack' : `#${rank}`}</span>
        <div class="episode-identity">
          <span class="episode-meta">
            {episode.episodeNumber !== null ? `Episode ${episode.episodeNumber}` : 'Episode'} /
            {formatDate(episode.publishedAt)}
          </span>
          <a href={`/episodes/${episode.slug}`}>{episode.title}</a>
        </div>
        <div class:active-metric={mode === 'fastest'} class="episode-metric first-mention-metric">
          <span>First mention</span>
          <strong>{formatTimestamp(episode.metrics.firstMentionMs)}</strong>
        </div>
        <div class:active-metric={mode === 'most'} class="episode-metric mention-count-metric">
          <span>Total mentions</span>
          <strong>{episode.metrics.mentionCount}</strong>
        </div>
      </li>
    {/each}
  </ol>
  {#if episodes.length === 0}
    <div class="empty-state">
      <strong>No episodes match this search.</strong>
      <span>Try another title.</span>
    </div>
  {/if}
</div>
