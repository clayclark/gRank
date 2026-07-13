import { describe, expect, it } from 'vitest';
import { metricRank, rankEpisodes } from './ranking';
import type { Episode } from './types';

function episode(guid: string, firstMentionMs: number | null, mentionCount: number): Episode {
  return {
    guid,
    slug: guid,
    title: guid,
    episodeNumber: null,
    seasonNumber: null,
    publishedAt: '2026-01-01T00:00:00Z',
    durationSeconds: 3600,
    episodeUrl: `https://example.com/${guid}`,
    imageUrl: null,
    audio: { enclosureUrl: `https://example.com/${guid}.mp3`, declaredBytes: null },
    review: {
      status: 'complete',
      completedAt: '2026-01-02T00:00:00Z',
      transcriptionModel: 'test',
      transcriptionConfigHash: 'test'
    },
    mentions: [],
    metrics: { firstMentionMs, mentionCount, mentionsPerHour: mentionCount }
  };
}

describe('rankEpisodes', () => {
  const episodes = [
    episode('none', null, 0),
    episode('slow', 20_000, 4),
    episode('fast', 5_000, 1)
  ];

  it('sorts earliest accepted mention first', () => {
    expect(rankEpisodes(episodes, 'fastest').map((item) => item.guid)).toEqual([
      'fast',
      'slow',
      'none'
    ]);
  });

  it('sorts highest mention count first', () => {
    expect(rankEpisodes(episodes, 'most').map((item) => item.guid)).toEqual([
      'slow',
      'fast',
      'none'
    ]);
  });

  it('uses competition ranks for equal metric values', () => {
    const tied = [...episodes, episode('also-fast', 5_000, 3)];
    expect(metricRank(tied, tied[2], 'fastest')).toBe(1);
    expect(metricRank(tied, tied[3], 'fastest')).toBe(1);
  });
});
