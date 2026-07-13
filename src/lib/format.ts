export function formatDuration(totalSeconds: number): string {
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = Math.floor(totalSeconds % 60);
  const mm = String(minutes).padStart(hours > 0 ? 2 : 1, '0');
  const ss = String(seconds).padStart(2, '0');
  return hours > 0 ? `${hours}:${mm}:${ss}` : `${mm}:${ss}`;
}

export function formatTimestamp(milliseconds: number | null): string {
  if (milliseconds === null) return 'No mention';
  return formatDuration(Math.round(milliseconds / 1000));
}

export function formatDate(value: string): string {
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    timeZone: 'UTC'
  }).format(new Date(value));
}

export function formatRate(value: number): string {
  return value.toFixed(value >= 10 ? 0 : 1);
}

export function episodeSummary(description: string): string {
  const normalized = description.replace(/\s+/g, ' ').trim();
  const stopPatterns = [
    /\bthank(?:s| you) to (?:this episode's|today's) sponsors?\b/i,
    /\bsources available\b/i,
    /\b\d{2}:\d{2}:\d{2}\b/
  ];
  const stop = Math.min(
    ...stopPatterns.map((pattern) => normalized.search(pattern)).filter((index) => index >= 0),
    normalized.length
  );
  const summary = normalized
    .slice(0, stop)
    .replace(/[\s,;:–—-]+$/, '')
    .trim();
  return summary.length >= 20 ? summary : normalized;
}
