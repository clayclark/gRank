export type DatasetStatus = 'draft' | 'published';
export type ReviewStatus = 'pending' | 'complete';

export interface Mention {
  id: string;
  startMs: number;
  endMs: number;
  detectedText: string;
  publicContext: string;
  source: 'mlx' | 'youtube' | 'metadata' | 'manual';
  sources: ('mlx' | 'youtube' | 'metadata' | 'manual')[];
  reviewConfidence: number;
}

export interface Episode {
  guid: string;
  slug: string;
  title: string;
  description?: string;
  episodeNumber: number | null;
  seasonNumber: number | null;
  publishedAt: string;
  durationSeconds: number;
  episodeUrl: string;
  imageUrl: string | null;
  youtube?: {
    videoId: string;
    watchUrl: string;
    matchStatus: 'automatic' | 'reviewed';
    captionSource?: string | null;
  } | null;
  audio: {
    enclosureUrl: string;
    declaredBytes: number | null;
    analyzedBytes?: number | null;
    sha256?: string | null;
  };
  review: {
    status: ReviewStatus;
    completedAt: string | null;
    method: 'automated-transcript-consensus' | 'human-audio' | null;
    policyVersion: string | null;
    evidenceSummary: {
      candidateCount: number;
      acceptedCount: number;
      rejectedCount: number;
      duplicateCount: number;
      corroboratedAcceptedCount: number;
      singleSourceAcceptedCount: number;
    } | null;
    transcriptionModel: string | null;
    transcriptionConfigHash: string | null;
  };
  mentions: Mention[];
  metrics: {
    firstMentionMs: number | null;
    mentionCount: number;
    mentionsPerHour: number;
  };
}

export interface GrankDataset {
  schemaVersion: 1;
  status: DatasetStatus;
  generatedAt: string;
  source: {
    feedUrl: string;
    youtubeChannelUrl: string;
    feedLastBuildDate: string | null;
    catalogEpisodeCount: number;
  };
  methodology: {
    definitionVersion: string;
    detectorVersion: string;
    reviewPolicyVersion: string;
    reviewMethod: 'automated-transcript-consensus';
  };
  episodes: Episode[];
}

export type RankMode = 'fastest' | 'most';
export type MentionFilter = 'all' | 'present' | 'absent' | 'pending';
