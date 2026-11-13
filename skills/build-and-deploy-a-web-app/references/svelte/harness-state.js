// Shared wire/state helpers. No framework or SDK dependency.
/** @param {string} text */
export function parseRecords(text) {
  return text.split('\n').filter(line => line.trim()).map(line => {
    const record = JSON.parse(line);
    const strings = ['id', 'project_id', 'run_id', 'milestone', 'tier_reason', 'step', 'evidence', 'project_summary'];
    const times = ['start_time', 'end_time', 'run_start', 'deadline'];
    const lists = ['check_plan', 'next_actions', 'open_issues'];
    if (!record || record.schema_version !== 1 ||
        !strings.every(key => typeof record[key] === 'string' && record[key].trim()) ||
        !times.every(key => typeof record[key] === 'string' && Number.isFinite(Date.parse(record[key]))) ||
        !Number.isInteger(record.attempt) || record.attempt < 1 ||
        !['Nurse', 'Coordinator', 'Generator', 'Evaluator'].includes(record.role) ||
        !['started', 'completed', 'failed'].includes(record.status) ||
        typeof record.detail !== 'string' ||
        !['running', 'passed', 'retry-needed', 'stopped', 'escalated'].includes(record.outcome) ||
        !['light', 'focused', 'full'].includes(record.tier) ||
        !lists.every(key => Array.isArray(record[key]) && record[key].every((item) => typeof item === 'string')) ||
        !record.check_plan.length || !Array.isArray(record.resources) ||
        !record.resources.every((/** @type {{kind?: unknown, id?: unknown} | null} */ resource) => resource && typeof resource.kind === 'string' && typeof resource.id === 'string')) {
      throw new Error('Invalid harness event; check the configured v1 schema');
    }
    return record;
  });
}

/** @param {Record<string, any>[]} existing @param {Record<string, any>[]} incoming */
export function mergeEvents(existing, incoming) {
  return [...new Map([...existing, ...incoming].map(event => [event.id, event])).values()]
    .sort((a, b) => Date.parse(a.start_time) - Date.parse(b.start_time) || a.id.localeCompare(b.id));
}

/** @param {Record<string, any>[]} events */
export function groupRuns(events) {
  const runs = new Map();
  for (const event of mergeEvents([], events)) {
    const previous = runs.get(event.run_id);
    runs.set(event.run_id, { ...event, events: [...(previous?.events || []), event] });
  }
  return [...runs.values()].sort((a, b) => Date.parse(b.run_start) - Date.parse(a.run_start));
}

/** @param {string | null} selected @param {{run_id: string}[]} runs */
export function selectedRunId(selected, runs) {
  return selected || runs[0]?.run_id || null;
}

// Fixed presentation cells; the event schema and writers remain unchanged.
export const flowCells = [
  ['nurse', 'Nurse', 0, 0], ['plan', 'Plan & start', 1, 0],
  ['build', 'Build', 2, 0], ['check', 'Check', 3, 0],
  ['review', 'Independent review', 3, 1], ['complete', 'Mark milestone done', 4, 0],
  ['unfinished', 'Milestone unfinished', 4, 1], ['finalize', 'Finalize run', 5, 0],
  ['continue', 'Continue work', 6, 0], ['finish', 'Finish project', 6, 1]
].map(([id, label, column, row]) => ({ id, label, column, row }));

/** @type {Record<string, string>} */
const phaseForStep = {
  RUN_START: 'plan', FIND_MILESTONE: 'plan', GENERATE: 'build', RESOURCE_CREATED: 'build',
  CHECK: 'check', REVIEW: 'review', MARK_COMPLETE: 'complete',
  RUN_END: 'finalize', BOOKKEEPING: 'finalize', PROJECT_COMPLETE: 'finish'
};

/** @param {Record<string, any>[]} events @param {Record<string, any>[]} [allEvents] */
export function runFlow(events, allEvents = events) {
  const ordered = mergeEvents([], events);
  const cells = flowCells.map(cell => ({ ...cell, state: 'pending', status: 'Not recorded', events: /** @type {Record<string, any>[]} */ ([]) }));
  const byId = Object.fromEntries(cells.map(cell => [cell.id, cell]));
  let current = 'plan';
  /** @type {{id: string, label: string, events: Record<string, any>[], state: string, status: string}[]} */
  const nurseSteps = [];
  let previous;
  for (const event of ordered) {
    if (event.role === 'Nurse') {
      // Results can arrive across interleaved activity; new starts retain their own action.
      let action = event.status === 'started'
        ? (previous?.role === 'Nurse' ? nurseSteps.at(-1) : undefined)
        : nurseSteps.findLast(action => action.label === event.step && action.events.at(-1)?.status === 'started');
      if (!action || action.label !== event.step || action.events.at(-1)?.status !== 'started') {
        action = { id: event.id, label: event.step, events: [], state: 'pending', status: 'Not recorded' };
        nurseSteps.push(action);
      }
      action.events.push(event);
      Object.assign(action, eventState(event));
      byId.nurse.events.push(event);
      Object.assign(byId.nurse, eventState(event));
    }
    const id = Object.hasOwn(phaseForStep, event.step) ? phaseForStep[event.step] : undefined;
    if (id) {
      byId[id].events.push(event);
      if (event.step !== 'RESOURCE_CREATED') Object.assign(byId[id], eventState(event));
    }
    if (id || event.role === 'Nurse') current = id || 'nurse';
    previous = event;
  }
  const end = ordered.findLast(event => event.step === 'RUN_END');
  const bookkeeping = ordered.findLast(event => event.step === 'BOOKKEEPING');
  if (end && end.outcome !== 'running' && end.outcome !== 'passed' && byId.complete.state !== 'done') {
    Object.assign(byId.unfinished, { state: 'done', status: 'Left unfinished', events: [end] });
    if (!byId.complete.events.length) Object.assign(byId.complete, { state: 'skipped', status: 'Not taken' });
  }
  const finalized = end && end.outcome !== 'running' && bookkeeping?.status === 'completed' && bookkeeping.bookkeeping === 'complete';
  const finalFailure = byId.finalize.events.at(-1)?.status === 'failed';
  if (byId.finalize.events.length) {
    Object.assign(byId.finalize, {
      state: finalized ? 'done' : finalFailure ? 'failed' : 'pending',
      status: finalized ? 'Completed' : finalFailure ? 'Could not finalize' : end ? 'Records pending' : 'Outcome not recorded'
    });
  }
  if (byId.complete.state === 'done') Object.assign(byId.unfinished, { state: 'skipped', status: 'Not taken' });
  // Only settle an unused verification branch after a recorded run end.
  // Reconciliation can still add evidence and restore that branch later.
  if (end && end.outcome !== 'running') {
    for (const [used, unused] of [['check', 'review'], ['review', 'check']]) {
      if (byId[used].events.length && !byId[unused].events.length) {
        Object.assign(byId[unused], { state: 'skipped', status: 'Not recorded in run' });
      }
    }
  }
  const nextRun = allEvents.find(event => event.step === 'RUN_START' && event.previous_run_id === ordered[0]?.run_id && event.project_id === ordered[0]?.project_id && event.run_id !== ordered[0]?.run_id);
  const nurseOutcomes = [
    { id: 'continue', label: 'Continue', state: 'pending', status: 'Not confirmed yet', events: [] },
    { id: 'help', label: 'Ask for help', state: 'pending', status: 'Not recorded', events: [] }
  ];
  if (nextRun) {
    Object.assign(nurseOutcomes[0], { state: 'done', status: 'Linked retry started', events: [nextRun] });
    Object.assign(nurseOutcomes[1], { state: 'skipped', status: 'Not taken' });
  }
  if (end?.outcome === 'escalated') {
    if (!nextRun) Object.assign(nurseOutcomes[0], { state: 'skipped', status: 'Not taken' });
    Object.assign(nurseOutcomes[1], { state: 'attention', status: 'Escalation recorded', events: [end] });
  }
  // A terminal record ends earlier activity, not later Nurse closure repairs.
  if (end && end.outcome !== 'running') {
    for (const cell of [...cells, ...nurseSteps]) {
      const lastEvent = cell.events.at(-1);
      if (cell.state === 'active' && lastEvent && ordered.indexOf(lastEvent) < ordered.indexOf(end)) {
        Object.assign(cell, { state: 'pending', status: 'No result recorded' });
      }
    }
  }
  // An incomplete outcome proves work remains, not that another worker started.
  if (end && ['stopped', 'retry-needed', 'escalated'].includes(end.outcome)) {
    Object.assign(byId.continue, {
      state: end.outcome === 'escalated' ? 'attention' : 'waiting',
      status: end.outcome === 'escalated' ? 'Help needed · not started' : 'Awaiting work · not started',
      events: [end]
    });
    if (!byId.finish.events.length) Object.assign(byId.finish, { state: 'skipped', status: 'Work remains' });
  }
  if (nextRun) Object.assign(byId.continue, { state: 'done', status: 'Linked retry started', events: [nextRun] });
  if (byId.finish.state === 'done') Object.assign(byId.continue, { state: 'skipped', status: 'Not taken' });
  const otherEvents = ordered.filter(event => event.role !== 'Nurse' && !Object.hasOwn(phaseForStep, event.step));
  return { cells, current, nurseSteps, nurseOutcomes, otherEvents };
}

/** @param {Record<string, any>} event */
function eventState(event) {
  return {
    state: event.status === 'failed' ? 'failed' : event.status === 'started' ? 'active' : 'done',
    status: event.status === 'failed' ? 'Failed' : event.status === 'started' ? 'In progress' : 'Completed'
  };
}

// Two-minute overlap handles ordinary ingestion delay. Every twelfth poll
// reconciles from run_start, including idle/terminal runs. Never use event time
// as a permanent high-water mark: arbitrarily late records need reconciliation.
/** @param {string} runStart @param {string | null} lastRead @param {boolean} reconcile */
export function pollStart(runStart, lastRead, reconcile) {
  if (!lastRead || reconcile) return runStart;
  return new Date(Math.max(Date.parse(runStart), Date.parse(lastRead) - 120000)).toISOString();
}

/** @param {string} type @param {string | null} [start] @param {string | null} [end] */
export function recordsQuery(type, start, end) {
  if (!/^Event\/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(type)) {
    throw new Error('HARNESS_DATA_TYPE must be Event/<UUID>');
  }
  const selector = `{__name__=${JSON.stringify(type)}}`;
  if (start === undefined && end === undefined) return selector;
  if (!start || !end) throw new Error('Invalid time range');
  const from = Math.floor(Date.parse(start) / 1000);
  const to = Math.ceil(Date.parse(end) / 1000);
  if (!Number.isFinite(from) || !Number.isFinite(to) || to <= from) throw new Error('Invalid time range');
  return `${selector}[${to - from}s] @ ${to}`;
}
