import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as state from '../../skills/build-and-deploy-a-web-app/references/svelte/harness-state.js';
import { event } from './fixtures.mjs';

const events = (...items) => items.map((item, i) => event({
  id: `event-${i}`, start_time: `2026-01-01T00:00:${String(i + 1).padStart(2, '0')}Z`, ...item
}));
test('Nurse activity uses original records, preserves attempts and only confirms continuation from a linked run', () => {
  const records = events(
    { role: 'Nurse', step: 'Inspect dashboard', status: 'failed' },
    { role: 'Nurse', step: 'Repair configuration', status: 'started' },
    { role: 'Nurse', step: 'Repair configuration', status: 'completed' },
    { role: 'Nurse', step: 'Repair configuration', status: 'started' }
  );
  const flow = state.runFlow(records);
  assert.equal(flow.current, 'nurse');
  assert.equal(flow.nurseSteps.length, 3, 'a later started record is a new action, not a rewrite of completed history');
  assert.equal(flow.nurseSteps[0].state, 'failed');
  assert.equal(flow.nurseSteps[1].state, 'done');
  assert.equal(flow.nurseSteps[2].state, 'active');
  assert.equal(flow.nurseSteps[1].id, records[1].id, 'stable selection as a started action completes');
  assert.deepEqual(flow.nurseSteps[1].events, records.slice(1, 3));
  assert.equal(flow.nurseOutcomes[0].state, 'pending');
  const next = event({ id: 'next', run_id: 'run-b', previous_run_id: 'run-a', step: 'RUN_START' });
  const linked = state.runFlow(records, [...records, next]);
  assert.equal(linked.nurseOutcomes[0].state, 'done');
  assert.equal(linked.nurseOutcomes[1].state, 'skipped');
  const escalated = state.runFlow([...records, event({ id: 'end', start_time: '2026-01-01T00:01:00Z', step: 'RUN_END', outcome: 'escalated' })]);
  assert.equal(escalated.nurseOutcomes[0].state, 'skipped');
  assert.equal(escalated.nurseOutcomes[1].state, 'attention');
  assert.ok(escalated.cells.every(cell => cell.state !== 'active'), 'closed attempts cannot still pulse');
});

test('Nurse results resolve outstanding actions across interleaved activity without merging later attempts', () => {
  const records = events(
    { role: 'Nurse', step: 'Inspect worker', status: 'started' },
    { role: 'Generator', step: 'GENERATE', status: 'started' },
    { role: 'Nurse', step: 'Inspect configuration', status: 'started' },
    { role: 'Nurse', step: 'Inspect worker', status: 'completed' },
    { role: 'Nurse', step: 'Inspect worker', status: 'started' },
    { role: 'Nurse', step: 'Inspect configuration', status: 'failed' }
  );
  const flow = state.runFlow(records);
  assert.equal(flow.nurseSteps.length, 3);
  assert.deepEqual(flow.nurseSteps.map(action => action.state), ['done', 'failed', 'active']);
  assert.equal(flow.nurseSteps[0].id, records[0].id, 'selection keeps its original action ID');
  assert.deepEqual(flow.nurseSteps[0].events, [records[0], records[3]]);
  assert.deepEqual(flow.nurseSteps[1].events, [records[2], records[5]]);
  assert.deepEqual(flow.nurseSteps[2].events, [records[4]], 'a later attempt stays separate');
});

test('interleaved Nurse starts retain separate action IDs while consecutive progress stays grouped', () => {
  const records = events(
    { role: 'Nurse', step: 'Inspect worker', status: 'started' },
    { role: 'Generator', step: 'GENERATE', status: 'started' },
    { role: 'Nurse', step: 'Inspect worker', status: 'started' },
    { role: 'Nurse', step: 'Inspect worker', status: 'started' },
    { role: 'Nurse', step: 'Inspect worker', status: 'completed' }
  );
  const flow = state.runFlow(records);
  assert.equal(flow.nurseSteps.length, 2);
  assert.equal(flow.nurseSteps[0].id, records[0].id);
  assert.deepEqual(flow.nurseSteps[0].events, [records[0]]);
  assert.equal(flow.nurseSteps[0].state, 'active', 'an unmatched earlier start has no result');
  assert.equal(flow.nurseSteps[1].id, records[2].id);
  assert.deepEqual(flow.nurseSteps[1].events, records.slice(2));
  assert.equal(flow.nurseSteps[1].state, 'done');
});

test('branch styling uses recorded transitions, not absence, and retains unfamiliar events', () => {
  const records = events(
    { step: 'CHECK', status: 'started', tier: 'focused' },
    { step: 'CHECK', tier: 'focused' },
    { step: 'MARK_COMPLETE', tier: 'focused' },
    { step: 'RUN_END', outcome: 'passed', tier: 'focused' },
    { step: 'EXTRA_OBSERVATION', outcome: 'passed', tier: 'focused' }
  );
  const flow = state.runFlow(records);
  assert.equal(cell(flow, 'review').state, 'skipped');
  assert.equal(cell(flow, 'unfinished').state, 'skipped');
  assert.equal(cell(flow, 'finish').state, 'pending');
  assert.equal(cell(state.runFlow(records.slice(0, 1)), 'review').state, 'pending');
  assert.deepEqual(flow.otherEvents, [records.at(-1)]);
  const both = state.runFlow(events({ step: 'CHECK' }, { step: 'REVIEW' }, { step: 'RUN_END', outcome: 'passed' }));
  assert.equal(cell(both, 'check').state, 'done');
  assert.equal(cell(both, 'review').state, 'done');
  const done = state.runFlow([...records, event({ id: 'project', start_time: '2026-01-01T00:01:00Z', step: 'PROJECT_COMPLETE', outcome: 'passed' })]);
  assert.equal(cell(done, 'finish').state, 'done');
  assert.equal(cell(done, 'continue').state, 'skipped');
  const wrongProject = event({ id: 'new', step: 'RUN_START', run_id: 'run-b', project_id: 'other', previous_run_id: 'run-a' });
  assert.equal(cell(state.runFlow(records, [...records, wrongProject]), 'continue').state, 'pending');
});

test('finalization failure stays failed until verified closure, including Nurse bookkeeping', () => {
  const records = events(
    { step: 'RUN_END', outcome: 'passed' },
    { step: 'BOOKKEEPING', role: 'Nurse', status: 'failed', outcome: 'passed', bookkeeping: 'pending' }
  );
  assert.equal(cell(state.runFlow(records), 'finalize').state, 'failed');
  const repair = [...records, event({ id: 'repair', start_time: '2026-01-01T00:01:00Z', role: 'Nurse', step: 'BOOKKEEPING', outcome: 'passed', bookkeeping: 'complete' })];
  assert.equal(cell(state.runFlow(repair), 'finalize').state, 'done');
  assert.deepEqual(cell(state.runFlow(repair), 'finalize').events, repair);
});

test('resource records do not complete Build and arbitrary step names remain evidence', () => {
  const records = events({ step: 'GENERATE', status: 'started' }, { step: 'RESOURCE_CREATED' });
  assert.equal(cell(state.runFlow(records), 'build').state, 'active');
  assert.deepEqual(cell(state.runFlow(records), 'build').events, records);
  for (const step of ['constructor', 'toString', '__proto__']) {
    const record = event({ step, role: 'Nurse' });
    assert.equal(state.runFlow([record]).nurseSteps[0].label, step);
  }
});

test('a later continuation preserves earlier escalation evidence', () => {
  const records = events({ step: 'RUN_END', outcome: 'escalated' });
  const next = event({ id: 'next', run_id: 'run-b', previous_run_id: 'run-a', step: 'RUN_START' });
  const flow = state.runFlow(records, [...records, next]);
  assert.equal(flow.nurseOutcomes[0].state, 'done');
  assert.equal(flow.nurseOutcomes[1].state, 'attention');
  assert.deepEqual(flow.nurseOutcomes[1].events, records);
});

test('unsuccessful completion preserves the attempted path and confirms unfinished work', () => {
  for (const status of ['failed', 'started']) {
    const records = events(
      { step: 'CHECK' },
      { step: 'MARK_COMPLETE', status },
      { step: 'RUN_END', outcome: 'retry-needed' },
      { step: 'BOOKKEEPING', outcome: 'retry-needed', bookkeeping: 'complete' }
    );
    const flow = state.runFlow(records);
    assert.equal(cell(flow, 'unfinished').state, 'done');
    assert.deepEqual(cell(flow, 'unfinished').events, [records[2]]);
    assert.equal(cell(flow, 'complete').state, status === 'failed' ? 'failed' : 'pending');
    assert.deepEqual(cell(flow, 'complete').events, [records[1]]);
    assert.equal(cell(flow, 'finalize').state, 'done');
  }
});

const cell = (flow, id) => flow.cells.find(cell => cell.id === id);

for (const outcome of ['stopped', 'retry-needed', 'escalated']) {
  test(`${outcome} awaits continuation without claiming a worker started`, () => {
    const records = events({ step: 'RUN_END', outcome }, { step: 'BOOKKEEPING', outcome, bookkeeping: 'complete' });
    const flow = state.runFlow(records);
    assert.equal(cell(flow, 'continue').state, outcome === 'escalated' ? 'attention' : 'waiting');
    assert.match(cell(flow, 'continue').status, /not started/i);
    assert.equal(cell(flow, 'finish').state, 'skipped');
    const unrelated = event({ id: 'other', step: 'RUN_START', run_id: 'other' });
    const repair = event({ id: 'repair', role: 'Nurse', step: 'Repair configuration' });
    assert.notEqual(cell(state.runFlow(records, [...records, unrelated, repair]), 'continue').state, 'done');
    const linked = event({ id: 'next', step: 'RUN_START', run_id: 'run-b', previous_run_id: 'run-a' });
    assert.equal(cell(state.runFlow(records, [...records, linked]), 'continue').status, 'Linked retry started');
  });
}

test('insufficient records keep project branches unknown; explicit completion wins', () => {
  for (const records of [[], events({ step: 'CHECK', status: 'failed' }), events({ step: 'BOOKKEEPING', outcome: 'stopped' }), events({ step: 'RUN_END', outcome: 'passed' })]) {
    assert.equal(cell(state.runFlow(records), 'continue').state, 'pending');
    assert.equal(cell(state.runFlow(records), 'finish').state, 'pending');
  }
  const records = events({ step: 'RUN_END', outcome: 'stopped' }, { step: 'PROJECT_COMPLETE', outcome: 'passed' });
  assert.equal(cell(state.runFlow(records), 'finish').state, 'done');
  assert.equal(cell(state.runFlow(records), 'continue').state, 'skipped');
});

test('finalization combines outcome and verified records without coloring successful failure handling as failure', () => {
  assert.equal(typeof state.runFlow, 'function', 'record-to-flow helper');
  const records = events(
    { step: 'CHECK', status: 'failed' },
    { step: 'RUN_END', outcome: 'retry-needed' },
    { step: 'BOOKKEEPING', outcome: 'retry-needed', bookkeeping: 'complete' }
  );
  const flow = state.runFlow(records, records);
  assert.equal(cell(flow, 'check').state, 'failed');
  assert.equal(cell(flow, 'unfinished').state, 'done');
  assert.equal(cell(flow, 'finalize').state, 'done');
  assert.equal(cell(flow, 'complete').state, 'skipped');
  assert.deepEqual(cell(flow, 'finalize').events, records.slice(1));
  assert.equal(cell(state.runFlow(records.slice(0, 2)), 'finalize').state, 'pending');
  assert.equal(cell(state.runFlow(records.slice(2)), 'finalize').state, 'pending');
  assert.equal(flow.current, 'finalize');
});
