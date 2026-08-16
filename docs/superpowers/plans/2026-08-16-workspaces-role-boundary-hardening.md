# Workspaces Role Boundary Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make PR #176 explain the portable role minimum, preserve the advanced Coord boundary, and state current cross-skill compatibility honestly.

**Architecture:** Keep the existing role implementation unchanged. Strengthen the public skill and protocol around three invariants: a portable lease is coordination ownership rather than authorization or liveness, advanced policy stays outside Workspaces, and the current community role engine must not operate on the same role until a schema-alignment migration lands. Enforce those invariants with documentation contract tests.

**Tech Stack:** Markdown, Python 3, pytest, JSON documentation alignment stamp.

## Global Constraints

- Do not add role-addressed routing, presence, vacancy escalation, review policy, task policy, or forge behavior to Workspaces.
- Do not claim current wire compatibility with an existing `fulcra-agent-coordination` release whose role paths or event model differ.
- Keep File Store documents authoritative and human-readable; role operations remain explicit bounded control-plane reads.
- Do not change role command behavior or durable schemas in this hardening pass.
- Keep private machine, harness, model, identity, and team mappings out of the repository.

---

### Task 1: Lock The Public Boundary Into Contract Tests

**Files:**
- Modify: `skills/fulcra-workspaces/scripts/tests/test_docs_contract.py`

**Interfaces:**
- Consumes: `SKILL`, `PROTOCOL`, and `ALIGNMENT` documentation paths already defined by the test module.
- Produces: a contract test that fails unless the public docs distinguish portable ownership from authorization and warn against mixed role engines before alignment.

- [ ] **Step 1: Write the failing documentation contract test**

Add a test that reads `SKILL.md` and `coordination-protocol.md`, then asserts these concepts are present:

```python
def test_portable_roles_define_policy_and_compatibility_boundaries():
    skill = SKILL.read_text()
    protocol = PROTOCOL.read_text()
    public_contract = "\n".join((skill, protocol))

    assert "coordination ownership" in public_contract
    assert "not authorization" in public_contract
    assert "proof of process liveness" in public_contract
    assert "must not run" in public_contract
    assert "same workspace role" in public_contract
    assert "alignment migration" in public_contract
```

- [ ] **Step 2: Run the focused test and verify it fails**

Run:

```bash
pytest -q skills/fulcra-workspaces/scripts/tests/test_docs_contract.py::test_portable_roles_define_policy_and_compatibility_boundaries
```

Expected: failure because the approved boundary language exists only in the design spec, not the public skill or protocol.

- [ ] **Step 3: Commit the failing contract test**

```bash
git add skills/fulcra-workspaces/scripts/tests/test_docs_contract.py
git commit -m "test: lock portable role boundaries"
```

### Task 2: Clarify Portable And Advanced Role Responsibilities

**Files:**
- Modify: `skills/fulcra-workspaces/SKILL.md`
- Modify: `skills/fulcra-workspaces/references/coordination-protocol.md`
- Modify: `README.md`
- Test: `skills/fulcra-workspaces/scripts/tests/test_docs_contract.py`

**Interfaces:**
- Consumes: the approved `Boundary And Compatibility` section in `docs/superpowers/specs/2026-08-14-workspaces-portable-roles-design.md`.
- Produces: public guidance that explains why Workspaces has finite leases, what those leases do not prove, what remains advanced, and when two role engines may coexist.

- [ ] **Step 1: Add the minimal-role explanation to `SKILL.md`**

In `## Portable Roles`, explain that a finite lease exists only to validate current coordination ownership for checkpoint, handoff, and resume. State explicitly that it is not authorization, access control, user approval, presence, or proof of process liveness.

- [ ] **Step 2: Add the compatibility warning to the protocol**

Under `## Advanced Coordination Boundary`, describe the portable schema as the alignment target. State that existing advanced implementations with different role paths or event models must not operate their role engine on the same workspace role until an explicit alignment migration lands.

- [ ] **Step 3: Tighten the README summary**

Describe portable leases as bounded coordination ownership for handoff and resume, and point advanced presence, routing, and escalation to `fulcra-agent-coordination` without claiming immediate role-record interchangeability.

- [ ] **Step 4: Run the focused contract test**

Run:

```bash
pytest -q skills/fulcra-workspaces/scripts/tests/test_docs_contract.py::test_portable_roles_define_policy_and_compatibility_boundaries
```

Expected: pass.

- [ ] **Step 5: Run the full Workspaces suite and static checks**

Run:

```bash
pytest -q skills/fulcra-workspaces/scripts/tests
python3 -m compileall -q skills/fulcra-workspaces/scripts
python3 -m json.tool skills/fulcra-workspaces/references/coord-alignment.json
git diff --check
```

Expected: 83 tests pass, compileall exits zero, JSON prints successfully, and `git diff --check` is silent.

- [ ] **Step 6: Commit the public documentation changes**

```bash
git add README.md skills/fulcra-workspaces/SKILL.md skills/fulcra-workspaces/references/coordination-protocol.md
git commit -m "docs: define portable and advanced role boundaries"
```

### Task 3: Update The Pull Request And Re-run Exact-Head Review

**Files:**
- Modify: PR #176 description on GitHub.
- No repository file changes.

**Interfaces:**
- Consumes: verified commit SHA after Tasks 1 and 2.
- Produces: a PR description that records the reviewer-driven boundary hardening and an exact-head review request for Fabio.

- [ ] **Step 1: Push the branch to the PR head branch**

```bash
git push https://github.com/ashfulcra/agent-skills.git HEAD:codex/workspaces-portable-roles
```

- [ ] **Step 2: Update PR #176 validation and relationship notes**

Add a short `Relationship to fulcra-agent-coordination` section that distinguishes the portable minimum from advanced policy and discloses that current role schemas require an alignment migration before both engines may manage the same role.

- [ ] **Step 3: Request Fabio exact-head review**

Send the new SHA, changed files, test evidence, and two review questions: whether the portable minimum stays non-authoritative and whether the compatibility warning prevents mixed-engine corruption.

- [ ] **Step 4: Re-run verification if the reviewed head changes**

Do not treat a prior approval as applying to a different commit. Repeat the full Workspaces suite and exact-head review after any amendment.
