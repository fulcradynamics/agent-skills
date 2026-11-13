<script lang="ts">
  import { onMount } from 'svelte';
  import { HarnessFeed } from '$lib/harness-feed.js';
  import { groupRuns, runFlow } from '$lib/harness-state.js';

  let runs: any[] = $state([]);
  let selected: string | null = $state(null);
  let phaseSelection: { run: string; phase: string } | null = $state(null);
  let nurseSelection: { run: string; action: string } | null = $state(null);
  let isOwner = $state(false);
  let loading = $state(true);
  let message = $state('');
  let historyMessage = $state('');
  let lastSuccess = $state('');
  let now = $state(Date.now());
  let historyStart: string | null = $state(null);
  let historyBusy = $state(false);
  const feed = new HarnessFeed(async (params: Record<string, string>) => {
    const response = await fetch(`/api/harness/runs?${new URLSearchParams(params)}`, {
      signal: AbortSignal.timeout(20000), cache: 'no-store'
    });
    if (!response.ok) throw new Error(`Run request failed (${response.status}). Sign in again for 401; ask the Nurse about other errors.`);
    return (await response.json()).records;
  });
  let current = $derived(runs.find(run => run.run_id === selected));
  let latest = $derived(runs[0]);
  let flow = $derived(runFlow(current?.events || [], runs.flatMap(run => run.events)));
  let phaseId = $derived.by(() => phaseSelection?.run === current?.run_id ? phaseSelection?.phase : flow.current);
  let phase = $derived(flow.cells.find(cell => cell.id === phaseId) || flow.cells[0]);
  let nurseAction = $derived(flow.nurseSteps.find(action => nurseSelection?.run === current?.run_id && action.id === nurseSelection?.action) || flow.nurseSteps.at(-1));
  const edges = [
    ['plan', 'build'], ['build', 'check'], ['build', 'review'],
    ['check', 'complete'], ['check', 'unfinished'], ['review', 'complete'], ['review', 'unfinished'],
    ['complete', 'finalize'], ['unfinished', 'finalize'], ['finalize', 'continue'], ['finalize', 'finish']
  ];
  const descriptions: Record<string, string> = {
    nurse: 'Recorded Nurse actions and results. Select an action to inspect its evidence.',
    plan: 'Select the milestone and scoped checks, verify harness health, and start a bounded attempt.',
    build: 'Build the milestone. Created resources and implementation evidence are retained here.',
    check: 'Run the scoped checks against the actual app. Passing evidence must be accepted before completing the milestone.',
    review: 'A separate reviewer checks the fixed requirements and the actual app.',
    complete: 'Mark the milestone done only after accepting passing evidence.',
    unfinished: 'This attempt ended without completing the milestone. Its outcome and records still need to be saved.',
    finalize: 'Record the outcome, then save and verify the final run records. Both are required for completion here; a failed check can still be followed by successful finalization.',
    continue: 'A needed retry is not proof it started. Only a recorded, linked new run confirms continuation. Otherwise consult What’s next above.',
    finish: 'Only an explicit project-completion record establishes that no milestones remain.'
  };
  function connection(from: string, to: string) {
    const a = flow.cells.find(cell => cell.id === from)!;
    const b = flow.cells.find(cell => cell.id === to)!;
    const x = Number(a.column) * 132 + 120, y = Number(a.row) * 76 + 40;
    const u = Number(b.column) * 132 + 4, v = Number(b.row) * 76 + 40;
    return { path: `M${x} ${y} H${(x + u) / 2} V${v} H${u - 3}`, skipped: a.state === 'skipped' || b.state === 'skipped' };
  }
  function follow() { phaseSelection = null; nurseSelection = null; }

  let stale = $derived(!!lastSuccess && now - Date.parse(lastSuccess) > 15000);
  let overdue = $derived(latest?.outcome === 'running' && now > Date.parse(latest.deadline));

  function sync() {
    runs = groupRuns(feed.events);
    selected = feed.selected;
    historyStart = feed.historyStart;
  }

  async function poll() {
    try {
      await feed.refresh();
      sync();
      lastSuccess = feed.lastRead || '';

      message = '';
    } catch (error) {
      message = error instanceof Error ? error.message : 'Refresh failed';
    }
  }

  async function openRun(run: any) {
    follow();
    feed.selected = run.run_id;
    selected = run.run_id;
    try {
      // Explicit selection reconciles late history, not only its cached slice.
      await feed.history(run.run_start, new Date().toISOString());
      sync();
      historyMessage = '';
    } catch (error) {
      historyMessage = String(error);
    }
  }

  async function older() {
    historyBusy = true;
    try {
      await feed.loadOlder();
      sync();
      historyMessage = '';
    } catch (error) {
      historyMessage = String(error);
    } finally {
      historyBusy = false;
    }
  }

  onMount(() => {
    let stopped = false;
    let timer: ReturnType<typeof setInterval>;
    async function start() {
      try {
        const response = await fetch('/api/harness/owner', { signal: AbortSignal.timeout(20000) });
        if (!response.ok) throw new Error(`Owner check failed (${response.status})`);
        isOwner = (await response.json()).isOwner === true;
        if (!isOwner) message = 'Sign in as the app owner to view the harness.';
        if (isOwner && !stopped) {
          await poll();
          if (!stopped) timer = setInterval(() => {
            now = Date.now();
            // Five-second cadence; never overlap a slow poll or history request.
            if (!feed.busy) void poll();
          }, 5000);
        }
      } catch (error) {
        message = String(error);
      } finally {
        loading = false;
      }
    }
    void start();
    return () => { stopped = true; clearInterval(timer); };
  });
</script>

{#snippet eventList(events: any[])}
  {#if events.length}
    <ol class="event-list">
      {#each events as event (event.id)}
        <li class:failed={event.status === 'failed'}>
          <div class="heading"><strong>{event.step}</strong><span>{event.status}</span></div>
          <small>{event.role} · {new Date(event.start_time).toLocaleString()}</small>
          <p>{event.detail || 'No additional detail recorded.'}</p>
          <details><summary>Evidence</summary><p class="evidence">{event.evidence}</p></details>
        </li>
      {/each}
    </ol>
  {:else}
    <p class="muted">No activity recorded for this phase. This does not prove completion.</p>
  {/if}
{/snippet}

<section class="harness">
  <h1>Harness Dashboard</h1>
  {#if loading}<p>Loading owner access…</p>{/if}
  {#if message}<p role="alert" class="attention">{message} {lastSuccess ? 'Showing retained data.' : ''}</p>{/if}
  {#if isOwner}
    <p class="muted" aria-live="polite">{stale ? 'Stale data — ' : ''}Last successful refresh: {lastSuccess ? new Date(lastSuccess).toLocaleString() : 'not yet'}</p>
    {#if latest}
      <section class="panel overview" aria-label="Project overview">
        <div class="heading"><h2>Project overview</h2><span class:attention={latest.outcome === 'escalated'}>{latest.outcome === 'escalated' ? 'Help needed' : latest.outcome}</span></div>
        <p>{latest.project_summary}</p>
        <p class="muted">{latest.milestone} · {latest.tier}</p>
        <div class="overview-columns">
          <section><h3>What’s next</h3><ul>{#each latest.next_actions as action}<li>{action}</li>{/each}</ul></section>
          <section class:attention={latest.open_issues.length > 0} aria-label="Open issues">
            <h3>Open issues</h3>
            {#if latest.open_issues.length}<ul>{#each latest.open_issues as issue}<li>{issue}</li>{/each}</ul>{:else}<p>No open issues recorded.</p>{/if}
          </section>
        </div>
        {#if overdue}<p class="attention">Deadline passed without a terminal outcome. Nurse intervention needed; this is not an automatic stop confirmation.</p>{/if}
        {#if selected !== latest.run_id}<button onclick={() => openRun(latest)}>View latest run</button>{/if}
      </section>
    {:else if !loading && !message}<p>No run events yet. This is not evidence of completion.</p>{/if}
    <section class="panel" aria-label="Selected run">
      <div class="heading run-controls">
        <h2>Selected run</h2>
          <select aria-label="Run" value={selected || ''} disabled={!runs.length} onchange={(event) => {
            const run = runs.find(run => run.run_id === event.currentTarget.value);
            if (run) void openRun(run);
          }}>
            {#if !runs.length}<option value="">No runs loaded</option>{/if}
            {#each runs as run}<option value={run.run_id}>{run.milestone} · {run.run_id} · {run.outcome}</option>{/each}
          </select>
        <button disabled={historyBusy || !historyStart} onclick={older}>Load older 30-day window</button>
      </div>
      {#if historyStart}<p class="muted" aria-live="polite">History loaded from {new Date(historyStart).toLocaleString()}.</p>{/if}
      {#if historyMessage}<p role="alert" class="attention">{historyMessage}</p>{/if}
      {#if current}
        <div class="heading"><h2>{current.milestone}</h2><span class:attention={current.outcome === 'escalated'}>{current.outcome === 'escalated' ? 'Help needed' : current.outcome}</span></div>
        <p class="muted">Run {current.run_id} · Attempt {current.attempt} · {current.tier}</p>
        <!-- svelte-ignore a11y_no_noninteractive_tabindex (Keyboard users must be able to scroll the diagram.) -->
        <div class="flow-scroll" tabindex="0" role="region" aria-label="Run flow; scroll horizontally on narrow screens">
          <div class="run-flow">
            <svg width="918" height="156" aria-hidden="true">
              <defs><marker id="run-arrow" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6" class="arrow-head" /></marker></defs>
              {#each edges as [from, to]}
                {@const edge = connection(from, to)}
                <path d={edge.path} class="connector" class:skipped={edge.skipped} />
              {/each}
            </svg>
            {#each flow.cells as cell (cell.id)}
              <button class="flow-cell {cell.state}" class:nurse={cell.id === 'nurse'} style:left={`${Number(cell.column) * 132 + 4}px`} style:top={`${Number(cell.row) * 76 + 12}px`} aria-pressed={phase.id === cell.id} data-phase={cell.id} onclick={() => { phaseSelection = { run: current.run_id, phase: String(cell.id) }; }}>
                <strong>{cell.label}</strong><small>{cell.status}</small>
              </button>
            {/each}
          </div>
        </div>
        <p class="legend">Green · completed &nbsp; Teal pulse · active &nbsp; Blue · awaiting work &nbsp; Purple · failed step &nbsp; Orange · needs attention &nbsp; Faded · unused path</p>
        <p class="muted">Nurse supervises throughout. Missing records stay unknown; an ended run is not necessarily a finished project.</p>
        <section class="phase-detail" aria-label="Selected phase details">
          <div class="heading"><h2>{phase.label}</h2><button onclick={follow} disabled={phaseSelection === null && nurseSelection === null}>Follow current step</button></div>
          <p>{descriptions[String(phase.id)]}</p>
          {#if phase.id === 'nurse'}
            <div class="nurse-columns">
              <div>
                <h3>Recorded Nurse flow</h3>
                <div class="nurse-flow">
                  {#each flow.nurseSteps as action (action.id)}
                    <button class="nurse-action {action.state}" aria-pressed={nurseAction?.id === action.id} onclick={() => { nurseSelection = { run: current.run_id, action: action.id }; }}>
                      <strong>{action.label}</strong><small>{action.status}</small>
                    </button>
                  {/each}
                </div>
                {#if nurseAction}
                  <div class="action-detail">
                    <h3>{nurseAction.label}</h3>
                    {@render eventList(nurseAction.events)}
                  </div>
                {:else}<p class="muted">No separate Nurse action recorded. Initial health evidence may be included in Plan & start.</p>{/if}
                <h3>After the intervention</h3>
                <div class="nurse-outcomes">
                  {#each flow.nurseOutcomes as outcome}
                    <div class="outcome {outcome.state}"><strong>{outcome.label}</strong><small>{outcome.status}</small></div>
                  {/each}
                </div>
                <p class="muted">Only recorded escalation or a linked new run confirms these paths. Completing a repair alone does not prove work continued.</p>
              </div>
              <div><h3>What happened</h3>{@render eventList(phase.events)}</div>
            </div>
          {:else}
            {#if phase.id === 'finalize'}<p class="muted">{phase.status} · Outcome and final records are shown together below.</p>{/if}
            {@render eventList(phase.events)}
          {/if}
        </section>
        <details><summary>Run plan and resources</summary>
          <p>{current.tier_reason}</p>
          <p class="muted">Started {new Date(current.run_start).toLocaleString()} · Deadline {new Date(current.deadline).toLocaleString()}</p>
          <h3>Scoped checks</h3><ul>{#each current.check_plan as check}<li>{check}</li>{/each}</ul>
          <h3>Resources</h3><ul>{#each current.resources as resource}<li>{resource.kind}: {resource.id} {resource.url || ''}</li>{/each}</ul>
          <p>Final records: {current.bookkeeping || 'not recorded'}</p>
        </details>
        {#if flow.otherEvents.length}<details><summary>Other recorded steps</summary>{@render eventList(flow.otherEvents)}</details>{/if}
      {/if}
    </section>
  {/if}
</section>

<style>
  .harness { width: 100%; max-width: 78rem; min-width: 0; margin: auto; padding: 1.5rem; color: var(--color-fulcra-black, #182025); background: var(--color-fulcra-white, #fff); overflow-wrap: anywhere; }
  .panel { padding: 1.5rem; margin: 1rem 0; border: 1px solid #b8c4c7; border-radius: .75rem; background: var(--color-fulcra-white, #fff); }
  h1 { font-size: 1.75rem; margin-bottom: .75rem; } h2 { font-size: 1.25rem; font-weight: 600; } h3 { font-size: 1rem; font-weight: 600; margin: .75rem 0; }
  p { margin: .6rem 0; line-height: 1.5; } ul { padding-left: 1.25rem; list-style: disc; } small { display: block; font-size: .75rem; }
  .heading { display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; }
  .run-controls { flex-wrap: wrap; align-items: center; }
  .run-controls select { flex: 1 1 16rem; min-width: 0; }
  select { display: block; width: 100%; min-height: 44px; font: inherit; color: #182025; background: white; border: 1px solid #849a9e; border-radius: .35rem; padding: .55rem; }
  .overview-columns, .nurse-columns { display: grid; grid-template-columns: minmax(0, 1.2fr) minmax(0, 1fr); gap: 1.5rem; margin-top: 1rem; }
  .overview-columns { border-top: 1px solid #d6dfe0; padding-top: 1rem; }
  .overview-columns > section { padding: .75rem; border-radius: .5rem; }
  .muted, .legend, small { color: #546168; } .muted, .legend { font-size: .8rem; }
  button { font: inherit; border: 1px solid #849a9e; border-radius: .35rem; background: white; color: #182025; padding: .55rem .75rem; cursor: pointer; min-height: 44px; }
  button:disabled { opacity: .55; cursor: default; } button[aria-pressed='true'] { outline: 2px solid #182025; outline-offset: 3px; }
  button:focus-visible, select:focus-visible, summary:focus-visible, .flow-scroll:focus-visible { outline: 3px solid #146dca; outline-offset: 4px; }
  .flow-scroll { overflow-x: auto; padding: 6px; margin: 1rem -6px 0; }
  .run-flow { position: relative; width: 918px; height: 156px; }
  .run-flow svg { position: absolute; inset: 0; }
  .connector { fill: none; stroke: #91a9ac; stroke-width: 1.4; marker-end: url(#run-arrow); } .arrow-head { fill: #91a9ac; }
  .flow-cell { position: absolute; width: 116px; height: 56px; padding: 5px; font-size: .75rem; line-height: 1.15; }
  .flow-cell strong, .nurse-action strong { display: block; font-weight: 600; } .flow-cell small { margin-top: 5px; font-size: .65rem; }
  .flow-cell.nurse { border-top: 3px solid var(--color-fulcra-orange, #ff9500); }
  .phase-detail { border-top: 1px solid #d6dfe0; margin-top: 1rem; padding-top: 1.25rem; }
  .nurse-flow { display: flex; flex-wrap: wrap; align-items: center; gap: 20px; padding: 5px; margin: 0 -5px 1rem; }
  .nurse-action { position: relative; width: 155px; min-height: 58px; font-size: .8rem; }
  .nurse-action:not(:last-child)::after { content: '→'; position: absolute; right: -18px; top: 20px; color: #91a9ac; }
  .nurse-action small { margin-top: 5px; }
  .nurse-outcomes { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; } .outcome { border: 1px solid #b8c4c7; border-radius: .4rem; padding: .75rem; }
  .outcome small { margin-top: .4rem; }
  .event-list { padding: 0; list-style: none; } .event-list li { border: 1px solid #dae3e3; padding: .85rem; margin: .75rem 0; border-radius: .4rem; }
  .event-list .heading { font-size: .85rem; } .event-list p { font-size: .85rem; }
  details { margin-top: .85rem; } summary { cursor: pointer; font-weight: 600; min-height: 30px; } .evidence { white-space: pre-wrap; overflow-wrap: anywhere; }
  .done { background: #e7f4ef; color: #225c43; border-color: #81b49e; }
  .waiting { background: #eaf2ff; color: #224e85; border-color: #5683bd; }
  .active { background: #e0f3f1; color: #15534f; border-color: #247c76; }
  .active::before { content: ''; position: absolute; right: 5px; top: 5px; width: 5px; height: 5px; border-radius: 50%; background: #247c76; animation: pulse 1.8s infinite; }
  .failed { color: var(--color-fulcra-purple-100, #2b2b69); background: #f1edff; border-color: var(--color-fulcra-purple, #7b61ff); }
  .attention { color: #784300; background: #fff3df; border-color: var(--color-fulcra-orange, #ff9500); padding: .65rem; border-radius: .4rem; }
  .skipped { opacity: .45; } .pending { color: #546168; }
  @keyframes pulse { 50% { opacity: .5; box-shadow: 0 0 0 5px #247c7620; } }
  @media (prefers-reduced-motion: reduce) { .active::before { animation: none; } }
  @media (max-width: 900px) { .overview-columns, .nurse-columns { grid-template-columns: minmax(0, 1fr); } }
  @media (max-width: 600px) { .harness { padding: .75rem; } .panel { padding: 1rem; } .run-controls > h2, .run-controls > select, .run-controls > button { flex: 1 1 100%; width: 100%; } }
</style>
