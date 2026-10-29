# Harness Control Flow

One run attempts one milestone. The harness is a tool-executed workflow, not a
checkpoint service. M1 is always the working baseline and owner dashboard;
app-specific features start at M2.

## Roles and tiers

- **Nurse** diagnoses interruptions, verifies workers have stopped, repairs and
  monitors harness machinery. Only this role modifies the harness.
- **Coordinator** selects the earliest incomplete milestone, autonomously chooses
  a tier with a reason and scoped check plan, operates the run, inspects evidence,
  and closes it. Announce the choice; the user may override it.
- **Generator** implements the milestone and proportionate affected tests.
- **Evaluator** evaluates against the fixed spec, actual product behavior and
  relevant regressions, not the Generator's claims.

| Tier | Scope | Required checks and independence |
| --- | --- | --- |
| light | Presentation-only | Affected visual/browser checks and basic real evidence. No independent reviewer required. |
| focused | Contained behavior change to an existing feature | Affected tests and changed user journey. Independent review optional. |
| full | New features, cross-cutting, complex or security-sensitive changes; always M1 | Scoped acceptance and regression checks plus a separate evaluator agent/context. |

Full does not mean every unrelated suite. Coordinator escalates the tier when
inspection/testing reveals uncertainty or broader impact. Record the new reason
and additional checks before continuing; never weaken the spec or omit a
required check to obtain a pass. If a separate evaluator is unavailable for full,
record the blocker and escalate, rather than silently evaluating in the same context.
Light/focused may execute roles sequentially in one agent, but checking remains
an explicit phase after implementation, not a claim that writing code suffices.

## Rules

- The spec is fixed during a run. Only user requirements/escalation responses
  change it before the next run. A failing spec is not permission to rewrite it.
- Every tier requires real tool checks and meaningful evidence. Record commands
  or UI actions, tested target/revision, expected behavior and actual results.
  Builds, reading code and API calls alone do not establish a user journey.
  Missing tools/credentials/checks are blockers, not passes.
- Preserve template authentication. For authenticated checks use the existing
  `fulcra_access_token` HTTP-only cookie and the CLI access token without logging
  credentials. Test backend denials, not only hidden controls.
- When establishing/changing sign-in, test device-flow startup and authenticated
  behavior. Ask the user to complete interactive sign-in once at the deployed URL;
  keep that explicit non-blocking confirmation in live `open_issues`, then at
  closure in `outstanding-issues.md`. Resolve only after confirmation.
- Default **two retries per milestone**, three total attempts. Nurse repairs also
  have two retries, three total tries. Default **15-minute timeout per run**.
  Failed, stopped and interrupted product attempts consume the milestone budget.
  No restart resets retry counts. Stop timed-out workers via actual runtime
  controls and close the timed-out attempt. Choose and persist these limits and
  any explicit override in plan's Harness section before the attempt's `RUN_START`,
  then derive its absolute deadline from that configuration. Never silently extend
  an existing deadline; an override for a fresh attempt does not resume a closed run.

## Setup

Read [workspace.md](workspace.md) once at startup, including relevant history.
Pass the context to subsequent roles, including the separate evaluator. Nurse
reconciles saved IDs/state with live events and runtime before another attempt.
Check `progress.md` and the catalog before creating any type. Reuse a saved v1
Event type after inspecting its schema; legacy apps require the deliberate
[upgrade](harness-dashboard-setup.md#existing-app-upgrade), not automatic replacement.

Before the first run, Nurse creates the one custom Event type following
[harness-events.md](harness-events.md), saves its full `Event/<UUID>` ID durably
in `progress.md`, and verifies the saved file and schema. This bootstrap write
is before the run. Do not create another type for dashboard wiring.
If creation has an ambiguous result, resolve it through catalog/metadata before
retrying; never silently create duplicates.

Coordinator selects milestone/tier/check plan, mints a fresh `run_id`, sets
`run_start`, `attempt` and absolute `deadline`, and records/read-backs `RUN_START`
with Nurse health-check evidence before implementation. Include the actual
runtime/session handle when workers are started. Emit `FIND_MILESTONE`, then
`GENERATE` started/completed as work happens. M1 baseline deployment and Nurse's
dashboard implementation are inside this run, not untracked prerequisites.

## Run flow and evidence

1. Generate within the selected scope. Record created resource IDs immediately
   as `RESOURCE_CREATED` events before using them (especially deploy project ID
   and domain). Keep the small resource list in subsequent events. Do not write
   the workspace mid-run. On an uncertain creation response, inspect/reconcile
   the resource rather than creating another.
2. Execute `CHECK` for light/focused, or `REVIEW` with the separate evaluator for
   full. Optional focused independent review may also use `REVIEW`. Record actual
   starts/results. M1 must pass every [deployed handoff gate](harness-dashboard-setup.md#evaluate-m1-before-handoff).
3. Coordinator inspects evidence covering the scoped check plan. Only then emit
   `MARK_COMPLETE`. Emit `RUN_END` with explicit `outcome`: `passed`,
   `retry-needed`, `stopped`, or `escalated`. During work it is `running`.
   A failed check with budget left means `retry-needed`, not a successful run.
   Exhausted retries mean `escalated`; retain the incomplete milestone.
4. Close workspace/history, including failures/stops. Record `bookkeeping:
   "pending"` on `RUN_END`, then `BOOKKEEPING` completed with `bookkeeping:
   "complete"` after verifying closure uploads. Preserve the terminal product
   outcome on bookkeeping events. If no milestone remains, explicitly record
   `PROJECT_COMPLETE` with evidence of the milestone inventory; missing generation
   is never evidence of completion.

Each event contains only its new evidence, not an accumulating transcript.
Started events describe actual setup observed so far, never future successes.
Failure evidence includes what was attempted, failure output, and blocked checks.
Use concise inline results and history paths for longer output; links alone or
"tests passed" are insufficient. Never include credentials or private user data.
Coarse progress events every few minutes are enough; all evidence remains in the
expandable timeline. Keep the small current summary/next actions/open issues,
resource IDs and run metadata on every record so latest is useful independently.

## Interrupted attempts: diagnose, stop, close, start fresh

There is **no same-run resumption** and no checkpoint framework.

1. Nurse reads the latest event then the full run from its `run_start`, checks
   saved history and inspects actual code/deployed resources. Diagnose unfinished
   work versus a bookkeeping-only failure. Do not assume earlier checks passed.
2. Inspect the recorded worker handle with the runtime's actual process/session
   controls. If active, cancel/terminate and wait/poll for confirmed termination,
   including spawned workers. Save the observed result as evidence. A `stopped`
   event does not stop a process. If controls or confirmation are unavailable,
   escalate and do not launch competing work.
3. Close the failed/interrupted attempt under its original ID, with stop evidence,
   outcome, retry consumption, resources and unresolved actions. Preserve its
   history. Repair harness faults within the separate repair budget.
4. If budget remains, start a **fresh run ID** with `previous_run_id`, the next
   attempt number and a new bounded deadline. Inspect and reuse suitable code,
   type/deploy IDs and other resources, but rerun the required scoped checks for
   the new attempt; reused code is not inherited success.

Bookkeeping-only recovery is not a new product attempt: if verified check and
terminal evidence already establish the product outcome, Nurse repairs missing
closure files and records `BOOKKEEPING` for that closed run. Do not regenerate,
redeploy or rerun verified product work. Read back only affected closure targets
and retain the original outcome; this is not resuming execution. If evidence is
insufficient, follow interrupted-attempt handling instead.

## User-reported Bugs and Adjustments

Before the next run, preserve the user's exact decision, update spec acceptance
criteria, and insert a pending milestone after the last completed milestone
(e.g. `m2-1` between M2 and M3, then `m2-2`). Update progress and select an
appropriate tier. The same evidence, retry and closure rules apply.
