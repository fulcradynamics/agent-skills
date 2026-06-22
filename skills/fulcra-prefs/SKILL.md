---
name: fulcra-prefs
description: "Load the user's cross-platform preferences at session start and capture new ones the moment they're expressed. Trigger when the user says 'remember that I…', 'from now on…', 'I always/never want…', corrects a preference you applied, or confirms a pattern you noticed — and at the start of any session where user preferences would change your behavior."
homepage: "https://github.com/fulcradynamics/agent-skills/tree/main/skills/fulcra-prefs"
license: "MIT"
user-invocable: true
metadata: { "openclaw": { "emoji": "⚙️" } }
---

# fulcra-prefs

The user's preferences and facts live in their Fulcra account as typed, decaying signals. Your job is to **LOAD** them at session start, **APPLY** them, and **CAPTURE** new ones as they are expressed.

We use the base `fulcra-api` CLI and standard Fulcra Custom Annotations (specifically a `MomentAnnotation` named "User Preference") to manage this cross-platform preference system natively.

## Bootstrapping (First Time Setup)

If you have never set up the preference system before, you must create the schema.

1. Check if the schema exists:
   ```bash
   uv tool run fulcra-api catalog --user-only | jq '[.[] | select(.name == "User Preference")]'
   ```
2. If it does not exist, create it:
   ```bash
   uv tool run fulcra-api data-type create MomentAnnotation "User Preference" --description "Cross-platform user preferences and facts"
   ```
   **Capture the returned `"id"`** (e.g., `com.fulcradynamics.annotation.xyz`). You will need this ID for loading and capturing preferences.

## Load Preferences

Run this early in any session where you need context about the user's preferences:

1. Retrieve all recorded preferences using the schema ID:
   ```bash
   uv tool run fulcra-api get-records MomentAnnotation "10 years" | jq '[.[] | select(.source_id == "<USER_PREFERENCE_ID>")]'
   ```
2. The output will contain JSON payloads in the `data` field representing individual preference signals.
3. Review these signals and **synthesize** them into your working context. If there are conflicting signals for the same "key" (e.g., an older preference vs. a newer correction), always honor the most recent one.

## Capture Preferences

Capture creates durable records on the user's Fulcra timeline. Be conservative: capture what the user SAID or CONFIRMED, not silent inferences.

**When to Capture:**
- **Explicit asks:** "remember that I…", "from now on…", "I always/never want…"
- **Corrections:** "no, I prefer X"
- **Confirmed patterns:** A pattern you observed and the user confirmed when asked.

**DO NOT capture:**
- Unconfirmed inferences, one-off task context, credentials, health details the user didn't ask to store, or another person's preferences.

### How to Capture (Recording)

When capturing a preference, you must construct a single stringified JSON object for the `data` field that conforms to the `MomentAnnotation` spec. Because the spec expects a single `note` field, you must serialize your entire preference structure into a string and store it inside the `note` property. 

The inner serialized string should represent the preference logically (e.g., `key`, `value`, `scope`, `strength`).

Record the preference using the Fulcra Ingest API (injecting the token securely):

```bash
curl -i -X POST \
  -H "Authorization: Bearer $(uv tool run fulcra-api auth print-access-token)" \
  -H "Content-Type: application/json" \
  -d '{
    "metadata": {
      "data_type": "MomentAnnotation",
      "tags": [],
      "recorded_at": "<CURRENT_ISO_8601_UTC_TIMESTAMP>",
      "content_type": "application/json",
      "source": [
        "<USER_PREFERENCE_ID>"
      ]
    },
    "data": "{\"note\": \"{\\\"key\\\": \\\"comms.tone.concise\\\", \\\"value\\\": true, \\\"scope\\\": \\\"global\\\", \\\"strength\\\": 1.0}\"}"
  }' \
  https://api.fulcradynamics.com/ingest/v1/record
```

## Rules

- NEVER print or store the user's access token.
- Respect scopes: per-platform overrides beat global.
- Negative strength = aversion (don't suggest what they dislike; do not use `.not` keys).
- Capture is consent-adjacent: only capture what the user said or explicitly confirmed.
