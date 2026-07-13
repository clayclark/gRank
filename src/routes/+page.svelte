<script lang="ts">
  import { browser } from '$app/environment';
  import { afterNavigate, replaceState } from '$app/navigation';
  import Leaderboard from '$lib/components/Leaderboard.svelte';
  import RankingControls from '$lib/components/RankingControls.svelte';
  import SummaryStats from '$lib/components/SummaryStats.svelte';
  import { dataset } from '$lib/data';
  import { rankEpisodes } from '$lib/ranking';
  import type { MentionFilter, RankMode } from '$lib/types';

  let mode = $state<RankMode>('fastest');
  let filter = $state<MentionFilter>('all');
  let query = $state('');
  let mounted = $state(false);

  afterNavigate(() => {
    if (mounted) return;
    const params = new URLSearchParams(window.location.search);
    if (params.get('rank') === 'most') mode = 'most';
    const selectedFilter = params.get('mentions');
    if (selectedFilter && ['all', 'present', 'absent', 'pending'].includes(selectedFilter)) {
      filter = selectedFilter as MentionFilter;
    }
    query = params.get('q') ?? '';
    mounted = true;
  });

  $effect(() => {
    if (!browser || !mounted) return;
    const params = new URLSearchParams();
    if (mode !== 'fastest') params.set('rank', mode);
    if (filter !== 'all') params.set('mentions', filter);
    if (query.trim()) params.set('q', query.trim());
    const next = params.size ? `?${params}` : window.location.pathname;
    replaceState(next, {});
  });

  const visibleEpisodes = $derived.by(() => {
    const normalizedQuery = query.trim().toLocaleLowerCase();
    const matching = dataset.episodes.filter((episode) => {
      if (normalizedQuery && !episode.title.toLocaleLowerCase().includes(normalizedQuery))
        return false;
      if (filter === 'pending') return episode.review.status === 'pending';
      if (episode.review.status === 'pending') return filter === 'all';
      if (filter === 'present') return episode.metrics.mentionCount > 0;
      if (filter === 'absent') return episode.metrics.mentionCount === 0;
      return true;
    });
    return rankEpisodes(matching, mode);
  });
</script>

<svelte:head>
  <title>gRank | The Nerd Snipe gstack leaderboard</title>
  <meta property="og:title" content="gRank | How quickly does Nerd Snipe mention gstack?" />
  <meta property="og:image" content="/images/grank-signal-hero.jpg" />
</svelte:head>

<section class="ranking-home shell" aria-labelledby="leaderboard-heading">
  <header class="ranking-intro">
    <div>
      <p class="kicker">Nerd Snipe transcript index</p>
      <h1 id="leaderboard-heading">
        {mode === 'fastest' ? 'Fastest to gstack' : 'Most gstack'}
      </h1>
    </div>
    <div class="ranking-summary">
      <p>Episodes ranked by their first transcript match or total gstack mentions.</p>
      <span>{visibleEpisodes.length} of {dataset.episodes.length} episodes</span>
    </div>
  </header>

  <div class="signal-index">
    <aside class="signal-sidebar">
      <div class="signal-sidebar-heading">
        <span>Dataset pulse</span>
        <strong>{visibleEpisodes.length} shown</strong>
      </div>
      <SummaryStats episodes={dataset.episodes} generatedAt={dataset.generatedAt} />
    </aside>

    <div class="leaderboard-section">
    <div class="control-dock">
      <RankingControls bind:mode bind:filter bind:query />
    </div>
    <Leaderboard episodes={visibleEpisodes} allEpisodes={dataset.episodes} {mode} />
    </div>
  </div>
</section>
