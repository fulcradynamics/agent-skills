# Workspaces Portable Roles Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a portable, durable role lifecycle and role-bound continuity handoff directly to Fulcra Workspaces.

**Architecture:** A focused `RoleService` owns immutable definitions and append-only lease transitions with verified projections. `ContinuityService` adds an optional role binding and bounded role resume, while a small `RoleHandoffService` enforces checkpoint-before-release ordering. Explicit role operations may make bounded Store reads; normal Bus queue reads remain unchanged.

**Tech Stack:** Python 3 standard library, existing `FulcraTransport`, `Outcome`/`State`, pytest, Markdown protocol contracts.

## Global Constraints

- Preserve one bounded Bus read on the normal wake path.
- Do not require File Store delete or compare-and-swap.
- Store authoritative transitions append-only and verify every mutable projection.
- Return `UNKNOWN` for unreadable or unverifiable state; never infer vacancy from failed reads.
- Keep live machine, harness, model, identity, and routing mappings out of the repository.
- Do not add role-addressed delivery, escalation, presence, review policy, obligation folds, or forge integration.

---

### Task 1: Durable Role Definitions And Lease Fold

**Files:**
- Create: `skills/fulcra-workspaces/scripts/fulcra_workspaces/roles.py`
- Create: `skills/fulcra-workspaces/scripts/tests/test_roles.py`

**Interfaces:**
- Produces: `RoleService(transport: Any, state_dir: Path, *, max_holders: int = 100)`
- Produces: `define(workspace: str, role: str, policy: str, lease_seconds: int, description: str) -> Outcome`
- Produces: `claim(workspace: str, role: str, identity: str, *, now: str, event_id: str | None = None, session_nonce: str | None = None, takeover: bool = False) -> Outcome`
- Produces: `release(workspace: str, role: str, identity: str, *, now: str, event_id: str | None = None, session_nonce: str | None = None) -> Outcome`
- Produces: `status(workspace: str, role: str, *, now: str) -> Outcome`
- Produces: `parse_role(raw: object) -> dict[str, Any] | None` and `parse_lease(raw: object) -> dict[str, Any] | None`

- [ ] **Step 1: Write failing definition and lease lifecycle tests**

```python
def test_definition_is_write_once_and_idempotent(tmp_path):
    service = RoleService(MemoryTransport(), tmp_path)
    first = service.define("demo", "reviewer", "exclusive", 3600, "Review work")
    same = service.define("demo", "reviewer", "exclusive", 3600, "Review work")
    conflict = service.define("demo", "reviewer", "shared", 3600, "Review work")
    assert first.state is State.DATA
    assert same.state is State.DATA
    assert conflict.state is State.UNKNOWN


def test_claim_refresh_release_are_append_only(tmp_path):
    transport = MemoryTransport()
    service = RoleService(transport, tmp_path)
    service.define("demo", "reviewer", "exclusive", 3600, "Review work")
    assert service.claim(
        "demo", "reviewer", "alice", now="2026-08-14T10:00:00Z",
        event_id=UUID_1, session_nonce="session-a",
    ).state is State.DATA
    assert service.claim(
        "demo", "reviewer", "alice", now="2026-08-14T10:15:00Z",
        event_id=UUID_2, session_nonce="session-a",
    ).state is State.DATA
    assert service.release(
        "demo", "reviewer", "alice", now="2026-08-14T10:20:00Z",
        event_id=UUID_3, session_nonce="session-a",
    ).state is State.DATA
    assert len([p for p in transport.files if "/history/" in p]) == 3
    assert service.status(
        "demo", "reviewer", now="2026-08-14T10:21:00Z"
    ).state is State.CLEAR
```

- [ ] **Step 2: Run the focused tests and verify RED**

Run: `pytest -q skills/fulcra-workspaces/scripts/tests/test_roles.py`

Expected: collection fails because `fulcra_workspaces.roles` does not exist.

- [ ] **Step 3: Implement immutable definitions, append-only lease events, and verified projections**

Use schemas `fulcra.workspaces-role.v1`, `fulcra.workspaces-role-lease.v1`, and
`fulcra.workspaces-role-lease-latest.v1`. Validate every workspace, role, and
identity with the existing Workspaces name grammar. Write an immutable event,
read it back, then write a projection containing `ptr` and SHA-256. A failed
projection returns `DURABLE_ONLY` with the immutable event pointer.

Status must:

```python
names, listing_state = transport.list_dir(
    f"team/{workspace}/roles/{role}/leases"
)
if listing_state != "ok" or names is None or len(names) > self.max_holders:
    return Outcome(State.UNKNOWN, "role holder listing is unreadable or unbounded", exit_code=3)
```

It verifies every identity projection and event. Fresh `held` events become
holders; `released` or expired events do not. Return `CLEAR` with
`status="VACANT"`, or `DATA` with `HELD`/`CONTESTED` and sorted holders.

- [ ] **Step 4: Add and verify collision, takeover, shared, corruption, and bound tests**

Cover these exact behaviors:

```python
assert foreign_fresh_claim.state is State.UNKNOWN
assert explicit_takeover.state is State.DATA
assert stale_takeover.state is State.DATA
assert exclusive_two_holder_status.data["status"] == "CONTESTED"
assert shared_two_holder_status.data["status"] == "HELD"
assert malformed_projection.state is State.UNKNOWN
assert oversized_listing.state is State.UNKNOWN
```

Run: `pytest -q skills/fulcra-workspaces/scripts/tests/test_roles.py`

Expected: all role tests pass.

- [ ] **Step 5: Commit the role service**

```bash
git add skills/fulcra-workspaces/scripts/fulcra_workspaces/roles.py \
  skills/fulcra-workspaces/scripts/tests/test_roles.py
git commit -m "feat: add portable Workspaces role leases"
```

### Task 2: Role-Bound Continuity And Ordered Handoff

**Files:**
- Modify: `skills/fulcra-workspaces/scripts/fulcra_workspaces/continuity.py`
- Create: `skills/fulcra-workspaces/scripts/fulcra_workspaces/handoff.py`
- Modify: `skills/fulcra-workspaces/scripts/tests/test_continuity.py`
- Create: `skills/fulcra-workspaces/scripts/tests/test_handoff.py`

**Interfaces:**
- Changes: `ContinuityService.checkpoint(workspace: str, identity: str, snapshot: dict[str, Any], *, checkpoint_id: str | None = None, timestamp: str | None = None, role: str | None = None) -> Outcome`
- Produces: `ContinuityService.resume_role(workspace: str, role: str, *, now: str, max_age_seconds: int, max_bytes: int) -> Outcome`
- Produces: `RoleHandoffService(roles: RoleService, continuity: ContinuityService)`
- Produces: `handoff(workspace: str, role: str, identity: str, snapshot: dict[str, Any], *, now: str, checkpoint_id: str | None = None, release_event_id: str | None = None, session_nonce: str | None = None) -> Outcome`

- [ ] **Step 1: Write failing role checkpoint and resume tests**

```python
def test_role_checkpoint_projects_one_bounded_resume_pointer():
    outcome = service.checkpoint(
        "demo", "alice", SNAPSHOT, role="reviewer",
        checkpoint_id=UUID_1, timestamp="2026-08-14T10:00:00Z",
    )
    assert outcome.state is State.DATA
    resumed = service.resume_role(
        "demo", "reviewer", now="2026-08-14T10:30:00Z",
        max_age_seconds=3600, max_bytes=10_000,
    )
    assert resumed.data["checkpoint"]["role"] == "reviewer"
    assert resumed.data["checkpoint"]["identity"] == "alice"
```

- [ ] **Step 2: Run continuity tests and verify RED**

Run: `pytest -q skills/fulcra-workspaces/scripts/tests/test_continuity.py`

Expected: failure because `checkpoint` has no `role` parameter and
`resume_role` does not exist.

- [ ] **Step 3: Implement optional role binding and verified role projection**

Add optional `role` to the checkpoint document and validate it when present.
After the immutable checkpoint and member projection verify, write:

```json
{"schema":"fulcra.workspaces-role-continuity-latest.v1",
 "workspace":"demo","role":"reviewer","identity":"alice",
 "timestamp":"2026-08-14T10:00:00Z","ptr":"team/demo/member/alice/continuity/checkpoint/<id>.json",
 "sha256":"<checkpoint digest>"}
```

`resume_role` reads that projection and selected checkpoint only, then verifies
workspace, role, identity, prefix, freshness, size, schema, and digest.

- [ ] **Step 4: Write failing handoff-order tests**

```python
def test_handoff_checkpoints_before_release():
    outcome = handoffs.handoff(
        "demo", "reviewer", "alice", SNAPSHOT,
        now="2026-08-14T10:30:00Z", checkpoint_id=UUID_1,
        release_event_id=UUID_2, session_nonce="session-a",
    )
    assert outcome.state is State.DATA
    assert transport.writes.index(role_continuity_ptr) < transport.writes.index(release_ptr)


def test_handoff_does_not_release_when_checkpoint_projection_fails():
    transport.fail_path = role_continuity_ptr
    outcome = handoffs.handoff(
        "demo", "reviewer", "alice", SNAPSHOT,
        now="2026-08-14T10:30:00Z", checkpoint_id=UUID_1,
        release_event_id=UUID_2, session_nonce="session-a",
    )
    assert outcome.state is State.DURABLE_ONLY
    assert not any('"state":"released"' in body for body in transport.files.values())
```

- [ ] **Step 5: Implement `RoleHandoffService` and run both suites**

Checkpoint first. Call `roles.release` only when checkpoint returns `DATA`.
When release fails, return `DURABLE_ONLY` with the checkpoint pointer and the
release outcome message; never erase or replace the checkpoint.

Run: `pytest -q skills/fulcra-workspaces/scripts/tests/test_continuity.py skills/fulcra-workspaces/scripts/tests/test_handoff.py`

Expected: all continuity and handoff tests pass.

- [ ] **Step 6: Commit continuity and handoff**

```bash
git add skills/fulcra-workspaces/scripts/fulcra_workspaces/continuity.py \
  skills/fulcra-workspaces/scripts/fulcra_workspaces/handoff.py \
  skills/fulcra-workspaces/scripts/tests/test_continuity.py \
  skills/fulcra-workspaces/scripts/tests/test_handoff.py
git commit -m "feat: add role continuity handoff"
```

### Task 3: CLI And End-To-End Demo

**Files:**
- Modify: `skills/fulcra-workspaces/scripts/fulcra_workspaces/cli.py`
- Modify: `skills/fulcra-workspaces/scripts/tests/test_cli.py`
- Modify: `skills/fulcra-workspaces/scripts/tests/test_acceptance_pair.py`

**Interfaces:**
- Produces CLI commands `role-define`, `role-claim`, `role-release`,
  `role-status`, `role-handoff`, and `role-resume`.
- Changes `checkpoint` to accept optional `--role`.

- [ ] **Step 1: Extend the CLI surface test and verify RED**

```python
for command in (
    "role-define", "role-claim", "role-release", "role-status",
    "role-handoff", "role-resume",
):
    assert command in result.stdout
```

Run: `pytest -q skills/fulcra-workspaces/scripts/tests/test_cli.py`

Expected: failure because the new commands are absent.

- [ ] **Step 2: Add parsers and dispatch to the role services**

Use `state_dir` for nonce persistence. All mutating role commands require the
verified Workspaces authority, even though they write Store state only, so the
portable workspace cannot silently split from its account coordination plane.
`role-status` and `role-resume` accept `--now` for deterministic tests.

- [ ] **Step 3: Extend the pair acceptance test and verify RED then GREEN**

After member join and before message delivery:

```python
roles = RoleService(account, tmp_path / "roles")
assert roles.define("demo", "reviewer", "exclusive", 3600, "Review plans").state is State.DATA
assert roles.claim(
    "demo", "reviewer", "alice", now="2026-08-14T10:02:00Z",
    event_id=UUID_6, session_nonce="alice-session",
).state is State.DATA
assert handoffs.handoff(
    "demo", "reviewer", "alice", snapshot,
    now="2026-08-14T10:16:00Z", checkpoint_id=UUID_7,
    release_event_id=UUID_8, session_nonce="alice-session",
).state is State.DATA
assert roles.claim(
    "demo", "reviewer", "bob", now="2026-08-14T10:17:00Z",
    event_id=UUID_9, session_nonce="bob-session",
).state is State.DATA
assert continuity.resume_role(
    "demo", "reviewer", now="2026-08-14T10:20:00Z",
    max_age_seconds=3600, max_bytes=10_000,
).data["checkpoint"]["identity"] == "alice"
```

Run: `pytest -q skills/fulcra-workspaces/scripts/tests/test_acceptance_pair.py`

Expected: the complete two-agent flow passes.

- [ ] **Step 4: Commit the CLI and demo**

```bash
git add skills/fulcra-workspaces/scripts/fulcra_workspaces/cli.py \
  skills/fulcra-workspaces/scripts/tests/test_cli.py \
  skills/fulcra-workspaces/scripts/tests/test_acceptance_pair.py
git commit -m "test: demonstrate portable role handoff"
```

### Task 4: Public Contract And Full Verification

**Files:**
- Modify: `skills/fulcra-workspaces/SKILL.md`
- Modify: `skills/fulcra-workspaces/references/coordination-protocol.md`
- Modify: `skills/fulcra-workspaces/references/fulcra-workspaces-cli.md`
- Modify: `skills/fulcra-workspaces/references/acceptance-demo.md`
- Modify: `skills/fulcra-workspaces/references/coord-alignment.json`
- Modify: `skills/fulcra-workspaces/scripts/tests/test_docs_contract.py`

**Interfaces:**
- Produces a self-contained Workspaces explanation of definitions, leases,
  status, collision limits, handoff, resume, and the advanced Coord boundary.

- [ ] **Step 1: Add failing documentation contract assertions**

```python
for phrase in (
    "role-define", "role-claim", "role-status", "role-handoff", "role-resume",
    "HELD", "VACANT", "CONTESTED", "checkpoint before releasing",
):
    assert phrase in public_docs
assert "portable-role-leases" in alignment
assert "role-continuity-handoff" in alignment
```

Run: `pytest -q skills/fulcra-workspaces/scripts/tests/test_docs_contract.py`

Expected: failure on the newly required role contract.

- [ ] **Step 2: Update the skill and references**

Make roles a core section before Advanced Coordination. State that normal
queue reads never scan role leases, status is explicit and bounded, different
identities racing an exclusive claim can only be detected as `CONTESTED`, and
same-identity live takeover requires `--takeover`. Revise Advanced Coordination
to list escalation and role-based routing, not basic role leases, as Coord-only.

- [ ] **Step 3: Run focused and full verification**

```bash
pytest -q skills/fulcra-workspaces/scripts/tests
python -m compileall -q skills/fulcra-workspaces/scripts
git diff --check
```

Expected: every test passes, compile exits 0, and diff check is clean.

- [ ] **Step 4: Commit the public contract**

```bash
git add skills/fulcra-workspaces/SKILL.md \
  skills/fulcra-workspaces/references/coordination-protocol.md \
  skills/fulcra-workspaces/references/fulcra-workspaces-cli.md \
  skills/fulcra-workspaces/references/acceptance-demo.md \
  skills/fulcra-workspaces/references/coord-alignment.json \
  skills/fulcra-workspaces/scripts/tests/test_docs_contract.py
git commit -m "docs: make portable roles visible in Workspaces"
```

- [ ] **Step 5: Request exact-head review and publish the stacked PR**

Push `codex/workspaces-portable-roles`, open a PR against `main` explaining
that it stacks on Workspaces protocol PR #175, then send Fabio a Bus review
request containing the PR URL and exact head SHA. Do not create or alter a
tick. Record Fabio's verdict against that exact SHA and address any requested
changes before reporting the PR green.
