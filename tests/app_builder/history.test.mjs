import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { HarnessFeed } from '../../skills/build-and-deploy-a-web-app/references/svelte/harness-feed.js';
import { event } from './fixtures.mjs';

const now = '2026-06-15T12:00:00.000Z';
const week = '2026-06-08T12:00:00.000Z';
for (const [name, latest, start] of [
  ['recent current', event({ run_start: '2026-06-14T00:00:00Z' }), week],
  ['older current', event(), '2026-01-01T00:00:00Z'],
  ['empty latest', null, week]
]) {
  test(`opening loads at least a week and full current run: ${name}`, async () => {
    const calls = [];
    const historical = event({ id: 'historical', run_id: 'history', run_start: week, start_time: week });
    const feed = new HarnessFeed(async params => {
      calls.push(params);
      return params.mode ? (latest ? [latest] : []) : [historical];
    });
    await feed.refresh(now);
    assert.deepEqual(calls, [{ mode: 'latest' }, { start, end: now }]);
    assert.equal(feed.historyStart, start);
    assert.ok(feed.events.some(row => row.id === 'historical'));
  });
}

test('initial range failure commits no cursor/data and retry loads the week', async () => {
  let fail = true;
  const calls = [];
  const feed = new HarnessFeed(async params => {
    calls.push(params);
    if (params.mode) return [];
    if (fail) throw new Error('range offline');
    return [];
  });
  await assert.rejects(feed.refresh(now), /range offline/);
  assert.equal(feed.historyStart, null);
  assert.equal(feed.lastRead, null);
  assert.deepEqual(feed.events, []);
  assert.equal(feed.busy, false);
  fail = false;
  await feed.refresh(now);
  assert.equal(feed.historyStart, week);
  assert.deepEqual(calls.at(-1), { start: week, end: now });
});

test('older paging commits only successful boundaries and pins selection across polls', async () => {
  let fail = false;
  const calls = [];
  const feed = new HarnessFeed(async params => {
    calls.push(params);
    if (fail) throw new Error('older offline');
    return params.mode ? [event({ run_start: now })] : [];
  });
  await feed.refresh(now);
  feed.selected = 'run-a';
  fail = true;
  await assert.rejects(feed.loadOlder(), /older offline/);
  assert.equal(feed.historyStart, week);
  fail = false;
  await feed.loadOlder();
  assert.deepEqual(calls.at(-1), { start: '2026-05-09T12:00:00.000Z', end: week });
  assert.equal(feed.historyStart, '2026-05-09T12:00:00.000Z');
  await feed.history('2025-01-01T00:00:00Z', now);
  await feed.refresh(now);
  assert.equal(feed.historyStart, '2026-05-09T12:00:00.000Z');
  assert.equal(feed.selected, 'run-a');
});

test('queued double older clicks calculate consecutive windows under the lock', async () => {
  let release;
  const gate = new Promise(resolve => { release = resolve; });
  const calls = [];
  const feed = new HarnessFeed(async params => {
    calls.push(params);
    if (params.mode) await gate;
    return [];
  });
  const poll = feed.refresh(now);
  const first = feed.loadOlder();
  const second = feed.loadOlder();
  assert.equal(calls.length, 1);
  release();
  await Promise.all([poll, first, second]);
  assert.deepEqual(calls.slice(1), [
    { start: week, end: now },
    { start: '2026-05-09T12:00:00.000Z', end: week },
    { start: '2026-04-09T12:00:00.000Z', end: '2026-05-09T12:00:00.000Z' }
  ]);
  assert.equal(feed.historyStart, '2026-04-09T12:00:00.000Z');
  assert.equal(feed.busy, false);
});

test('older before successful opening cannot claim a loaded boundary', async () => {
  const feed = new HarnessFeed(async () => { throw new Error('must not query'); });
  await assert.rejects(feed.loadOlder(), /initial history/i);
  assert.equal(feed.historyStart, null);
  assert.equal(feed.busy, false);
});

test('dashboard distinguishes muted loaded boundary from errors and labels select accessibly', () => {
  const source = readFileSync(new URL('../../skills/build-and-deploy-a-web-app/references/svelte/HarnessDashboard.svelte', import.meta.url), 'utf8');
  assert.match(source, /<select aria-label="Run"/);
  assert.doesNotMatch(source, /<label>Run/);
  assert.match(source, /class="muted" aria-live="polite">History loaded from/);
  assert.match(source, /role="alert" class="attention">\{historyMessage\}/);
  assert.match(source, /historyStart = feed.historyStart/);
  assert.match(source, /await feed.loadOlder\(\)/);
  assert.match(source, /\.run-controls select \{ flex: 1 1 16rem; min-width: 0; \}/);
  assert.match(source, /\.run-controls > (?:h2|select|button)/);
});
