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
  <link
    rel="preload"
    as="image"
    href="/images/grank-signal-hero.avif"
    type="image/avif"
    fetchpriority="high"
    media="(min-width: 721px)"
  />
</svelte:head>

<section class="signal-poster shell">
  <div class="poster-copy">
    <h1><span>How long until</span><span>they mention <em>gstack?</em></span></h1>
    <p>Every Nerd Snipe episode, ranked by its first transcript match and total gstack mentions.</p>
    <a class="hero-link" href="#leaderboard-heading">Inspect the evidence</a>
  </div>
  <figure class="poster-visual">
    <picture>
      <source srcset="/images/grank-signal-hero.avif" type="image/avif" />
      <img
        src="/images/grank-signal-hero.jpg"
        alt="A studio microphone beside transcript strips and a coral waveform ribbon"
        width="1200"
        height="640"
        fetchpriority="low"
      />
    </picture>
  </figure>
  <div class="poster-status">
    <span>{dataset.status === 'published' ? 'Published dataset' : 'Review in progress'}</span>
    <strong>{dataset.episodes.length} episodes</strong>
  </div>
</section>

<div class="signal-index shell">
  <aside class="signal-sidebar">
    <div class="signal-sidebar-heading">
      <span>Dataset pulse</span>
      <strong>{visibleEpisodes.length} shown</strong>
    </div>
    <SummaryStats episodes={dataset.episodes} generatedAt={dataset.generatedAt} />
  </aside>

  <section class="leaderboard-section" aria-labelledby="leaderboard-heading">
    <header class="leaderboard-masthead">
      <h2 id="leaderboard-heading">
        {mode === 'fastest' ? 'Fastest to gstack' : 'Most gstack'}
      </h2>
      <p>{visibleEpisodes.length} of {dataset.episodes.length} episodes</p>
    </header>
    <div class="control-dock">
      <RankingControls bind:mode bind:filter bind:query />
    </div>
    <Leaderboard episodes={visibleEpisodes} allEpisodes={dataset.episodes} {mode} />
  </section>
</div>

<section class="audit-notes shell">
  <header>
    <p class="kicker">Two measurements. No mystery score.</p>
    <h2>Simple enough to audit.</h2>
    <p>Each result resolves to transcript context, a timestamp, and the analyzed file.</p>
  </header>
  <div class="audit-sequence">
    <article>
      <h3>Find the first mention</h3>
      <p>The clock begins at the first second of the published file, including intros and ads.</p>
    </article>
    <article>
      <h3>Count every explicit reference</h3>
      <p>Each accepted “gstack,” “g stack,” or clearly intended “gee stack” counts once.</p>
    </article>
    <article>
      <h3>Cross-check before publishing</h3>
      <p>
        Exact transcript matches are accepted, generic stack references are rejected, and caption
        overlap remains as provenance.
      </p>
    </article>
  </div>
</section>
