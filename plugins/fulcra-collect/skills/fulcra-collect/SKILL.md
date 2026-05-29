---
name: fulcra-collect
description: "Create Fulcra annotation types and record consented user data through the Fulcra CLI. Use when a user wants an agent to collect structured personal context into Fulcra."
homepage: "https://github.com/fulcradynamics/agent-skills"
license: "MIT"
user-invocable: true
metadata:
  hermes:
    tags: [Fulcra, Data Collection, Annotations, Personal Context]
    related_skills: [fulcra-onboarding, fulcra-skills-dashboard]
required_environment_variables: []
---

# Fulcra Collect

Use this skill when the user wants to create structured Fulcra data streams and record new data points into those streams.

Fulcra is a personal context backend for agents. This skill should make data collection feel direct and useful while keeping consent, authentication, and privacy boundaries explicit.

## Rules

- Get user consent before reading from or writing to Fulcra.
- Never ask the user to paste access tokens, refresh tokens, credential files, or private records into chat.
- If authentication is needed, run the Fulcra CLI auth flow and give the user only the login URL and device code.
- Prefer `uv tool run fulcra-api` so the current CLI is fetched and isolated automatically.
- Store only the annotation IDs and data types needed for the current workflow in the conversation context.
- Do not invent annotation IDs. Use IDs returned by the Fulcra API or CLI.

## Preflight

Check that `uv` is available:

```bash
uv --version
```

If `uv` is missing, ask the user before installing it. Do not install tooling silently.

Check Fulcra CLI access:

```bash
uv tool run fulcra-api --help
```

If the user needs to authenticate, run:

```bash
uv tool run fulcra-api auth login
```

Share only the browser URL and device code. Do not expose token output.

## Create A Collection Stream

When the user describes something they want to track:

1. Ask one focused clarification only if the schema is genuinely ambiguous.
2. Choose a simple annotation name, description, and data type.
3. Create the annotation through Fulcra.
4. Save the returned annotation ID and data type in the working context.
5. Ask for the first value and record it immediately.

Prefer simple types first:

- Boolean: yes/no events, habits, symptoms, completed actions.
- Number: counts, duration, weight, dose amount, score.
- Text: notes, labels, short freeform observations.
- Scale: subjective ratings like mood, energy, pain, focus.

## Record Data

Before recording a value, restate what will be written in one sentence and ask for confirmation if the data is sensitive or high impact.

Use the Fulcra CLI command surface available on the host. If a direct annotation command is present, use it. If the CLI shape differs, inspect help first:

```bash
uv tool run fulcra-api --help
uv tool run fulcra-api annotations --help
```

For hosts that expose annotation helpers through Python, use a short script that shells out to `uv tool run fulcra-api` or imports the installed `fulcra-api` package. Keep token handling inside the CLI or SDK; do not print credentials.

## Verify The Write

After recording:

1. Query the relevant annotation or recent records.
2. Confirm the new value appears.
3. Report the result concisely, including the human-readable stream name and timestamp, not raw credential paths or token details.

## Handoff

When the first data point is verified, suggest one useful next step:

- create one more related stream,
- build a small dashboard,
- schedule recurring capture,
- or connect the data to an existing Fulcra analysis workflow.

Do not overwhelm the user with a long menu.
