---
name: fulcra-agent-review-cli
description: "Exact commands for the review handshake: request, verdict, and the coord-engine tally."
---

# Fulcra Agent Review — CLI reference

Requesting a review and reading the tally are `coord-engine` commands; leaving a verdict is a
`fulcra-api file` upload (needs `fulcra-api auth login`).

## Request review (author)
```bash
# writes the review doc (type: Review) at team/<team>/review/pr-42.md and registers the required reviewers
coord-engine review request <team> pr-42 \
  --of https://github.com/org/repo/pull/42 \
  --reviewer reviewer --reviewer security     # roles preferred; repeat --reviewer for many
```
Each required reviewer's obligation now shows up in `coord-engine needs-me <team> --agent <role>` and
persists until their verdict file exists — no separate inbox notice to send. Re-running an identical
request is idempotent recovery (re-delivers a dropped notice and converges); changing `--of` or the
reviewer set is refused (exit 1) — re-open under a new slug instead.

## Leave a verdict (reviewer)
```bash
# type: Verdict, reviewer: <you>, verdict: approve|changes
uv tool run fulcra-api file upload /tmp/verdict.md \
  "team/<team>/review/pr-42/verdicts/<you>.md"
# then notify the author's inbox (same lifecycle). Re-upload to change your verdict (last wins).
```

## Check state (deterministic — do not tally by hand)
```bash
coord-engine review status <team> pr-42 --json
# {state: APPROVED|CHANGES|PENDING, approvals:[...], changes:[...], required:[...], pending_required:[...]}
```
- **CHANGES** — any reviewer requested changes (a single blocker dominates).
- **APPROVED** — ≥1 approval, no outstanding changes, and every `required` reviewer approved.
- **PENDING** — otherwise (no verdicts yet, or required reviewers haven't voted).
- **exit 1** — the review doc is unreadable (transport failure or nonexistent slug); the tally is
  *unknown, retry*, not a state. Never fold a missing doc into APPROVED.

Verdict synonyms accepted: `approve|approved|lgtm` and `changes|request-changes|reject|rejected`.
