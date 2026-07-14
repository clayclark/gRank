<script lang="ts">
  import { formatTimestamp } from '$lib/format';
  import type { Mention } from '$lib/types';

  let { mentions, youtubeUrl = null }: { mentions: Mention[]; youtubeUrl?: string | null } =
    $props();

  function timestampUrl(mention: Mention) {
    if (!youtubeUrl) return null;
    const separator = youtubeUrl.includes('?') ? '&' : '?';
    return `${youtubeUrl}${separator}t=${Math.floor(mention.startMs / 1000)}s`;
  }
</script>

<section class="mentions-section" aria-labelledby="mentions-title">
  <header class="mentions-intro">
    <h2 id="mentions-title">Every gstack moment</h2>
    <p>{mentions.length} {mentions.length === 1 ? 'mention' : 'mentions'}</p>
  </header>

  {#if mentions.length > 0}
    <ol class="mention-list">
      {#each mentions as mention, index (mention.id)}
        <li>
          <span class="mention-index">{String(index + 1).padStart(2, '0')}</span>
          <div>
            <strong>{formatTimestamp(mention.startMs)}</strong>
            <p>{mention.publicContext}</p>
          </div>
          {#if timestampUrl(mention)}
            <a href={timestampUrl(mention) ?? undefined} target="_blank" rel="noreferrer"
              >Watch moment</a
            >
          {/if}
        </li>
      {/each}
    </ol>
  {:else}
    <p class="no-mentions">No gstack in this episode.</p>
  {/if}
</section>
