---
name: fulcra-prefs
description: "Load the user's cross-platform preferences at session start and capture new ones the moment they're expressed. Trigger when the user says 'remember that I…', 'from now on…', 'I always/never want…', corrects a preference you applied, or confirms a pattern you noticed — and at the start of any session where user preferences would change your behavior. Alpha."
homepage: "https://github.com/ashfulcra/fulcra-tools/tree/main/packages/fulcra-prefs"
license: "MIT"
user-invocable: true
metadata: { "openclaw": { "emoji": "⚙️" } }
---

# fulcra-prefs

The user's preferences and facts live in their Fulcra account as typed,
decaying signals, compiled into per-platform preference documents. Your job:
LOAD them at session start, APPLY them, and CAPTURE new ones as they're expressed.

> **Alpha status:** schema may change; expect a re-onboard across early versions.

## Load the preferences now

Run this immediately — before anything else:

- **CLI-capable agent:** `fulcra-prefs inject --platform <your-platform>`
  → prepend output to your working context. Empty output = no prefs yet; continue silently.
- **HTTP-only agent:** follow `references/fulcra-prefs-tier2-http.md` (steps 1–2).
- **MCP read-only agent:** preference read/write of compiled docs is not available
  via MCP today. Tell the user to run onboarding from a CLI-capable agent.

## Pick your path

1. **You can run shell commands** → use the CLI. Setup once:
   `uv tool install fulcra-prefs` (and `fulcra auth login` if not authed).
   - Load: `fulcra-prefs inject --platform <your-platform>` (done above).
   - Capture: `fulcra-prefs capture --key <ns.key> --value '<json>'
     --strength <-1..1> --platform <your-platform>` (see
     `references/fulcra-prefs-capture.md` for when and what to capture).
   - Refresh: `fulcra-prefs compile` (run after captures; cheap).
2. **You can make HTTP requests but not run commands** → follow
   `references/fulcra-prefs-tier2-http.md` (device-flow auth + direct API).
3. **You only have the Fulcra MCP** → read-only; no compiled-doc access.
   Direct the user to re-run onboarding from a CLI-capable agent.

## Capture

Capture is the continuous half of the loop. After loading prefs, watch the
conversation for signals and capture them — see `references/fulcra-prefs-capture.md`
for the full heuristics, consent rules, and key conventions.

Quick triggers: explicit asks ("remember that I…", "from now on…", "I always/never
want…"), corrections of your behavior ("no, I prefer X"), or patterns you observed
AND the user confirmed.

## Onboarding a new user

If `inject`/`get` reports not-onboarded: run `fulcra-prefs onboard` (requires
`fulcra auth login` first — account auto-creates on first login). For a full
guided platform onboarding, hand off to the fulcra-onboarding skill:
https://github.com/fulcradynamics/agent-skills/blob/main/skills/fulcra-onboarding/SKILL.md

## Rules

- NEVER print or store the user's access token.
- Respect scopes: per-platform overrides beat global; negative weight =
  aversion (don't suggest what they dislike).
- Capture is consent-adjacent: only capture what the user said or confirmed —
  see the capture reference for the heuristics.
