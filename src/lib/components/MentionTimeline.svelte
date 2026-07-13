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

  function timestampUrl(mention: Mention) {
    if (!youtubeUrl) return null;
    const separator = youtubeUrl.includes('?') ? '&' : '?';
    return `${youtubeUrl}${separator}t=${Math.floor(mention.startMs / 1000)}s`;
  }
</script>

<section class="timeline-section" aria-labelledby="timeline-title">
  <div class="section-heading">
    <div>
      <span class="eyebrow">Episode timeline</span>
      <h2 id="timeline-title">Where gstack appears</h2>
    </div>
    <span>{mentions.length} accepted {mentions.length === 1 ? 'mention' : 'mentions'}</span>
  </div>

  {#if mentions.length > 0}
    <div
      class="timeline"
      role="group"
      aria-label={`${mentions.length} gstack mentions across the episode`}
    >
      <span class="timeline-start">0:00</span>
      <div class="track">
        {#each mentions as mention, index (mention.id)}
          <button
            class="marker"
            style={`left: ${percent(mention.startMs)}%`}
            aria-label={`Mention ${index + 1} at ${formatTimestamp(mention.startMs)}: ${mention.publicContext}`}
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
        <li>
          <span class="mention-index">{String(index + 1).padStart(2, '0')}</span>
          <div>
            <strong>{formatTimestamp(mention.startMs)}</strong>
            <p>{mention.publicContext}</p>
          </div>
          {#if timestampUrl(mention)}
            <a href={timestampUrl(mention) ?? undefined} target="_blank" rel="noreferrer">Watch ↗</a
            >
          {/if}
        </li>
      {/each}
    </ol>
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
