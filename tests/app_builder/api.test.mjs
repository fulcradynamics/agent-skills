import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { event } from './fixtures.mjs';
const root = new URL('../../skills/build-and-deploy-a-web-app/references/svelte/', import.meta.url);
const load = async (file, imports) => {
  let code = readFileSync(new URL(file, root), 'utf8');
  for (const [pattern, replacement] of imports) code = code.replace(pattern, replacement);
  return import('data:text/javascript;base64,' + Buffer.from(code).toString('base64'));
};
const owner = await load('harness-owner.js', [[/import .* from '\$env\/dynamic\/private';/, "const privateEnv = { OWNER_USER_ID: 'owner' };"]]);
globalThis.harnessTestOwner = owner.isOwner;
const api = await load('harness-api-server.js', [
  [/import .* from '\$env\/dynamic\/public';/, "const env = { PUBLIC_FULCRA_API_ENDPOINT: 'https://fixture.invalid/' };"],
  [/import .* from '\$env\/dynamic\/private';/, "const privateEnv = { HARNESS_DATA_TYPE: 'Event/00000000-0000-4000-8000-000000000000' };"],
  [/import .* from '@sveltejs\/kit';/, 'const error = (status, message) => Object.assign(new Error(message), {status}); const json = data => Response.json(data);'],
  [/import .* from '\$lib\/api-client.js';/, 'const FulcraAPI = class {};'],
  [/import .* from '\$lib\/server\/harness-owner.js';/, 'const isOwner = globalThis.harnessTestOwner;'],
  [/from '\$lib\/harness-state.js'/, `from '${new URL('harness-state.js', root).href}'`]
]);
const token = user => `fixture.${Buffer.from(JSON.stringify({'fulcradynamics.com/userid': user})).toString('base64url')}.unverified`;
const request = (query = '', user = 'owner') => ({ cookies: {get: () => user ? token(user) : undefined}, url: new URL('https://fixture.invalid/api/harness/runs' + query), fetch: globalThis.fetch });
test('backend denies missing/nonowner tokens before upstream requests', async () => {
  await assert.rejects(api.GET_runs(request('', null)), {status: 401});
  await assert.rejects(api.GET_runs(request('', 'other')), {status: 403});
  assert.equal(owner.isOwner('broken'), false);
});
test('latest and ranges use configured type, JSONL and caller token; never arbitrary frontend scope', async () => {
  const calls = [];
  const fetch = async (url, options) => { calls.push([new URL(url), options]); return new Response(JSON.stringify(event()) + '\n'); };
  const response = await api.GET_runs({...request('?mode=latest&annotation_id=evil'), fetch});
  assert.deepEqual((await response.json()).records, [event()]);
  assert.equal(calls[0][0].pathname, '/data/v1/records');
  assert.equal(calls[0][0].searchParams.get('q'), '{__name__="Event/00000000-0000-4000-8000-000000000000"}');
  assert.equal(calls[0][1].headers.Authorization, `Bearer ${token('owner')}`);
  await api.GET_runs({...request('?start=2026-01-01T00:00:00Z&end=2026-01-01T01:00:00Z'), fetch});
  assert.match(calls[1][0].searchParams.get('q'), /\[3600s\]/);
});
test('upstream forged/expired token and errors are not empty successes', async () => {
  for (const status of [401, 403, 404, 500]) {
    await assert.rejects(api.GET_runs({...request('?mode=latest'), fetch: async () => new Response('', {status})}), {status: status < 404 ? status : 502});
  }
  await assert.rejects(api.GET_runs({...request('?mode=latest'), fetch: async () => new Response('{bad')}), {status: 502});
  await assert.rejects(api.GET_runs(request('?start=bad&end=bad')), {status: 400});
});
