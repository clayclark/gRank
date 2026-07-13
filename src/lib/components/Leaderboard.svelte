<script lang="ts">
  import { formatDate, formatDuration, formatRate, formatTimestamp } from '$lib/format';
  import { metricRank } from '$lib/ranking';
  import type { Episode, RankMode } from '$lib/types';

  let {
    episodes,
    allEpisodes,
    mode
  }: { episodes: Episode[]; allEpisodes: Episode[]; mode: RankMode } = $props();
</script>

<div class="leaderboard-wrap">
  <table>
    <caption class="sr-only"
      >Nerd Snipe episodes ranked by {mode === 'fastest'
        ? 'first gstack mention'
        : 'total gstack mentions'}</caption
    >
    <thead>
      <tr>
        <th scope="col">Rank</th>
        <th scope="col">Episode</th>
        <th scope="col">Published</th>
        <th scope="col">Duration</th>
        <th scope="col">First mention</th>
        <th scope="col">Mentions</th>
        <th scope="col">Per hour</th>
      </tr>
    </thead>
    <tbody>
      {#each episodes as episode (episode.guid)}
        {@const rank = metricRank(allEpisodes, episode, mode)}
        <tr class:pending={episode.review.status === 'pending'}>
          <td data-label="Rank" class="rank">
            {rank === null ? 'Not ranked' : rank}
          </td>
          <th scope="row" data-label="Episode">
            <a href={`/episodes/${episode.slug}`}>{episode.title}</a>
            <span class="episode-meta">
              {episode.episodeNumber !== null ? `Episode ${episode.episodeNumber}` : 'Episode'}
              {episode.review.status === 'pending' ? ' / Pending review' : ''}
            </span>
          </th>
          <td data-label="Published">{formatDate(episode.publishedAt)}</td>
          <td data-label="Duration" class="numeric">{formatDuration(episode.durationSeconds)}</td>
          <td data-label="First mention" class="numeric emphasis">
            {episode.review.status === 'pending'
              ? 'Pending'
              : formatTimestamp(episode.metrics.firstMentionMs)}
          </td>
          <td data-label="Mentions" class="numeric"
            >{episode.review.status === 'pending' ? 'Pending' : episode.metrics.mentionCount}</td
          >
          <td data-label="Per hour" class="numeric"
            >{episode.review.status === 'pending'
              ? 'Pending'
              : formatRate(episode.metrics.mentionsPerHour)}</td
          >
        </tr>
      {/each}
    </tbody>
  </table>
  {#if episodes.length === 0}
    <div class="empty-state">
      <strong>No episodes match these filters.</strong>
      <span>Try clearing the search or selecting a different review state.</span>
    </div>
  {/if}
</div>
