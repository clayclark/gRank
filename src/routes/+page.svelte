<script lang="ts">
  import { afterNavigate, replaceState } from '$app/navigation';
  import Leaderboard from '$lib/components/Leaderboard.svelte';
  import RankingControls from '$lib/components/RankingControls.svelte';
  import SummaryStats from '$lib/components/SummaryStats.svelte';
  import { dataset } from '$lib/data';
  import { rankEpisodes } from '$lib/ranking';
  import type { RankMode } from '$lib/types';

  let mode = $state<RankMode>('fastest');
  let query = $state('');
  let mounted = $state(false);

  afterNavigate(() => {
    if (mounted) return;
    const params = new URLSearchParams(window.location.search);
    if (params.get('rank') === 'most') mode = 'most';
    mounted = true;
  });

  $effect(() => {
    if (!mounted) return;
    const params = new URLSearchParams();
    if (mode !== 'fastest') params.set('rank', mode);
    const next = params.size ? `?${params}` : window.location.pathname;
    replaceState(next, {});
  });

  const visibleEpisodes = $derived.by(() => {
    const normalizedQuery = query.trim().toLocaleLowerCase();
    const matching = dataset.episodes.filter(
      (episode) => !normalizedQuery || episode.title.toLocaleLowerCase().includes(normalizedQuery)
    );
    return rankEpisodes(matching, mode);
  });
</script>

<svelte:head>
  <title>gRank | The Nerd Snipe gstack leaderboard</title>
  <meta property="og:title" content="gRank | How quickly does Nerd Snipe mention gstack?" />
</svelte:head>

<section class="ranking-home shell" aria-labelledby="leaderboard-heading">
  <header class="ranking-intro">
    <h1 id="leaderboard-heading">
      {mode === 'fastest' ? 'Fastest to gstack' : 'Most gstack'}
    </h1>
    <p>
      {dataset.episodes.length} episodes, updated
      {new Date(dataset.generatedAt).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        timeZone: 'UTC'
      })}
    </p>
  </header>

  <SummaryStats episodes={dataset.episodes} />

  <section class="leaderboard-section" aria-label="Episode rankings">
    <div class="control-dock">
      <RankingControls bind:mode bind:query />
    </div>
    <Leaderboard episodes={visibleEpisodes} allEpisodes={dataset.episodes} {mode} />
  </section>

  <p class="ranking-note">
    gRank counts explicit spoken references to gstack. Rank by the first timestamp or the total
    number of mentions.
  </p>
</section>
