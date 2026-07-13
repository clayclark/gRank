import { error } from '@sveltejs/kit';
import { dataset, findEpisode } from '$lib/data';
import { metricRank } from '$lib/ranking';
import type { EntryGenerator, PageLoad } from './$types';

export const entries: EntryGenerator = () => {
  return dataset.episodes.map((episode) => ({ slug: episode.slug }));
};

export const load: PageLoad = ({ params }) => {
  const episode = findEpisode(params.slug);
  if (!episode) error(404, 'Episode not found');
  return {
    episode,
    fastestRank: metricRank(dataset.episodes, episode, 'fastest'),
    mostRank: metricRank(dataset.episodes, episode, 'most')
  };
};
