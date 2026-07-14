import datasetJson from '../../data/grank.json';
import type { GrankDataset } from './types';

export const dataset = datasetJson as GrankDataset;

export function findEpisode(slug: string) {
  return dataset.episodes.find((episode) => episode.slug === slug);
}
