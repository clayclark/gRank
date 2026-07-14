import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
  preprocess: vitePreprocess(),
  kit: {
    inlineStyleThreshold: 25_000,
    csp: {
      mode: 'auto',
      directives: {
        'default-src': ['self'],
        'base-uri': ['self'],
        'connect-src': ['self'],
        'font-src': ['self'],
        'form-action': ['self'],
        'img-src': ['self', 'data:'],
        'object-src': ['none'],
        'script-src': ['self'],
        'style-src': [
          'self',
          'sha256-IRGtDaJoWUyd8zoPZ2Rl1Ad5ErPWovCmj1jXl1LdmQA=',
          'sha256-DpHesKLBZiQMvMgWVlgtXvKeSJwNJzi5fYtQiTHgiBE=',
          'sha256-HR6/MuuYfB8aijiNP5MPm3YOR8WqVmL7UkE3Q8OslTs='
        ],
        'style-src-attr': ['unsafe-inline'],
        'worker-src': ['self']
      }
    },
    adapter: adapter({
      pages: 'build',
      assets: 'build',
      fallback: undefined,
      precompress: true,
      strict: true
    })
  }
};

export default config;
