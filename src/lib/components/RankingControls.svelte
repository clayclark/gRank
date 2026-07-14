<script lang="ts">
  import type { RankMode } from '$lib/types';

  let { mode = $bindable(), query = $bindable() }: { mode: RankMode; query: string } = $props();
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
    <span>Find an episode</span>
    <input bind:value={query} type="search" placeholder="Search by title" />
  </label>
</section>
