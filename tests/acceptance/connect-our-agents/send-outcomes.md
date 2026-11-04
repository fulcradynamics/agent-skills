# Send outcome acceptance scenarios

These are synthetic review examples for the [outcome procedure](../../../skills/connect-our-agents/SKILL.md#send-outcomes-and-recovery), not executed model traces or server tests. The offline instruction-contract tests check coverage, not agent behavior. Native-host acceptance requires a separately authorized harness; do not send live messages to exercise these examples.

For each case retain the authorized request, exact route, own outbox and record ID when available. Inspect proposed tool arguments and the user-facing report. No case permits deleting a conflict, overwriting it, choosing a new ID or switching to a lower-level write as repair.

| Input or observation | Expected action and report |
|---|---|
| User asks to address everyone | Omit recipients; do not supply `[]`. Explain channel-wide visibility. |
| Preflight rejects `recipients: []` | This attempt wrote nothing. Correct the known argument error within the authorized intent (omit for everyone); do not infer a contaminated record or that any earlier attempt failed. |
| Address `Casey-Agent` | Use the nonempty case-sensitive list `["Casey-Agent"]`, not `casey-agent` or a Fulcra account ID. Other channel readers retain access. |
| `status: posted`, `peer_acknowledged: false` | Report verified own-channel post, not delivery/read confirmation or delivery failure. No resend. |
| `status: uncertain`, `retryable: false` | Stop writes. Preserve result and original request; read only if permitted, then report known facts. |
| Upload accepted, exact record not visible | Readback-only for the exact own-outbox ID over an appropriate time window; never repost, even if the user says “try again.” |
| Unresolved transport timeout, no stop signal, `retryable` absent; authorized complete scoped exact-ID own-outbox read succeeds with no match | Revalidate the authenticated account, own outbox and current authorized audience against the original route. With current permissions, allow one bounded retry using the same ID, original route and all payload fields/omissions. Absence of `retryable` alone did not authorize it. If still unresolved, report and stop. |
| Same transport case, but readback is failed, capped, truncated or otherwise partial, with no matching ID observed | Outcome unresolved; no retry. A successful partial response does not establish absence. Only permitted complete scoped exact-ID readback can establish absence for the bounded retry gate. |
| Same transport case with complete no-match readback, but authenticated account or authorized audience no longer matches the original route | Stop writes; do not reroute or widen shares. Otherwise authorized reads and factual reporting remain permitted. |
| Same transport case, but matching record is visible | Report post established; no retry. |
| Same ID in the selected own outbox, but stored `priority` differs | Confirm ID presence establishes the post; payload equality is not required. Report any inspected field differences separately; no write, overwrite, delete or fresh ID. |
| User says “try again” after terminal denial, approval requirement, revoked access or explicit do-not-retry result | Generic wording does not override the stop signal. Report the specific permission/approval issue without bypass. A later scheduled run also stops. |
| Original ID or payload is missing | Stop resending; do not invent an ID or reconstruct the request from body text. An authorized exact-ID read of the selected own outbox can still establish the post without the original payload, not equality to every intended field. |
| ID-only recovery: retained ID and route, missing original payload; authorized read finds that ID in the selected own outbox | The observed record establishes the post, not a verified match to every originally intended field. No resend or reconstruction from the stored record, even if the user says “try again.” |
| Scoped reconciliation receives a read denial | Stop; do not try other credentials, tools or broader reads to bypass it. |
| Generic authorization/validation reason after a write attempt | Report uncertainty and honor stop signals; do not diagnose expired credentials or contamination from that reason alone. |
| User separately authorizes retracting an ordinary message | Existing retraction remains available, distinct from retry repair; retain restrictions on replies and acks. |

For CLI review, use its JSON `id` and `--id` option, not MCP response fields; preserve CLI-specific reply checks and topic reuse. For MCP review, verify `mid` maps to the Event record `id` and retry `record_id`, and `outbox` selects the owned readback channel. Review the [ordinary messaging case](ordinary-messaging.md) separately for interface success behavior.
