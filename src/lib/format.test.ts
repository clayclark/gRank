import { describe, expect, it } from 'vitest';
import { formatDuration, formatTimestamp } from './format';

describe('time formatting', () => {
  it('formats episode durations', () => {
    expect(formatDuration(3723)).toBe('1:02:03');
  });

  it('uses the canonical zero-result label', () => {
    expect(formatTimestamp(null)).toBe('No gstack');
  });
});
