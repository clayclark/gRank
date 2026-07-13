import type { Episode, RankMode } from './types';

function publishedTime(episode: Episode): number {
  return new Date(episode.publishedAt).getTime();
}

export function compareEpisodes(a: Episode, b: Episode, mode: RankMode): number {
  const aComplete = a.review.status === 'complete';
  const bComplete = b.review.status === 'complete';
  if (aComplete !== bComplete) return aComplete ? -1 : 1;

  if (mode === 'fastest') {
    const aTime = a.metrics.firstMentionMs;
    const bTime = b.metrics.firstMentionMs;
    if ((aTime === null) !== (bTime === null)) return aTime === null ? 1 : -1;
    if (aTime !== bTime) return (aTime ?? Infinity) - (bTime ?? Infinity);
    if (a.metrics.mentionCount !== b.metrics.mentionCount) {
      return b.metrics.mentionCount - a.metrics.mentionCount;
    }
  } else {
    if (a.metrics.mentionCount !== b.metrics.mentionCount) {
      return b.metrics.mentionCount - a.metrics.mentionCount;
    }
    const aTime = a.metrics.firstMentionMs;
    const bTime = b.metrics.firstMentionMs;
    if ((aTime === null) !== (bTime === null)) return aTime === null ? 1 : -1;
    if (aTime !== bTime) return (aTime ?? Infinity) - (bTime ?? Infinity);
  }

  if (publishedTime(a) !== publishedTime(b)) return publishedTime(b) - publishedTime(a);
  return a.guid.localeCompare(b.guid);
}

export function rankEpisodes(episodes: Episode[], mode: RankMode): Episode[] {
  return [...episodes].sort((a, b) => compareEpisodes(a, b, mode));
}

export function metricRank(episodes: Episode[], episode: Episode, mode: RankMode): number | null {
  if (episode.review.status !== 'complete') return null;
  const completed = episodes.filter((item) => item.review.status === 'complete');
  const values = completed.map((item) =>
    mode === 'fastest' ? item.metrics.firstMentionMs : item.metrics.mentionCount
  );
  const target = mode === 'fastest' ? episode.metrics.firstMentionMs : episode.metrics.mentionCount;
  if (mode === 'fastest' && target === null) return null;
  const better = values.filter((value) => {
    if (mode === 'fastest') return value !== null && value < (target as number);
    return (value as number) > (target as number);
  });
  return new Set(better).size + 1;
}
