import { test } from 'node:test';
import assert from 'node:assert/strict';
import { HarnessFeed } from '../../skills/build-and-deploy-a-web-app/references/svelte/harness-feed.js';
import { event } from './fixtures.mjs';

for (const action of ['open old run', 'load older']) {
  test(`delayed poll preserves queued ${action} request`, async () => {
    const old = event();
    const terminal = event({ id: 'old-end', step: 'RUN_END', outcome: 'passed', start_time: '2026-01-01T00:14:00Z' });
    const latest = event({ id: 'new', run_id: 'run-b', run_start: '2026-06-01T00:00:00Z', start_time: '2026-06-01T00:00:01Z' });
    let releasePoll;
    const gate = new Promise(resolve => { releasePoll = resolve; });
    const calls = [];
    let active = 0;
    let maxActive = 0;
    const feed = new HarnessFeed(async params => {
      calls.push(params);
      maxActive = Math.max(maxActive, ++active);
      try {
        if (params.mode) { await gate; return [latest]; }
        return params.start === latest.run_start ? [latest] : [old, terminal];
      } finally { active--; }
    });
    feed.events = [old, latest];
    feed.current = latest.run_id;
    feed.selected = latest.run_id;
    const poll = feed.refresh('2026-06-01T00:01:00Z');
    // Mirror the dashboard: selection is pinned immediately; older's cursor
    // advances only after the requested range has actually loaded.
    feed.selected = old.run_id;
    let historyEnd = '2026-02-01T00:00:00Z';
    const start = action === 'open old run' ? old.run_start : '2025-12-01T00:00:00Z';
    const end = action === 'open old run' ? '2026-06-01T00:01:00Z' : historyEnd;
    const history = feed.history(start, end).then(loaded => {
      if (loaded && action === 'load older') historyEnd = start;
      return loaded;
    });
    assert.equal(calls.length, 1);
    releasePoll();
    await poll;
    assert.equal(await history, true);
    assert.ok(calls.some(params => params.start === start && params.end === end));
    assert.ok(feed.events.some(row => row.id === terminal.id));
    assert.equal(feed.selected, old.run_id);
    assert.equal(maxActive, 1);
    assert.equal(feed.busy, false);
    if (action === 'load older') assert.equal(historyEnd, start);
  });
}

test('queued history survives poll and history errors without advancing failed cursors', async () => {
  let releasePoll;
  const gate = new Promise(resolve => { releasePoll = resolve; });
  const calls = [];
  const feed = new HarnessFeed(async params => {
    calls.push(params);
    if (params.mode) { await gate; throw new Error('poll offline'); }
    if (params.start === 'bad') throw new Error('history offline');
    return [event({ id: params.start })];
  });
  feed.lastRead = '2026-01-01T00:00:00Z';
  feed.selected = 'run-a';
  const poll = assert.rejects(feed.refresh(), /poll offline/);
  let historyEnd = 'unchanged';
  const failed = assert.rejects(feed.history('bad', 'end').then(() => {
    historyEnd = 'bad';
  }), /history offline/);
  const first = feed.history('first', 'end');
  const second = feed.history('second', 'end');
  await feed.refresh(); // A cadence tick must not bypass queued user requests.
  assert.equal(calls.length, 1);
  releasePoll();
  await Promise.all([poll, failed, first, second]);
  assert.deepEqual(calls, [{ mode: 'latest' }, { start: 'bad', end: 'end' }, { start: 'first', end: 'end' }, { start: 'second', end: 'end' }]);
  assert.equal(historyEnd, 'unchanged');
  assert.equal(feed.lastRead, '2026-01-01T00:00:00Z');
  assert.equal(feed.selected, 'run-a');
  assert.equal(feed.busy, false);
  assert.deepEqual(feed.events.map(row => row.id), ['first', 'second']);
});

test('latest discovers old idle run, incremental polling reconciles delayed events, history remains selected', async () => {
  const calls = [];
  let latest = event();
  let rows = [latest];
  const feed = new HarnessFeed(async params => { calls.push(params); return params.mode ? [latest] : rows; });
  await feed.refresh('2026-06-01T00:00:00Z');
  assert.equal(calls[0].mode, 'latest');
  assert.equal(calls[1].start, latest.run_start);
  feed.selected = 'run-a';
  latest = event({id: 'b', run_id: 'run-b', run_start: '2026-06-01T00:00:00Z', start_time: '2026-06-01T00:00:01Z'});
  rows = [latest];
  await feed.refresh('2026-06-01T00:00:10Z');
  assert.equal(feed.selected, 'run-a');
  await feed.refresh('2026-06-01T00:05:00Z');
  assert.equal(Date.parse(calls.at(-1).start), Date.parse(latest.run_start));
  rows = [latest, event({id: 'late', run_id: 'run-b', run_start: latest.run_start})];
  for (let i = 0; i < 12; i++) await feed.refresh('2026-06-01T00:10:00Z');
  assert.ok(calls.some(p => p.start === latest.run_start));
  assert.ok(feed.events.some(e => e.id === 'late'));
  await feed.history('2025-01-01T00:00:00Z', '2026-01-01T00:00:00Z');
  assert.equal(feed.selected, 'run-a');
});
test('failed poll retains data/cursor and concurrent refresh is skipped', async () => {
  let fail = false;
  let calls = 0;
  const feed = new HarnessFeed(async () => { calls++; if (fail) throw new Error('offline'); return [event()]; });
  await feed.refresh('2026-01-01T00:01:00Z');
  fail = true;
  await assert.rejects(feed.refresh('2026-01-01T00:02:00Z'), /offline/);
  assert.equal(feed.lastRead, '2026-01-01T00:01:00Z');
  assert.equal(feed.events.length, 1);
  feed.busy = true;
  const before = calls;
  await feed.refresh();
  assert.equal(calls, before);
});

test('range-aware fixture exposes late event only at full reconciliation', async () => {
  const recent = event({id: 'recent', start_time: '2026-01-01T00:10:00Z'});
  const late = event({id: 'delayed', start_time: '2026-01-01T00:01:00Z'});
  let visible = [recent];
  const feed = new HarnessFeed(async params => params.mode ? [recent] : visible.filter(e => Date.parse(e.start_time) >= Date.parse(params.start)));
  await feed.refresh('2026-01-01T00:11:00Z');
  visible = [recent, late];
  await feed.refresh('2026-01-01T00:11:05Z');
  assert.equal(feed.events.length, 1);
  for (let i = 0; i < 11; i++) await feed.refresh('2026-01-01T00:12:00Z');
  assert.deepEqual(feed.events.map(e => e.id), ['delayed', 'recent']);
});
