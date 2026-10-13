# Workspace

Lightweight tracking structure for app-building progress and history. Enables resume capability without the complexity of multi-agent coordination.

## Purpose

The workspace provides:
- **Resume capability** — Pick up where you left off after interruption
- **History preservation** — Record of completed milestones and decisions
- **Current state visibility** — Single source of truth for what's done and what's next

All files live in Fulcra File Store under `workspace/<project-name>/`.

## Structure

```
workspace/<project-name>/
├── plan.md              # Approved enhancement plan (from step 1)
├── spec.md              # Requirements and milestones (from interview)
├── decisions.md         # Specific user decisions, preserved verbatim
├── overview.md          # Concise progress + milestone summary (nurse, each loop)
├── progress.md          # Current state snapshot
├── outstanding-issues.md # Issues requiring user attention
└── history/             # Timestamped run outcomes and evaluation evidence
    └── YYYYMMDD-HHMMSS_milestone-name_run-id.md
```

### plan.md

Created in step 1 after user approval. Contains:
- Core app idea
- Fulcra-enabled enhancements
- High-level vision
- Harness section: notes the product is built and iterated through harness runs,
  links to [`harness-control-flow.md`](harness-control-flow.md), and records the
  current harness configuration (retry counts, per-run timeout, and any other
  settings), including any overrides the user or agent introduces

This is the approved plan that guides spec creation and implementation.

### spec.md

Created during the interview step. Contains:
- App description and purpose
- Milestone breakdown beginning with **M1 — Working baseline and harness dashboard**;
  include the [M1 handoff checks](harness-dashboard-setup.md#evaluate-m1-before-handoff),
  then app-specific milestones starting at M2
- Key features and requirements

Updated as requirements evolve.

### decisions.md

An append-only log of **specific decisions the user has made**, preserved in the
user's own terms rather than paraphrased or summarized away. This is the durable
record of user intent that the spec and milestones must honor. Decisions come
from three sources:

- The **interview** (step 3) — concrete choices the user makes while shaping the
  spec.
- **Escalations** — how the user resolves an issue the Nurse escalated.
- **New features or requirements** the user introduces later.

Preserve the actual decision (the specific choice, value, or constraint), not a
restatement. Never overwrite or reinterpret past entries — append new ones.
Recording a decision here does not license changing `spec.md` on its own: the
spec changes only through the user (a new requirement or an escalation
response), and this file captures exactly what they decided.

Format:
```markdown
# Decisions

## [ISO-8601 timestamp] - Interview
**Decision:** <the specific choice, in the user's terms>
**Context:** <the question or situation that prompted it>

## [ISO-8601 timestamp] - Escalation - Run <run-id>
**Decision:** <what the user chose>
**Context:** <the issue that was escalated>

## [ISO-8601 timestamp] - New requirement
**Decision:** <the new feature/requirement, specifically>
**Context:** <where it came from>
```

### overview.md

Concise, human-readable summary the harness dashboard renders at the top as
styled markdown. Rewritten (not appended) by the Nurse on every loop. Covers
overall status, a milestone checklist, and recent activity. This is a snapshot
for a human skimming the dashboard — keep it short; the detailed state lives in
progress.md. See [`harness-control-flow.md`](harness-control-flow.md) for the
suggested format.

### progress.md

Single source of truth for current state. Updated by Coordinator after each harness run.

Suggested sections:
- **Current Status** — Where we are, what's working
- **Active Milestone** — Current milestone name from spec.md
- **Harness State** — Full annotation data type ID, current `run_id`, role/step,
  run status, retry count, last run timestamp, and evidence/history links
- **Next Actions** — Specific next steps
- **Recent Completions** — Last 3-5 completed milestones with dates
- **Deployment** — Deploy project `id` and `domain` (or that the user's own Vercel
  account is used); see [`deploy.md`](deploy.md)
- **Open Questions** — Anything blocking or unclear
- **Notes** — Context worth preserving

### outstanding-issues.md

Issues requiring user attention. Updated by Nurse when escalations occur.

Format:
```markdown
# Outstanding Issues

## [ISO-8601 timestamp] - Run <run-id>

**Issue:** <description>
**Action Needed:** <what user should do>

---

## [timestamp] - Run <older-run-id> [RESOLVED]

**Issue:** <description>
**Resolution:** <how it was resolved>
```

### history/

Keep a timestamped history entry for each run, including failed or interrupted
attempts; never preserve only successful results. The Coordinator records
milestone completion only after a passing evaluation.

Suggested content:
- What was built
- Key decisions made during generation
- Review notes and issues found
- Run ID, milestone/attempt, actual tool commands and results, deployment URL,
  and links to evaluation evidence (without credentials or tokens)
- Any retries and what was attempted
- Context for next milestone

## Fulcra File Operations

Upload and download workspace files using `uvx fulcra-api file`:

```bash
# Upload to workspace
uvx fulcra-api file upload /local/path/spec.md "workspace/<project-name>/spec.md"

# Download from workspace
uvx fulcra-api file download "workspace/<project-name>/progress.md" /local/path/progress.md

# List workspace files
uvx fulcra-api file list "workspace/<project-name>/"
```

## Update Patterns

### During Idea and Enhancement (Step 1)
- Create plan.md with approved enhancement vision
- Upload to `workspace/<project-name>/plan.md`
- Initialize progress.md with empty state
- Upload to `workspace/<project-name>/progress.md`

### During Interview for Spec (Step 3)
- Keep a running local note of each specific decision the user makes (preserve their exact choice) — don't upload after every question, as that slows the interview
- Create spec.md locally based on clarifying questions and plan
- At the end, upload both together: spec.md to `workspace/<project-name>/spec.md` and the collected decisions to `workspace/<project-name>/decisions.md`

### When the user introduces a new feature or requirement
- Append the specific new feature/requirement to decisions.md and upload it
- Reflect it in spec.md (this user-introduced change is a valid reason to update the spec)

### When the user reports an app bug or requests an adjustment
- Update decisions.md and spec.md with the user's guidance and acceptance criteria.
- Insert a regular milestone immediately after the last completed milestone,
  named for that position (e.g., `m2-1` after M2), and update progress.md.
- Upload these files before implementation, then [run the harness as usual](harness-control-flow.md#user-reported-bugs-and-adjustments).

### During Harness Runs

**Coordinator** (after every run, including failures):
- Downloads current progress.md
- Records the run ID, outcome, retries, blockers, and evidence links; adds to
  Recent Completions only after a passing review
- Clears or updates Active Milestone
- Uploads updated progress.md
- Creates timestamped history file
- Uploads to `workspace/<project-name>/history/YYYYMMDD-HHMMSS_milestone-name_run-id.md`

**Generator** (before starting work):
- Downloads progress.md and spec.md
- Reads current state and milestone requirements
- May reference recent history for context

**Evaluator** (during review):
- May download recent history files to understand patterns/issues

**Nurse** (during health checks):
- Downloads progress.md to understand current state
- May review history when diagnosing stuck runs
- Rewrites overview.md each loop with the current status, milestone checklist, and recent activity
- On escalation, records the user's resolution in decisions.md once they respond (preserve their specific decision), and uploads it

## Resume Pattern

When resuming work after interruption:

1. Download and read `progress.md` → See active milestone, harness state, and current status
2. Download and read `spec.md` → Find milestone requirements
3. Download and read `decisions.md` → Honor the specific decisions the user has made
4. Download `plan.md` → Understand approved vision and harness configuration
5. Download relevant history files → Preserve prior decisions and regression evidence
6. Reconcile stored run state with annotation events. Do not mark interrupted
   work complete without evaluation evidence; apply the retry/timeout rules and
   continue through the harness, using a new run ID for the next attempt.

The Coordinator uses this same pattern to find the next incomplete milestone.

## Integration with Harness Flow

Workspace updates happen at natural points in the harness cycle:

- **Before generate**: Generator reads workspace for context
- **After milestone passes review**: Coordinator updates progress and creates history
- **During health check**: Nurse reads workspace to diagnose issues

No additional harness steps needed—workspace reads/writes fit into existing role responsibilities.
