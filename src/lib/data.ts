import Ajv2020 from 'ajv/dist/2020.js';
import addFormats from 'ajv-formats';
import datasetJson from '../../data/grank.json';
import schema from '../../schema/grank.schema.json';
import type { GrankDataset } from './types';

const ajv = new Ajv2020({ allErrors: true, strict: false });
addFormats(ajv);
const validate = ajv.compile(schema);

if (!validate(datasetJson)) {
  const details = validate.errors
    ?.map((error) => `${error.instancePath} ${error.message}`)
    .join('; ');
  throw new Error(`Invalid gRank dataset: ${details}`);
}

export const dataset = datasetJson as GrankDataset;

export function findEpisode(slug: string) {
  return dataset.episodes.find((episode) => episode.slug === slug);
}
