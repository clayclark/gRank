<script lang="ts">
  import { formatTimestamp } from '$lib/format';
  import type { Mention } from '$lib/types';

  let {
    mentions,
    durationSeconds,
    youtubeUrl = null
  }: { mentions: Mention[]; durationSeconds: number; youtubeUrl?: string | null } = $props();

  function percent(startMs: number) {
    return Math.min(100, Math.max(0, (startMs / (durationSeconds * 1000)) * 100));
  }

  function laneOffset(index: number) {
    return [-66, -22, 22, 66][index % 4];
  }

  function timestampUrl(mention: Mention) {
    if (!youtubeUrl) return null;
    const separator = youtubeUrl.includes('?') ? '&' : '?';
    return `${youtubeUrl}${separator}t=${Math.floor(mention.startMs / 1000)}s`;
  }

  function revealMention(id: string) {
    const row = document.querySelector<HTMLElement>(`[data-mention-id="${id}"]`);
    row?.scrollIntoView({ behavior: 'smooth', block: 'center' });
    row?.focus({ preventScroll: true });
  }
</script>

<section class="timeline-section" aria-labelledby="timeline-title">
  <header class="timeline-intro">
    <h2 id="timeline-title">Where gstack appears</h2>
    <p>{mentions.length} accepted {mentions.length === 1 ? 'mention' : 'mentions'}</p>
  </header>

  {#if mentions.length > 0}
    <div class="evidence-reader">
      <div
        class="timeline-map"
        role="group"
        aria-label={`${mentions.length} gstack mentions across the episode`}
      >
        <span class="timeline-start">0:00</span>
        <div class="track">
          {#each mentions as mention, index (mention.id)}
            <button
              class="marker"
              style={`top: ${percent(mention.startMs)}%; left: calc(50% + ${laneOffset(index)}px); --marker-row: ${index % 4}`}
              aria-label={`Mention ${index + 1} at ${formatTimestamp(mention.startMs)}: ${mention.publicContext}`}
              onclick={() => revealMention(mention.id)}
            >
              <span class="marker-line"></span>
              <span class="tooltip" role="tooltip">
                <strong>{formatTimestamp(mention.startMs)}</strong>
                {mention.publicContext}
              </span>
            </button>
          {/each}
        </div>
        <span class="timeline-end">{formatTimestamp(durationSeconds * 1000)}</span>
      </div>

      <ol class="mention-list">
        {#each mentions as mention, index (mention.id)}
          <li data-mention-id={mention.id} tabindex="-1">
            <span class="mention-index">{String(index + 1).padStart(2, '0')}</span>
            <div>
              <strong>{formatTimestamp(mention.startMs)}</strong>
              <p>{mention.publicContext}</p>
            </div>
            {#if timestampUrl(mention)}
              <a href={timestampUrl(mention) ?? undefined} target="_blank" rel="noreferrer"
                >Watch timestamp</a
              >
            {/if}
          </li>
        {/each}
      </ol>
    </div>
  {:else}
    <div class="no-mentions">
      <strong>No accepted mentions.</strong>
      <p>
        {mentions.length === 0
          ? 'The reviewed episode contains no confirmed audible reference to gstack.'
          : ''}
      </p>
    </div>
  {/if}
</section>
