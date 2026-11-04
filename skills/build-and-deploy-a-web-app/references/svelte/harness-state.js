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
