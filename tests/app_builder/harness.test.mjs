import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { parseRecords, mergeEvents, groupRuns, pollStart, selectedRunId, recordsQuery } from '../../skills/build-and-deploy-a-web-app/references/svelte/harness-state.js';

import { event } from './fixtures.mjs';
test('v1 JSONL parser rejects malformed records rather than showing empty success', () => {
  assert.deepEqual(parseRecords(JSON.stringify(event()) + '\n'), [event()]);
  assert.deepEqual(parseRecords(''), []);
  assert.throws(() => parseRecords('{broken'));
  assert.throws(() => parseRecords(JSON.stringify({ note: '{}' })));
  for (const invalid of [null, event({deadline: 'bad'}), event({step: null}), event({open_issues: [42]}), event({resources: [null]})]) {
    assert.throws(() => parseRecords(JSON.stringify(invalid)));
  }
});
test('actual timeline preserves evidence and explicit outcomes, never missing-generation completion', () => {
  const events = mergeEvents([event()], [event(), event({ id: 'b', step: 'RUN_END', outcome: 'retry-needed', start_time: '2026-01-01T00:00:02Z' })]);
  assert.equal(events.length, 2);
  assert.equal(groupRuns([event()])[0].outcome, 'running');
  assert.equal(groupRuns(events)[0].outcome, 'retry-needed');
});
test('overlap plus periodic run-relative reconciliation recovers arbitrarily late events', () => {
  const start = event().run_start;
  assert.equal(pollStart(start, '2026-01-01T00:10:00Z', false), '2026-01-01T00:08:00.000Z');
  assert.equal(pollStart(start, '2026-01-01T00:10:00Z', true), start);
  assert.equal(mergeEvents([event({ id: 'new' })], [event({ id: 'late', start_time: start })]).length, 2);
});
test('history selection remains pinned as new runs arrive', () => {
  assert.equal(selectedRunId('old', [{ run_id: 'new' }, { run_id: 'old' }]), 'old');
  assert.equal(selectedRunId(null, [{ run_id: 'new' }]), 'new');
});
test('public v1 query contract uses instant selector and outward-rounded range seconds', () => {
  const type = 'Event/00000000-0000-4000-8000-000000000000';
  assert.equal(recordsQuery(type), `{__name__="${type}"}`);
  assert.equal(recordsQuery(type, '2026-01-01T00:00:00.500Z', '2026-01-01T00:00:02.500Z'), `{__name__="${type}"}[3s] @ 1767225603`);
  assert.throws(() => recordsQuery('Event/evil"'));
  assert.throws(() => recordsQuery(type, 'bad', 'bad'));
});
test('reusable additional-field schema declares retained state, no note payload or base overrides', () => {
  const schema = JSON.parse(readFileSync(new URL('../../skills/build-and-deploy-a-web-app/references/harness-event-fields.json', import.meta.url)));
  for (const key of Object.keys(event()).filter(k => !['id', 'start_time', 'end_time'].includes(k))) {
    assert.ok(schema.properties[key], key);
    assert.ok(schema.required.includes(key), key);
  }
  assert.equal(schema.properties.note, undefined);
  assert.equal(schema.properties.start_time, undefined);
  assert.deepEqual(schema.properties.outcome.enum, ['running', 'passed', 'retry-needed', 'stopped', 'escalated']);
});
