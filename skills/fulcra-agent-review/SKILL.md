---
name: fulcra-agent-review
description: "Add a review handshake to a fulcra-agent-teams space: request review of an artifact (PR, doc, plan), reviewers leave verdicts, and the overall APPROVED/CHANGES/PENDING state is computed deterministically — including required-reviewer gating."
homepage: "https://github.com/fulcradynamics/agent-skills"
license: "MIT"
user-invocable: true
metadata: { "openclaw": { "emoji": "🔎" } }
---

# Fulcra Agent Review

## Installation

This skill uses the `coord-engine` CLI — a small, stdlib-only tool that runs the deterministic folds. Install it once:

```bash
uv tool install "git+https://github.com/ashfulcra/fulcra-tools@coord-engine-v1.6.3#subdirectory=packages/coord-engine"
```

After installation, `coord-engine <command>` is on your PATH.

Enhances the [`fulcra-agent-teams`](https://github.com/fulcradynamics/agent-skills) skill with a
lightweight **review handshake**: an author requests review of an artifact, one or more reviewers leave
verdicts, and the overall state is folded deterministically. Requesting a review and reading the tally
are `coord-engine` commands; leaving a verdict is a single-file write. Folding multiple reviewers is a
derived state — code, not eyeballing.

## Layout (under `team/<team>/review/<slug>/`)
- **`review/<slug>.md`** — the review request, written by `review request` (below). OKF `type: Review`.
  `<slug>` is a short id for the artifact (e.g. `pr-42`). The `required` list is what the tally gates on —
  name **roles** where you can (`reviewer`, `security`), so the obligation follows whoever holds the role
  rather than a named session:
  ```yaml
  ---
  type: Review
  schema: review-request/v1
  requested_by: ash
  of: https://github.com/org/repo/pull/42
  required: [reviewer, security]   # all must approve for APPROVED (a "a, b" string also parses)
  ---
  Review requested: <artifact>
  ```
- **`review/<slug>/verdicts/<required-token>.md`** — one verdict per requirement. The **filename stem is
  the tally key** and must equal a `required` token (the role, or the direct agent name), not the holder's
  own name. OKF `type: Verdict`:
  ```yaml
  ---
  type: Verdict
  reviewer: alice             # who signed off (informational — the FILENAME drives the tally)
  verdict: approve            # approve | changes
  ---
  Notes / requested changes.
  ```

## Lifecycle
1. **Request** (author) — one command, not a hand-written doc:
   ```bash
   coord-engine review request <team> <slug-or-title> \
       --of <artifact> --reviewer <role> [--reviewer <role> …] [--from <me>]
   ```
   This writes `review/<slug>.md` at the exact path the tally reads and echoes the verdict path each
   required reviewer must fill. The request doc IS the durable obligation: it surfaces in every required
   reviewer's `coord-engine needs-me` as a pending marker and stays there until that reviewer's verdict
   file exists — no inbox message to remember, and no way for a dropped review to gate on nothing.
   Re-running the same request is safe: an identical `<slug>`/`--of`/reviewer set is **idempotent
   recovery** (it re-delivers any reviewer notice a prior partial failure dropped and converges), while a
   request that changes `--of` or the reviewer set is refused (exit 1) — a changed review is a **new
   slug**, never an overwrite of the old one.
2. **Verdict** (reviewer): write the verdict file at the **exact path `review request` echoed** for you,
   with `verdict: approve|changes` and notes, then drop a message into the author's inbox. The **filename
   stem is what the tally matches against the `required` token** — not the frontmatter `reviewer:` field —
   so name the file after the requirement, not after yourself:
   - **role requirement** (`required: reviewer`) → `review/<slug>/verdicts/reviewer.md`, whoever you are.
     Writing `verdicts/alice.md` records an approval the tally can't credit: `reviewer` stays in
     `pending_required` and the review can never reach APPROVED.
   - **direct requirement** (`required: alice`) → `review/<slug>/verdicts/alice.md`.

   To change your mind, re-upload the same file (overwrites; the File Store keeps the history).
   **Fail-closed:** a `changes` verdict keeps blocking until that same file is re-uploaded as `approve` —
   pushing a fix does **not** clear it; the requirement must be re-affirmed.
3. **Check state** (anyone) — deterministic fold, do not tally by hand:
   ```bash
   coord-engine review status <team> <slug> --json
   # -> {state: APPROVED|CHANGES|PENDING, approvals, changes, required, pending_required}
   ```
   **CHANGES** if any reviewer requests changes; **APPROVED** if there's an approval, no outstanding
   changes, and all `required` reviewers approved; **PENDING** otherwise.

   **Fail loud on an unreadable tally.** If the review doc can't be read — transport hiccup or a slug that
   doesn't exist — `review status` **exits 1** (`... tally unknown, retry`) instead of guessing. Without
   the `required` list a lone approval would fold to a clean APPROVED and durably hide a pending review, so
   a watcher must treat exit 1 as *transport down, retry* — never as a settled state.

## When to use
- Gating a merge/land on review in a multi-agent team.
- Any "N reviewers must sign off" flow where you need an unambiguous, non-drifting verdict state.

See [`references/review-cli.md`](references/review-cli.md) for exact commands.
