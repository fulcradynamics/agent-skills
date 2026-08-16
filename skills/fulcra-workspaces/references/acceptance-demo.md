# Two-Agent Acceptance Demo

This demo shows the behavior the automated pair test proves. It assumes no
prior knowledge of Coord.

1. Two agents run `setup`; both adopt one account Bus and only one channel is
   created.
2. Each runs `join`. Its logical identity and current machine/cloud/harness/model
   attribution become append-only Fulcra data and a Bus pointer. If an identity
   moves, the next profile points to the previous one.
3. The first agent sends a message. Workspaces verifies the durable message and
   recipient index before publishing the small Bus event.
4. The second agent runs one `queue` read. It receives only relevant events and
   selected pointer bodies. It processes each and writes a receipt before cursor
   advancement. Re-reading old coverage suppresses the side effect by receipt.
5. The second agent checkpoints objective, decisions, completed work, next
   actions, questions, and pointers. A fresh process resumes from a bounded,
   digest-verified brief.
6. The agents define an exclusive reviewer role. The first agent claims it,
   writes and verifies a role checkpoint, then releases through `role-handoff`.
   The second agent claims the role from another harness and uses `role-resume`
   to recover the first holder's decisions and next actions.
7. The first agent sends a file. Bytes stay in the File Store; the Bus carries
   only the manifest pointer. The receiver verifies recipient, size, and SHA-256
   before accepting it.
8. An injected Bus read failure reports `UNKNOWN`, never `CLEAR`. A legacy
   workspace with files but no verified Bus reports `STORE_ONLY`.
9. An injected malformed event is returned as visible poison, consumed, and
   cannot prevent a healthy event or the next queue window from progressing.

The executable proof is
`scripts/tests/test_acceptance_pair.py`. It uses an in-memory account and no
private fleet names, credentials, or routing policy.
