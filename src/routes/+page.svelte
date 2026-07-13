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
  <title>gRank — The Nerd Snipe gstack leaderboard</title>
  <meta property="og:title" content="gRank — How quickly does Nerd Snipe mention gstack?" />
</svelte:head>

<section class="hero shell">
  <div class="hero-copy">
    <span class="eyebrow">A highly specific podcast index</span>
    <h1>How long until they mention <em>gstack?</em></h1>
    <p>
      Every Nerd Snipe episode, ranked by the first audible gstack mention and the total number of
      times it comes up.
    </p>
  </div>
  <aside class="hero-note">
    <span class:live={dataset.status === 'published'}></span>
    {dataset.status === 'published'
      ? 'Every episode has been transcribed and manually reviewed.'
      : 'The catalog is live. Transcript review is still in progress.'}
  </aside>
</section>

<div class="shell">
  <SummaryStats episodes={dataset.episodes} generatedAt={dataset.generatedAt} />

  <section class="leaderboard-section" aria-labelledby="leaderboard-heading">
    <div class="section-heading leaderboard-heading">
      <div>
        <span class="eyebrow">The leaderboard</span>
        <h2 id="leaderboard-heading">
          {mode === 'fastest' ? 'Fastest to gstack' : 'Most gstack'}
        </h2>
      </div>
      <p>{visibleEpisodes.length} of {dataset.episodes.length} episodes</p>
    </div>
    <RankingControls bind:mode bind:filter bind:query />
    <Leaderboard episodes={visibleEpisodes} allEpisodes={dataset.episodes} {mode} />
  </section>

  <section class="explainer">
    <div>
      <span class="eyebrow">Two measurements. No mystery score.</span>
      <h2>Simple enough to audit.</h2>
    </div>
    <div class="explainer-grid">
      <article>
        <span class="step">01</span>
        <h3>Find the first mention</h3>
        <p>We measure from the first second of the published audio, including intros and ads.</p>
      </article>
      <article>
        <span class="step">02</span>
        <h3>Count every explicit reference</h3>
        <p>Each accepted “gstack,” “g stack,” or clearly intended “gee stack” counts once.</p>
      </article>
      <article>
        <span class="step">03</span>
        <h3>Listen before publishing</h3>
        <p>Transcripts generate candidates. A human confirms the audio and exact timestamp.</p>
      </article>
    </div>
  </section>
</div>
