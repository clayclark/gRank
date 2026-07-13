<script lang="ts">
  import type { MentionFilter, RankMode } from '$lib/types';

  let {
    mode = $bindable(),
    filter = $bindable(),
    query = $bindable()
  }: { mode: RankMode; filter: MentionFilter; query: string } = $props();
</script>

<section class="controls" aria-label="Leaderboard controls">
  <div class="mode-switch" aria-label="Ranking mode">
    <button
      class:active={mode === 'fastest'}
      aria-pressed={mode === 'fastest'}
      onclick={() => (mode = 'fastest')}
    >
      Fastest to gstack
    </button>
    <button
      class:active={mode === 'most'}
      aria-pressed={mode === 'most'}
      onclick={() => (mode = 'most')}
    >
      Most gstack
    </button>
  </div>
  <label>
    <span class="sr-only">Search episodes</span>
    <input bind:value={query} type="search" placeholder="Search episodes" />
  </label>
  <label>
    <span class="sr-only">Filter by mention status</span>
    <select bind:value={filter}>
      <option value="all">All episodes</option>
      <option value="present">Has mentions</option>
      <option value="absent">No mention</option>
      <option value="pending">Pending review</option>
    </select>
  </label>
</section>
