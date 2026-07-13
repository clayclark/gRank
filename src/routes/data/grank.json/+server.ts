import { json } from '@sveltejs/kit';
import { dataset } from '$lib/data';

export const prerender = true;

export function GET() {
  return json(dataset, {
    headers: { 'cache-control': 'public, max-age=3600' }
  });
}
