import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vitest/config';
import Ajv2020 from 'ajv/dist/2020.js';
import addFormats from 'ajv-formats';
import dataset from './data/grank.json';
import schema from './schema/grank.schema.json';

const ajv = new Ajv2020({ allErrors: true, strict: false });
addFormats(ajv);
const validateDataset = ajv.compile(schema);

if (!validateDataset(dataset)) {
  const details = validateDataset.errors
    ?.map((error) => `${error.instancePath} ${error.message}`)
    .join('; ');
  throw new Error(`Invalid gRank dataset: ${details}`);
}

export default defineConfig({
  plugins: [sveltekit()],
  test: {
    include: ['src/**/*.test.ts']
  }
});
