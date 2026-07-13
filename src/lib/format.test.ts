import { describe, expect, it } from 'vitest';
import { episodeSummary } from './format';

describe('episodeSummary', () => {
  it('removes sponsor copy and chapter lists from show notes', () => {
    expect(
      episodeSummary(
        "A concise episode summary. Thank you to today's sponsors! Clerk https://example.com 00:40:49 - Topic"
      )
    ).toBe('A concise episode summary.');
  });

  it('keeps ordinary descriptions intact', () => {
    expect(episodeSummary('A short description with no appended boilerplate.')).toBe(
      'A short description with no appended boilerplate.'
    );
  });
});
