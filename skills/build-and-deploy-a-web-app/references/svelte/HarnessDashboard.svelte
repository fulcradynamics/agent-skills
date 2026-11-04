<script lang="ts">
  import { onMount } from 'svelte';
  import { HarnessFeed } from '$lib/harness-feed.js';
  import { groupRuns } from '$lib/harness-state.js';

  let runs: any[] = $state([]);
  let selected: string | null = $state(null);
  let isOwner = $state(false);
  let loading = $state(true);
  let message = $state('');
  let historyMessage = $state('');
  let lastSuccess = $state('');
  let now = $state(Date.now());
  let historyEnd = $state('');
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
  let stale = $derived(!!lastSuccess && now - Date.parse(lastSuccess) > 15000);
  let overdue = $derived(latest?.outcome === 'running' && now > Date.parse(latest.deadline));

  function sync() {
    runs = groupRuns(feed.events);
    selected = feed.selected;
  }

  async function poll() {
    try {
      await feed.refresh();
      sync();
      lastSuccess = feed.lastRead || '';
      if (!historyEnd && runs.length) historyEnd = runs.at(-1).run_start;
      message = '';
    } catch (error) {
      message = error instanceof Error ? error.message : 'Refresh failed';
    }
  }

  async function openRun(run: any) {
    feed.selected = run.run_id;
    selected = run.run_id;
    try {
      // Explicit selection reconciles late history, not only its cached slice.
      await feed.history(run.run_start, new Date().toISOString());
      sync();
    } catch (error) {
      historyMessage = String(error);
    }
  }

  async function older() {
    historyBusy = true;
    const end = historyEnd || new Date().toISOString();
    const start = new Date(Date.parse(end) - 30 * 86400000).toISOString();
    try {
      if (await feed.history(start, end)) {
        sync();
        historyEnd = start;
        historyMessage = `Loaded history from ${start} to ${end}. Load again to go further back.`;
      }
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

<section class="harness">
  <h1>Harness Dashboard</h1>
  {#if loading}<p>Loading owner access…</p>{/if}
  {#if message}<p role="alert" class="warning">{message} {lastSuccess ? 'Showing retained data.' : ''}</p>{/if}
  {#if isOwner}
    <p class="muted" aria-live="polite">{stale ? 'Stale data — ' : ''}Last successful refresh: {lastSuccess ? new Date(lastSuccess).toLocaleString() : 'not yet'}</p>
    {#if latest}
      <section class="card">
        <h2>Current project</h2>
        <p>{latest.project_summary}</p>
        <p>{latest.milestone} · {latest.tier} · <strong>{latest.outcome}</strong></p>
        <h3>Next actions</h3>
        <ul>{#each latest.next_actions as action}<li>{action}</li>{/each}</ul>
        <h3>Open issues</h3>
        {#if latest.open_issues.length}<ul>{#each latest.open_issues as issue}<li>{issue}</li>{/each}</ul>{:else}<p>No open issues recorded.</p>{/if}
        {#if overdue}<p class="warning">Deadline passed without a terminal outcome. Nurse intervention needed; this is not an automatic stop confirmation.</p>{/if}
        {#if selected !== latest.run_id}<button onclick={() => openRun(latest)}>View latest run</button>{/if}
      </section>
    {:else if !loading && !message}<p>No run events yet. This is not evidence of completion.</p>{/if}
    {#if current}
      <section class="card">
        <h2>{current.milestone} — {current.outcome}</h2>
        <p>Run {current.run_id} · Attempt {current.attempt} · {current.tier}</p>
        <p>{current.tier_reason}</p>
        <p class="muted">Started {new Date(current.run_start).toLocaleString()} · Deadline {new Date(current.deadline).toLocaleString()}</p>
        <h3>Scoped checks</h3>
        <ul>{#each current.check_plan as check}<li>{check}</li>{/each}</ul>
        <h3>Actual step timeline</h3>
        <ol class="run-timeline">
          {#each current.events as event (event.id)}
            <li class:nurse={event.role === 'Nurse'}>
              <strong>{event.role === 'Nurse' ? 'Nurse intervention · ' : ''}{event.step} — {event.status}</strong>
              <p>{event.detail}</p>
              <small>{event.role} · {new Date(event.start_time).toLocaleString()}</small>
              <details><summary>Evidence</summary><p class="evidence">{event.evidence}</p></details>
            </li>
          {/each}
        </ol>
        <details><summary>Resources and bookkeeping</summary>
          <ul>{#each current.resources as resource}<li>{resource.kind}: {resource.id} {resource.url || ''}</li>{/each}</ul>
          <p>Bookkeeping: {current.bookkeeping || 'not recorded'}</p>
        </details>
      </section>
    {/if}
    <details class="card"><summary>Run history</summary>
      <ul>{#each runs as run}<li><button aria-pressed={selected === run.run_id} onclick={() => openRun(run)}>{run.milestone} · {run.run_id} · {run.outcome}</button></li>{/each}</ul>
      <button disabled={historyBusy} onclick={older}>Load older 30-day window</button>
      <p aria-live="polite">{historyMessage}</p>
    </details>
  {/if}
</section>

<style>
  .harness { width: 100%; max-width: 64rem; min-width: 0; margin: auto; padding: 1.5rem; color: var(--color-fulcra-black, #182025); background: var(--color-fulcra-white, white); overflow-wrap: anywhere; }
  .card { padding: 1.25rem; margin: 1rem 0; border: 1px solid #b8c4c7; border-radius: .75rem; background: var(--color-fulcra-white, white); }
  h1 { font-size: 1.75rem; } h2 { font-size: 1.3rem; } h3 { margin-top: 1rem; font-weight: 600; }
  p { margin: .5rem 0; } ul, ol { padding-left: 1.5rem; }
  .muted, small { color: #546168; } .warning { padding: .75rem; background: #fff1d6; color: #713b00; }
  .run-timeline { display: block; }
  .run-timeline li { border-left: 3px solid #86a9ac; padding: .75rem; margin: .75rem 0; }
  .run-timeline .nurse { border-color: #b16b13; }
  .evidence { white-space: pre-wrap; overflow-wrap: anywhere; }
  button { border: 1px solid #678387; border-radius: .3rem; padding: .4rem .7rem; margin: .2rem; cursor: pointer; }
  button[aria-pressed='true'] { background: #d5eeeb; } summary { cursor: pointer; font-weight: 600; }
</style>
