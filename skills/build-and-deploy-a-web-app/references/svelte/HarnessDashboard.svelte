<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { env } from '$env/dynamic/public';
  import { marked } from 'marked';
  import DOMPurify from 'dompurify';

  // Render nurse-authored markdown (overview + outstanding issues) to safe HTML.
  // marked turns the markdown into HTML; DOMPurify strips anything unsafe. Only
  // ever called in the browser with non-empty content, so SSR never touches
  // DOMPurify (which needs a DOM).
  function renderMarkdown(md: string): string {
    if (!md) return '';
    return DOMPurify.sanitize(marked.parse(md, { async: false }) as string);
  }

  // Environment variables (set in .env). The owner's id is intentionally NOT
  // here — it is a server-only var; the backend tells us whether we're the
  // owner via /api/harness/owner so the id is never exposed to the browser.
  const HARNESS_ANNOTATION_ID = env.PUBLIC_HARNESS_ANNOTATION_ID;
  const WORKSPACE_PATH = env.PUBLIC_WORKSPACE_PATH;

  let runs: any[] = $state([]);
  let currentRun: any = $state(null);
  let overview: string = $state('');
  let outstandingIssues: string = $state('');
  let refreshInterval: any;

  // Ownership is decided by the backend; starts false until confirmed.
  let isOwner = $state(false);

  async function checkOwner() {
    try {
      const res = await fetch('/api/harness/owner');
      if (!res.ok) return false;
      const data = await res.json();
      return data.isOwner === true;
    } catch (e) {
      return false;
    }
  }

  // Flow chart lookups for the currently selected run
  let stepMap = $derived(new Map((currentRun?.events || []).map((e: any) => [e.step, e])));
  const hasStep = (step: string) => stepMap.has(step);
  const getStep = (step: string) => stepMap.get(step);

  // Which branches of the constant flow chart this run actually took.
  // The Nurse health-check at the top acts on the *previous* run, so a fix or
  // escalation appearing in this run means the nurse intervened before the run.
  let nurseIntervened = $derived(stepMap.has('FIX_ATTEMPT') || stepMap.has('ESCALATE'));
  let projectComplete = $derived(stepMap.has('FIND_MILESTONE') && !stepMap.has('GENERATE'));
  let reviewFailed = $derived(
    stepMap.has('REVIEW') &&
    !stepMap.has('MARK_COMPLETE') &&
    (stepMap.has('RUN_COMPLETE') || stepMap.has('RUN_INCOMPLETE')));
  // Retries remaining => milestone left incomplete but the run still completes.
  let retryScheduled = $derived(reviewFailed && stepMap.has('RUN_COMPLETE'));

  async function fetchRuns() {
    try {
      // Fetch records from backend API over a rolling 30-day window ending today.
      const end = new Date();
      const start = new Date(end.getTime() - 30 * 24 * 60 * 60 * 1000);
      const startDate = start.toISOString().slice(0, 10);
      const endDate = end.toISOString().slice(0, 10);
      const res = await fetch(`/api/harness/runs?annotation_id=${encodeURIComponent(HARNESS_ANNOTATION_ID)}&start_date=${startDate}&end_date=${endDate}`);
      const data = await res.json();

      // Extract records from the response
      const records = data.records || data || [];

      // Group by run_id from the record data
      const runMap = new Map();
      records.forEach((record: any) => {

        // Parse the note field as JSON to get harness data
        let harnessData;
        try {
          harnessData = record.note ? JSON.parse(record.note) : {};
        } catch (e) {
          console.error('Failed to parse note as JSON:', record.note);
          return;
        }

        const runId = harnessData.run_id;
        const step = harnessData.step;
        const status = harnessData.status;
        const detail = harnessData.detail || '';
        const evidence = typeof harnessData.evidence === 'string' ? harnessData.evidence : '';
        const timestamp = record.recorded_at;

        if (!runId || !step) return; // Skip records without required fields

        if (!runMap.has(runId)) {
          runMap.set(runId, { run_id: runId, events: [] });
        }
        runMap.get(runId).events.push({ step, status, timestamp, detail, evidence });
      });

      const runsArray = Array.from(runMap.values());
      // Sort each run's events chronologically so the last event is the newest
      // one — getRunStatus and the per-step lookup both rely on latest-wins,
      // and long steps emit several records that may arrive out of order.
      runsArray.forEach((r: any) =>
        r.events.sort((a: any, b: any) => (a.timestamp || '').localeCompare(b.timestamp || ''))
      );
      const sortedRunsArray = runsArray.sort((a, b) => {
        const aTime = a.events[0]?.timestamp || '';
        const bTime = b.events[0]?.timestamp || '';
        return bTime.localeCompare(aTime);
      });
      
      runs = sortedRunsArray;

      // Preserve the user's selection across polls; only default to the
      // latest run when nothing is selected yet or the selection disappeared,
      // OR if the current selection was the previous latest run.
      if (!currentRun || currentRun.run_id === sortedRunsArray[1]?.run_id || !runs.find((r) => r.run_id === currentRun.run_id)) {
        currentRun = sortedRunsArray[0] || null;
      } else {
        currentRun = runs.find((r) => r.run_id === currentRun.run_id) || null;
      }
    } catch (e) {
      console.error('Failed to fetch runs:', e);
      runs = [];
      currentRun = null;
    }
  }

  async function fetchOverview() {
    try {
      const res = await fetch(`/api/harness/overview?workspace_path=${encodeURIComponent(WORKSPACE_PATH)}`);
      overview = await res.text();
    } catch (e) {
      overview = '';
    }
  }

  async function fetchOutstandingIssues() {
    try {
      const res = await fetch(`/api/harness/issues?workspace_path=${encodeURIComponent(WORKSPACE_PATH)}`);
      outstandingIssues = await res.text();
    } catch (e) {
      outstandingIssues = '';
    }
  }

  onMount(async () => {
    // Ask the backend whether we're the owner, then fetch data if so.
    isOwner = await checkOwner();
    if (isOwner) {
      await fetchOverview();
      await fetchRuns();
      await fetchOutstandingIssues();

      // Refresh every 5 seconds
      refreshInterval = setInterval(async () => {
        await fetchOverview();
        await fetchRuns();
        await fetchOutstandingIssues();
      }, 5000);
    }
  });

  onDestroy(() => {
    if (refreshInterval) clearInterval(refreshInterval);
  });

  function getRunStatus(run: any) {
    const lastEvent = run.events[run.events.length - 1];
    if (lastEvent.step === 'RUN_COMPLETE') return 'completed';
    if (lastEvent.step === 'RUN_INCOMPLETE') return 'incomplete';
    if (lastEvent.step === 'ESCALATE') return 'escalated';
    return 'in-progress';
  }

  function formatTimestamp(ts: string) {
    return new Date(ts).toLocaleString();
  }
</script>

{#if isOwner}
  <div class="harness-dashboard">
    <h2>Harness Dashboard</h2>

    <!-- Outstanding Issues -->
    {#if outstandingIssues}
      <div class="outstanding-issues">
        <h3>Outstanding Issues</h3>
        <div class="markdown-body issues-content">{@html renderMarkdown(outstandingIssues)}</div>
      </div>
    {/if}

    <!-- Run History - compact, scrollable -->
    <div class="run-history">
      <h3>Recent Runs</h3>
      <div class="run-list">
        {#each runs.slice(0, 3) as run}
          <button
            class="run-item"
            class:active={run === currentRun}
            onclick={() => currentRun = run}
          >
            <div class="run-header">
              <span class="run-id">{run.run_id}</span>
              <span class="status-badge status-{getRunStatus(run)}">{getRunStatus(run)}</span>
            </div>
            <div class="run-time">{formatTimestamp(run.events[0]?.timestamp)}</div>
          </button>
        {/each}
      </div>
    </div>

    <!-- Current Run with Flow Diagram -->
    {#if currentRun}
      <div class="current-run-flow">
        <div class="current-run-header">
          <h3>Run: {currentRun.run_id}</h3>
          <span class="run-status status-{getRunStatus(currentRun)}">{getRunStatus(currentRun)}</span>
        </div>

        {#snippet stepBox(key, name, extra = '')}
          <div class="flow-step-box {extra}" class:active={hasStep(key)}>
            <div class="step-header">
              <span class="step-name">{name}</span>
              {#if hasStep(key)}
                <span class="status-badge status-{getStep(key).status}">{getStep(key).status}</span>
              {/if}
            </div>
            {#if hasStep(key) && getStep(key).detail}
              <div class="step-detail">{getStep(key).detail}</div>
            {/if}
            {#if hasStep(key) && getStep(key).evidence}
              <div class="step-evidence">Evidence: {getStep(key).evidence}</div>
            {/if}
          </div>
        {/snippet}

        <div class="flow-chart">
          <div class="flow-body">
            <!-- Nurse pre-check: its own column, runs before the main loop -->
            <div class="nurse-band nurse-col">
              <div class="nurse-label">🩺 Nurse pre-check</div>
              <div class="flow-decision-box nurse">
                <div class="decision-text">Previous run completed?</div>
              </div>
              <div class="flow-h-arrow labeled vert">No ↓</div>
              <div class="flow-decision-box nurse">
                <div class="decision-text">Fix attempts remain?</div>
              </div>
              <div class="branch-item" class:active={hasStep('FIX_ATTEMPT')}>
                <span class="branch-tag">Yes ↓</span>
                {@render stepBox('FIX_ATTEMPT', '🩺 Attempt Fix', 'small')}
              </div>
              <div class="branch-item" class:active={hasStep('ESCALATE')}>
                <span class="branch-tag">No ↓</span>
                {@render stepBox('ESCALATE', '🩺 Escalate — Loop Ends', 'small')}
              </div>
            </div>

            <div class="flow-h-arrow labeled connector">Healthy<br />or fixed →</div>

            <!-- Main harness loop -->
            <div class="main-flow">
              <!-- Milestone selection -->
              <div class="flow-grid">
                {@render stepBox('FIND_MILESTONE', '🎛️ Find Incomplete Milestone', 'small')}
                <div class="flow-h-arrow">→</div>
                <div class="flow-decision-box inline">
                  <div class="decision-text">🎛️ Any incomplete milestone?</div>
                </div>
                <div class="flow-h-arrow labeled">No →</div>
                <div class="branch-item" class:active={projectComplete}>
                  <div class="flow-terminal complete small">Project Complete</div>
                </div>
              </div>
              <div class="flow-arrow">↓</div>

              <!-- Generate → review → decision -->
              <div class="flow-grid">
                {@render stepBox('GENERATE', '✍️ Generate Code', 'small')}
                <div class="flow-h-arrow">→</div>
                {@render stepBox('REVIEW', '⚖️ Review Code', 'small')}
                <div class="flow-h-arrow">→</div>
                <div class="flow-decision-box inline">
                  <div class="decision-text">🎛️ Review passed?</div>
                </div>
              </div>
              <div class="flow-arrow">↓</div>

              <!-- Review outcomes: Yes comes first; No spans the other two columns -->
              <div class="flow-grid outcomes">
                <div class="outcome-yes" class:active={hasStep('MARK_COMPLETE')}>
                  <div class="path-label">Yes</div>
                  {@render stepBox('MARK_COMPLETE', '🎛️ Mark Milestone Complete', 'small')}
                  <div class="flow-arrow">↓</div>
                  <div class="flow-terminal complete small">Run Complete</div>
                </div>
                <div class="outcome-no" class:active={reviewFailed}>
                  <div class="path-label">No</div>
                  <div class="flow-decision-box small">
                    <div class="decision-text">🎛️ Retries remain?</div>
                  </div>
                  <div class="flow-split tight">
                    <div class="flow-path" class:active={retryScheduled}>
                      <div class="path-label">Yes</div>
                      <div class="flow-terminal retry small">Leave Incomplete — Retry Next Run</div>
                    </div>
                    <div class="flow-path" class:active={hasStep('RUN_INCOMPLETE')}>
                      <div class="path-label">No</div>
                      <div class="flow-terminal incomplete small">End Run — Incomplete</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    {/if}

    <!-- Product Overview - concise progress + milestone summary (nurse-authored) -->
    {#if overview}
      <div class="overview">
        <div class="markdown-body">{@html renderMarkdown(overview)}</div>
      </div>
    {/if}
  </div>
{/if}

<style>
  .harness-dashboard {
    padding: 2rem;
    max-width: 1200px;
    margin: 0 auto;
    color: var(--color-fulcra-black);
  }

  .harness-dashboard h2,
  .harness-dashboard h3 {
    color: var(--color-fulcra-black);
  }

  .run-history {
    margin-bottom: 2rem;
  }

  .run-list {
    display: flex;
    gap: 1rem;
    overflow-x: auto;
    padding-bottom: 0.5rem;
  }

  .run-item {
    flex: 0 0 300px;
    background: var(--color-fulcra-white);
    border: 2px solid var(--color-fulcra-black-25);
    border-radius: 8px;
    padding: 1rem;
    cursor: pointer;
    transition: all 0.2s;
  }

  .run-item:hover {
    border-color: var(--color-fulcra-teal);
  }

  .run-item.active {
    border-color: var(--color-fulcra-teal);
    background: var(--color-fulcra-teal-10);
  }

  .run-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
  }

  .run-id {
    font-family: monospace;
    font-size: 0.875rem;
    font-weight: 600;
  }

  .run-time {
    color: var(--color-fulcra-gray);
    font-size: 0.75rem;
    margin-top: 0.25rem;
  }

  .current-run-flow {
    background: var(--color-fulcra-white);
    border: 1px solid var(--color-fulcra-black-25);
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 2rem;
  }

  .current-run-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1.5rem;
  }

  .current-run-header h3 {
    margin: 0;
  }

  .run-status {
    display: inline-block;
    padding: 0.35rem 0.85rem;
    border-radius: 4px;
    font-weight: 600;
    font-size: 0.875rem;
    text-transform: capitalize;
    white-space: nowrap;
  }

  .status-completed { background: var(--color-fulcra-teal-10); color: var(--color-fulcra-green-100); }
  .status-in-progress { background: var(--color-fulcra-lavender-25); color: var(--color-fulcra-purple-100); }
  .status-incomplete { background: #ffcdd2; color: var(--color-fulcra-error); }
  .status-escalated { background: #ffe0b2; color: #e65100; }

  .flow-chart {
    /* Three equal process columns with fixed arrow gutters between them.
       Fixed track sizes mean every .flow-grid row is the same total width,
       so the columns line up vertically across rows. */
    --flow-col: 185px;
    --arrow-w: 2.25rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0;
    overflow-x: auto;
  }

  .flow-step-box {
    width: 100%;
    max-width: 600px;
    padding: 1.25rem;
    background: var(--color-fulcra-white);
    border: 2px solid var(--color-fulcra-black-25);
    border-radius: 8px;
    opacity: 0.3;
    transition: all 0.2s;
  }

  .flow-step-box.small {
    max-width: 400px;
    padding: 1rem;
  }

  .flow-step-box.active {
    opacity: 1;
    border-color: var(--color-fulcra-teal);
    background: var(--color-fulcra-teal-10);
  }

  .flow-decision-box {
    width: 100%;
    max-width: 600px;
    padding: 1rem 1.5rem;
    background: var(--color-fulcra-lavender-25);
    border: 2px solid var(--color-fulcra-purple);
    border-radius: 8px;
    text-align: center;
    margin: 0.5rem 0;
  }

  .flow-decision-box.small {
    max-width: 340px;
    padding: 0.6rem 1rem;
  }

  .flow-decision-box.nurse {
    background: #ffe0b2;
    border-color: #f57c00;
  }

  .decision-text {
    font-weight: 600;
    font-size: 1rem;
    color: var(--color-fulcra-purple-100);
  }

  .flow-decision-box.small .decision-text {
    font-size: 0.875rem;
  }

  .flow-decision-box.nurse .decision-text {
    color: #e65100;
  }

  .flow-terminal {
    padding: 0.6rem 1.25rem;
    border-radius: 999px;
    font-weight: 700;
    font-size: 0.875rem;
    text-align: center;
    border: 2px solid var(--color-fulcra-black-25);
    background: var(--color-fulcra-white);
    color: var(--color-fulcra-black);
  }

  .flow-terminal.small {
    font-size: 0.8rem;
    padding: 0.45rem 1rem;
  }

  .flow-terminal.complete {
    background: var(--color-fulcra-teal-10);
    border-color: var(--color-fulcra-teal);
    color: var(--color-fulcra-green-100);
  }

  .flow-terminal.retry {
    background: var(--color-fulcra-lavender-25);
    border-color: var(--color-fulcra-purple);
    color: var(--color-fulcra-purple-100);
  }

  .flow-terminal.incomplete {
    background: #ffcdd2;
    border-color: var(--color-fulcra-error);
    color: var(--color-fulcra-error);
  }

  .flow-passthrough {
    font-size: 0.8rem;
    font-style: italic;
    color: var(--color-fulcra-gray);
    padding: 0.5rem 0;
  }

  .flow-grid {
    display: grid;
    grid-template-columns:
      var(--flow-col) var(--arrow-w) var(--flow-col) var(--arrow-w) var(--flow-col);
    align-items: center;
    justify-items: center;
    row-gap: 0.4rem;
    width: max-content;
    max-width: 100%;
    margin: 0.15rem auto;
  }

  /* Direct children of a grid row fill their column exactly */
  .flow-grid > .flow-step-box,
  .flow-grid > .flow-decision-box {
    width: var(--flow-col);
    max-width: none;
    box-sizing: border-box;
    margin: 0;
  }

  /* Force the nurse fix/escalate branch and the success path into column 3 */
  .col3 {
    grid-column: 5;
  }

  /* Nurse pre-check lives in its own column to the left of the main loop */
  .flow-body {
    display: flex;
    align-items: flex-start;
    justify-content: center;
    gap: 0.5rem;
  }

  .main-flow {
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .nurse-band {
    background: #fff8f0;
    border: 1px dashed #f57c00;
    border-radius: 10px;
    padding: 0.75rem;
  }

  .nurse-col {
    display: flex;
    flex-direction: column;
    align-items: stretch;
    gap: 0.35rem;
    width: calc(var(--flow-col) + 1.5rem);
    box-sizing: border-box;
  }

  .nurse-label {
    font-size: 0.8rem;
    font-weight: 700;
    color: #e65100;
    text-align: center;
    margin-bottom: 0.15rem;
  }

  .nurse-col .flow-decision-box {
    width: 100%;
    max-width: none;
    margin: 0;
    padding: 0.6rem 0.9rem;
    box-sizing: border-box;
  }

  .nurse-col .flow-step-box {
    width: 100%;
    max-width: none;
    box-sizing: border-box;
  }

  .flow-h-arrow.vert {
    text-align: center;
  }

  .flow-h-arrow.connector {
    align-self: flex-start;
    margin-top: 2.5rem;
    text-align: center;
    line-height: 1.2;
  }

  .flow-h-arrow {
    font-size: 1.25rem;
    color: var(--color-fulcra-gray);
    line-height: 1;
  }

  .flow-h-arrow.labeled {
    font-size: 0.8rem;
    font-weight: 600;
  }

  .flow-decision-box.inline {
    padding: 0.6rem 0.9rem;
  }

  .flow-decision-box.inline .decision-text {
    font-size: 0.85rem;
  }

  .branch-col {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    width: var(--flow-col);
  }

  .branch-col .flow-step-box {
    width: 100%;
    max-width: none;
    box-sizing: border-box;
  }

  .branch-tag {
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--color-fulcra-gray);
  }

  .branch-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.15rem;
    opacity: 0.3;
    transition: opacity 0.2s;
  }

  .branch-item.active {
    opacity: 1;
  }

  /* Review outcomes row: No spans two columns, Yes sits in column 3 */
  .outcomes {
    align-items: start;
    row-gap: 0;
  }

  .outcome-no {
    grid-column: 3 / span 3;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.4rem;
    width: 100%;
    opacity: 0.3;
    transition: opacity 0.2s;
  }

  .outcome-yes {
    grid-column: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.4rem;
    width: var(--flow-col);
    opacity: 0.3;
    transition: opacity 0.2s;
  }

  .outcome-yes .flow-step-box {
    width: 100%;
    max-width: none;
    box-sizing: border-box;
  }

  .outcome-no.active,
  .outcome-yes.active {
    opacity: 1;
  }

  .flow-split {
    display: flex;
    gap: 1rem;
    justify-content: center;
  }

  .flow-split.tight {
    gap: 1rem;
    margin: 0.25rem 0 0;
  }

  .flow-path {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    opacity: 0.3;
    transition: opacity 0.2s;
  }

  .flow-path.active {
    opacity: 1;
  }

  .path-label {
    font-weight: 600;
    color: var(--color-fulcra-gray);
    font-size: 0.875rem;
  }

  .flow-arrow {
    font-size: 1.5rem;
    color: var(--color-fulcra-gray);
    line-height: 1;
    padding: 0.25rem 0;
  }

  .step-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
  }

  .step-name {
    font-weight: 600;
    font-size: 1rem;
    color: var(--color-fulcra-black);
  }

  .status-badge {
    display: inline-block;
    padding: 0.25rem 0.5rem;
    border-radius: 3px;
    font-size: 0.75rem;
    font-weight: 500;
  }

  .status-started { background: var(--color-fulcra-lavender-50); color: var(--color-fulcra-purple-100); }
  .status-completed { background: var(--color-fulcra-teal-50); color: var(--color-fulcra-green-100); }
  .status-failed { background: #ffcdd2; color: var(--color-fulcra-error); }

  .step-detail {
    color: var(--color-fulcra-black);
    font-size: 0.875rem;
    margin-bottom: 0.5rem;
    line-height: 1.5;
  }

  .step-evidence {
    color: #4b5563;
    font-size: 0.75rem;
    line-height: 1.5;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
  }

  .step-time {
    color: var(--color-fulcra-gray);
    font-size: 0.75rem;
  }

  .overview {
    background: var(--color-fulcra-teal-25, #e6f7f5);
    border: 1px solid var(--color-fulcra-teal, #14b8a6);
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
  }

  .outstanding-issues {
    background: var(--color-fulcra-lavender-25);
    border: 1px solid var(--color-fulcra-purple);
    border-radius: 8px;
    padding: 1.5rem;
  }

  .issues-content {
    color: var(--color-fulcra-purple-100);
  }

  /* Rendered markdown. Styles must be :global — Svelte can't scope HTML
     injected with {@html}. */
  .markdown-body {
    font-size: 0.875rem;
    line-height: 1.5;
  }
  .markdown-body :global(h1),
  .markdown-body :global(h2),
  .markdown-body :global(h3),
  .markdown-body :global(h4) {
    margin: 0.75em 0 0.35em;
    line-height: 1.25;
  }
  .markdown-body :global(h1) { font-size: 1.35rem; }
  .markdown-body :global(h2) { font-size: 1.15rem; }
  .markdown-body :global(h3) { font-size: 1rem; }
  .markdown-body :global(:first-child) { margin-top: 0; }
  .markdown-body :global(p) { margin: 0.4em 0; }
  .markdown-body :global(ul),
  .markdown-body :global(ol) { margin: 0.4em 0; padding-left: 1.4rem; }
  .markdown-body :global(li) { margin: 0.15em 0; }
  .markdown-body :global(a) { color: var(--color-fulcra-teal, #14b8a6); }
  .markdown-body :global(code) {
    background: rgba(0, 0, 0, 0.06);
    padding: 0.1em 0.35em;
    border-radius: 4px;
    font-size: 0.85em;
  }
  .markdown-body :global(pre) {
    background: rgba(0, 0, 0, 0.06);
    padding: 0.75rem;
    border-radius: 6px;
    overflow-x: auto;
  }
  .markdown-body :global(pre code) { background: none; padding: 0; }
  .markdown-body :global(hr) {
    border: none;
    border-top: 1px solid rgba(0, 0, 0, 0.1);
    margin: 0.75em 0;
  }
</style>
