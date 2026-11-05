# Workspace

Durable requirements and closure history live in Fulcra File Store under
`workspace/<project-name>/`. Live status lives in the single structured Event
stream, not in markdown files polled by the dashboard.

## Structure

- `plan.md`: compact approved vision and Harness configuration (retry/time limits,
  overrides and a link to [control flow](harness-control-flow.md)).
- `spec.md`: full requirements and acceptance criteria, with M1 baseline/dashboard
  followed by feature milestones. Never compress away requirements. Fixed during a run.
- `decisions.md`: current user decisions in their exact words, with timestamp and
  context. Archive superseded decisions verbatim, linking the superseding entry.
- `progress.md`: compact milestone inventory, current/last run ID and outcome,
  attempts/repair budget, tier/reason/check plan, next actions, full Event type ID,
  deployment project ID/domain, resource IDs and history links.
- `outstanding-issues.md`: only open issues with run ID, time, observed problem
  and required action; resolved entries move to history with their resolution.
- `history/YYYYMMDD-HHMMSS_milestone_run-id.md`: every run, including failures and
  stops; changed code/revision, targets, actual commands/UI actions and results,
  tier/check plan, outcome, resources, retry counts and closure status.
- `history/decisions/<run-id>.md` and `history/resolved-issues/<run-id>.md`:
  immutable per-closure archives, so archiving never rewrites an expanding log.

Do not add a redundant current-context file or maintain a separate overview.md.
Existing overview files remain old history during a deliberate upgrade; move
unique useful information into progress before retiring their writes.

## Read once, pass context, write at closure

At startup, Coordinator/Nurse reads plan, full spec, current decisions, progress,
open issues and relevant history once. Pass this context among roles, including
the independent full-tier evaluator; roles do not re-download the same files.
Fetch older archived material only if diagnosis/requirements actually need it.
Reconcile live latest/full-run events with the startup snapshot before acting.

Planning/interview changes are saved together before a run, not per question.
User-requested changes update decisions/spec and insert the milestone before the
next run. Bootstrap and verify the durable Event type ID before the first run.
These are pre-run writes, not recurring live checkpoints.
Choose and persist retry/timeout overrides in `plan.md` before `RUN_START`, and
record the resulting absolute deadline in that run's events. Timed-out attempts
must stop and close; a later override applies only to a fresh attempt, not a
silent deadline extension or same-run resumption.

During work, use Event records only for current status, blockers and resource
creation. In particular, record newly created deploy IDs immediately in the live
stream; do not wait until closure or write progress.md mid-run. Keep local output
for closure and pass it between roles. The latest event carries compact summary,
next actions/open issues, tier/check plan and resource IDs, but evidence is a delta.

At closure, Coordinator writes the run's stable history path first, then updates
progress and changed issue/decision/archive files from the shared context. Nurse
contributes diagnosis and repair evidence. Verify each upload by reading its exact
target. Archive before removing a current entry. Superseded decisions retain the
original words, dates and context; resolved issues retain the problem and outcome.
Do not append full logs to current files. Full evidence belongs in run history.

Emit RUN_END with the actual product outcome and bookkeeping pending before these
writes. Emit BOOKKEEPING complete after readback. If interrupted, Nurse reconciles
which files landed and repairs only missing/stale bookkeeping using the same run
history path; do not double-count attempts or completions. Verified product work
is not regenerated. Missing product evidence follows the fresh-attempt rules in
[control flow](harness-control-flow.md#interrupted-attempts-diagnose-stop-close-start-fresh).
There is no same-run product resumption.

## File operations

Just before first accessing an upload destination, tell the user that you are
saving workspace files to Fulcra and name the hostname the transfer will use.
For direct storage uploads, use the Google hostname from the returned upload URL
(commonly `storage.googleapis.com`); if the tool returns a Fulcra-hosted relay URL,
name that hostname instead. Show only the hostname, never the signed URL or token.
Explain that restricted environments such as Claude may prompt for domain approval
or block the request, in which case the user may need to allow-list that hostname.
Continue with the upload after the notice; do not wait for a reply unless the
environment requires approval. Repeat only when a new upload hostname is needed.
If a request is blocked, report the hostname and required approval without
bypassing the restriction or claiming the file was saved. Other errors still need
their own diagnosis; not every upload failure is an allow-list problem.

```bash
uvx fulcra-api file download "workspace/<project-name>/progress.md" ./progress.md
uvx fulcra-api file upload ./progress.md "workspace/<project-name>/progress.md"
uvx fulcra-api file list "workspace/<project-name>/"
```

Use the same operations for the other files. Never put tokens/cookies in the
workspace. Record user decisions only when actually given, not inferred to make
a failed review pass. Keep failed/interrupted history as carefully as successful
history, including actual runtime stop confirmation and inspected reusable IDs.
