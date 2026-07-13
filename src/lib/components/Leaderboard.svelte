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
  <ol
    class="signal-list"
    aria-label={`Nerd Snipe episodes ranked by ${mode === 'fastest' ? 'first gstack mention' : 'total gstack mentions'}`}
  >
    {#each episodes as episode (episode.guid)}
      {@const rank = metricRank(allEpisodes, episode, mode)}
      <li class:pending={episode.review.status === 'pending'}>
        <span class="rank">{rank === null ? 'NR' : String(rank).padStart(2, '0')}</span>
        <div class="episode-identity">
          <span class="episode-meta">
            {episode.episodeNumber !== null ? `Episode ${episode.episodeNumber}` : 'Episode'} /
            {formatDate(episode.publishedAt)}
          </span>
          <a href={`/episodes/${episode.slug}`}>{episode.title}</a>
        </div>
        <div class="primary-signal">
          <span>{mode === 'fastest' ? 'First signal' : 'Total signals'}</span>
          <strong>
            {episode.review.status === 'pending'
              ? 'Pending'
              : mode === 'fastest'
                ? formatTimestamp(episode.metrics.firstMentionMs)
                : episode.metrics.mentionCount}
          </strong>
        </div>
        <dl class="episode-facts">
          <div><dt>Runtime</dt><dd>{formatDuration(episode.durationSeconds)}</dd></div>
          <div><dt>Mentions</dt><dd>{episode.review.status === 'pending' ? 'Pending' : episode.metrics.mentionCount}</dd></div>
          <div><dt>Per hour</dt><dd>{episode.review.status === 'pending' ? 'Pending' : formatRate(episode.metrics.mentionsPerHour)}</dd></div>
        </dl>
      </li>
    {/each}
  </ol>
  {#if episodes.length === 0}
    <div class="empty-state">
      <strong>No episodes match these filters.</strong>
      <span>Try clearing the search or selecting a different review state.</span>
    </div>
  {/if}
</div>
