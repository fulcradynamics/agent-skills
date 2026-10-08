---
name: build-and-host-a-web-app
description: "Build and iterate on Fulcra web apps through a required planning, generation, and evaluation harness, preserving requirements, decisions, and history."
homepage: "https://github.com/fulcradynamics/agent-skills"
license: "MIT"
user-invocable: true
metadata: { "openclaw": { "emoji": "🛠️" } }
---

# Build and Host a Web App

Build a working, maintainable Fulcra-backed web application through planned, generated, and evaluated milestones. Use when starting a custom web app or continuing one created with this skill. Deployment alone is not completion: preserve requirements, user decisions, evaluation evidence, and history so later changes can be integrated and checked against what already works.

The goal is an app the user can actually use, not something that only looks like their request. Evaluation is required and is often the most important part of the job: it establishes that the deployed experience works. Skipping or faking it does not finish the job; delivering broken functionality as working erodes the user's trust and interest.

## Required Harness Contract

- Read [harness-control-flow.md](references/harness-control-flow.md) before implementation. The harness is the development process, not an optional dashboard or a final setup step.
- **M1 — Working baseline and harness dashboard** is always the first milestone. Run scaffolding, baseline deployment, and dashboard integration through the harness; do not build features first and backfill events later.
- Execute each role with real tools. For simple work one agent may take the roles sequentially, but keep generation and evaluation separate: the Evaluator checks the spec and evidence rather than accepting the Generator's claims. Only the Nurse creates or repairs harness machinery.
- Every run event must include a non-empty `evidence` string describing what was actually done and observed so far. A completed `REVIEW` must report the successful evaluations actually performed, with commands or UI actions, the tested target, and observed results; intentions, a build alone, or "tests passed" are not sufficient. The Coordinator must reject a passing review without this evidence and leave the milestone incomplete.
- Before handing off M1, verify the deployed dashboard displays its actual run events and evaluation result. An empty dashboard, invented success records, or a deployed app without evaluation is not a completed milestone.
- For user-reported bugs or adjustments, update the spec and decisions, [insert a milestone after the last completed milestone](references/harness-control-flow.md#user-reported-bugs-and-adjustments) (e.g., `m2-1` after M2), and run the harness as usual.
- Continue all feature work and later changes through the same harness. If authentication, recording, evaluation, or deployment is blocked, preserve the blocker and escalate; do not silently skip the harness.

## Preferred Tone

This skill offers a fairly involved set of steps and so a tone that favors concise, simple language that does not include made-up technical jargon lends itself well to a lower-friction / easy-flowing user experience.

## Preferred Coding Style

Because this skill uses a harness approach, the preferred coding style is to avoid over-engineering, avoid overly-defensive code, and avoid writing an unnecessarily large number of tests so that milestones only require a reasonable amount of time to be attempted and maintained. The point is to add milestones and allow the project to evolve in a stable way. You'll still have the opportunity to author all the code you want, but use milestones as smaller lego bricks to build your empire.

## Overview

This skill helps users start a Fulcra-backed web application by cloning one of the official app templates. These templates provide:

- Complete sign-in and sign-up flow out of the box
- User authentication with Fulcra
- Ready-to-use structure for making authenticated API calls
- Placeholder strings designed to be customized for the user's specific app

The templates are the starting point; the harness makes the app reviewable and supports continued iteration against the stored plan, spec, decisions, and history.

## Template Options

Choose between two frontend frameworks:

1. **Svelte** (default) — Lightweight and beginner-friendly. Great for most projects.  
   https://github.com/fulcradynamics/app-template-svelte

2. **React** — Industry standard with extensive ecosystem and community resources.  
   https://github.com/fulcradynamics/app-template-react

## Workflow

### 1. Idea and Enhancement

Ask the user what they want to build.

To understand Fulcra's capabilities, read:

- **High-level overview**: https://github.com/kubla/fulcra-for-agents/blob/main/fulcra-for-agents.md
- **Platform capabilities**: https://docs.fulcradynamics.com/fulcra-platform/

These provide conceptual understanding of what Fulcra enables. Don't read the full REST API docs yet—those are for implementation, not planning.

Based on the user's idea, map it to Fulcra's capabilities to implement and enhance it:

- **User authentication** — Already built-in; enables user-specific features
- **Data persistence** — Store user history, progress, preferences via annotations
- **Multi-user interaction** — Leaderboards, sharing, social features across users
- **File storage** — User-uploaded content

Present a concise overall plan that includes the core idea including Fulcra-enabled enhancements. Include a Harness section: M1 establishes a verified baseline and populated owner dashboard, and later milestones build features through generation and evaluation. Record the retry/timeout configuration from the control-flow reference.

Get high-level approval from the user on this enhanced vision before proceeding.

### 2. Connect to Fulcra and Initialize Workspace

**Authentication**: Run `uvx fulcra-api auth login --get-auth-url` to get authentication URL and device code. Share the URL with the user to authenticate in their browser, then run `uvx fulcra-api auth login --device-code <code>` to complete authentication.

If the login command fails with a network error, inform the user that CLI authentication cannot be used in this environment and that MCP connector is an alternative option.

**Initialize workspace**: Upload the approved plan to `workspace/<project-name>/plan.md` and initialize the workspace structure (see [`references/workspace.md`](references/workspace.md)).

### 3. Interview for Spec

Ask only necessary clarifying questions one at a time to gather details needed for the spec and milestones. Keep questions concise and focused on what's needed to define milestones that fit the harness flow (see [`references/harness-control-flow.md`](references/harness-control-flow.md)).

As you go, note each specific decision the user makes — their actual choice, not a paraphrase.

Once you have enough detail, create the spec with milestone breakdown, then upload to the workspace: the spec to `spec.md` and the collected decisions to `decisions.md` (at the end, not after each question). Define M1's acceptance criteria using the [dashboard handoff gate](references/harness-dashboard-setup.md#evaluate-m1-before-handoff); app-specific features start at M2. Initialize `progress.md` with M1 pending. See [`references/workspace.md`](references/workspace.md).

### 4. Choose Template

Use Svelte unless the user prefers React or has already specified a preference.

### 5. Start the First Harness Run

Before cloning or writing app code, the Nurse bootstraps the minimal harness and its annotation data type using [harness-control-flow.md](references/harness-control-flow.md#setup). This is only the machinery needed to record and run M1, not an untracked dashboard implementation. Save the data type ID in `progress.md` and reuse it; do not create another in step 9.

Mint a unique `run_id`, perform the Nurse health-check, write and read back `RUN_START`, and have the Coordinator record `FIND_MILESTONE` selecting M1. Record `GENERATE` started before implementation. Follow the recording instructions in the control-flow reference; if recording fails, stop and repair or escalate rather than continuing untracked.

Steps 6–9 below are the implementation work **inside this run**, not prerequisites to starting the harness. Keep the default retry/timeout rules; if M1 needs more time, record an explicit configuration override in `plan.md` before continuing rather than silently ignoring the timeout.

### 6. Generate the Baseline

Clone the chosen template into a new directory named for their project:

```bash
git clone https://github.com/fulcradynamics/app-template-[react|svelte] <project-name>
cd <project-name>
rm -rf .git  # Remove template git history
git init     # Start fresh git history
```

Create `AGENTS.md` at the project root:

```markdown
# Agent Information

**Workspace**: `workspace/<project-name>/`  
**Skill**: build-and-host-a-web-app (fulcradynamics/agent-skills)

The Fulcra workspace is the primary source of truth. Read plan.md, spec.md,
decisions.md, progress.md, and relevant history before continuing. Load the
build-and-host-a-web-app skill and its harness-control-flow reference. All changes
must use the harness: select a milestone, generate, perform separate evaluation
with real tool evidence, then record the result and update workspace history.
Never skip the harness or infer completion from a deployment alone.
For a user-reported bug or adjustment, update the spec and decisions, insert a
milestone after the last completed one (e.g., m2-1 after M2), and run the harness.
```

Update placeholder strings in the login flow. Each template includes placeholder text (like "Your App Name", "Your App Description", etc.) that should be replaced with content from the spec.

### 7. Install, Configure, and Verify

Follow the template's `README.md` ("Getting Started"): `npm install`, `cp .env.example .env`, then review and configure the Auth0 and Fulcra API values as directed. Run `npm run dev` and confirm the app starts locally and the sign-in screen renders before deploying—this verifies a working authentication foundation.

### 8. Deploy Baseline

Deploy the customized, working template so the user has a live baseline before feature development. Apps are deployed to a Fulcra domain without a Vercel account: create the app's deploy project once, saving it in `progress.md`, then deploy with a fresh project token. Follow [`references/deploy.md`](references/deploy.md), which also covers falling back to the user's own Vercel account. Use the same deploy command for every later redeploy.

You may share this URL as an **in-progress baseline**, not a completed M1 handoff. Continue the same harness run with dashboard integration and evaluation before app-specific feature development.

### 9. Set Up Harness and Dashboard

Within M1, the Nurse sets up the dashboard as part of the harness machinery; the Generator handles baseline app code. Reuse the harness data type from step 5, add the environment variables (using `uvx fulcra-api user-info` to retrieve the owner's `"userid"`), create the backend-only server endpoints, integrate the dashboard components, and [redeploy](references/deploy.md#deploy). Keep role transitions explicit even when one agent performs both roles.

Follow [`references/harness-dashboard-setup.md`](references/harness-dashboard-setup.md) for commands, env vars, endpoints, component wiring, and acceptance checks. Both frameworks must pass the same gate; an untested React path is a blocker, not permission to omit the harness.

Record `GENERATE` completed only after the implementation work is done. The Evaluator then records `REVIEW` started and executes the dashboard handoff gate against the deployed app, including the Harness page and global `<OwnerNav />`, live run data, and owner-only access. This is where you establish that the user can actually use what you are handing over, not just view it. Store the tool evidence in the workspace; do not record `REVIEW` completed until its checks pass.

### 10. Close M1 and Continue Through the Harness

On a passing review, the Coordinator records `MARK_COMPLETE`, updates `progress.md` and milestone history with evidence, and records `RUN_COMPLETE`. The Nurse refreshes `overview.md`; verify that the dashboard now shows the real M1 result before presenting the completed baseline and dashboard to the user. On failure, leave M1 incomplete and follow the documented retry/escalation flow. Never manufacture a successful run to fill the dashboard.

For M2 onward, select the earliest incomplete milestone and execute the same [control flow](references/harness-control-flow.md) with a new run ID. Read the current requirements, decisions, and history, generate the change, then exercise the user's intended workflow against its acceptance criteria and check that previously working behavior still works. This evaluation is required for every milestone; recording success cannot substitute for doing it. Persist the actual result. User-requested changes update the recorded requirements before another run; roles cannot rewrite the spec merely to pass review. Resume this process after interruptions rather than switching to ad hoc coding.

Keep this harness implementation as simple as possible: the Preferred Coding Style intention applies to the harness too, so favor the smallest thing that works instead of an elaborate framework.

**Track progress** using the workspace pattern (see [`references/workspace.md`](references/workspace.md)) and write annotation records at each step (see tracking system instructions in harness-control-flow.md). The Coordinator updates progress.md and the dashboard shows live status.

## Key Points

- Keep setup minimal and straightforward
- The templates are designed to be customized—don't over-prescribe the structure
- A working starting point includes authentication, a populated harness dashboard, and verified M1 evidence
- The user's vision for their app drives what happens next
- Consult the Fulcra REST API docs when implementing app-specific features
