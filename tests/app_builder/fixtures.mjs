// Synthetic fixture only; never upload this as live evidence.
export const event = (overrides = {}) => ({
  id: '00000000-0000-4000-8000-000000000001', schema_version: 1,
  project_id: 'fixture', run_id: 'run-a', run_start: '2026-01-01T00:00:00Z',
  start_time: '2026-01-01T00:00:01Z', end_time: '2026-01-01T00:00:01Z',
  attempt: 1, deadline: '2026-01-01T00:15:00Z', milestone: 'm1', tier: 'full',
  tier_reason: 'Baseline', check_plan: ['deployed gates'], role: 'Coordinator',
  step: 'FIND_MILESTONE', status: 'completed', outcome: 'running',
  detail: 'Selected baseline', evidence: 'Fixture observation',
  project_summary: 'Fixture project', next_actions: ['Build'], open_issues: [], resources: [],
  ...overrides
});
