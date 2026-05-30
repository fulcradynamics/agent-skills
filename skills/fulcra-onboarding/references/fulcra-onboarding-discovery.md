---
name: fulcra-onboarding-discovery
description: "Handles the initial discovery and authentication phase for new Fulcra users. Guides the user through login, uncovers their core intent, and suggests concrete use cases."
---

# Fulcra Onboarding: Discovery

**Tone Reminder:** Keep the energy high! Use emojis when suggesting ideas, and maintain a conversational, exciting vibe that hints at the vast possibilities of what they can build.

This skill handles the first phase of the Fulcra onboarding process (Step 1). Its primary goals are to ensure the user is authenticated and to rapidly identify how Fulcra can be most useful to them right now.

## Workflow

1. **Intent Discovery (PRE-AUTH):**
   - *Before* asking the user to authenticate or click any links, engage them to uncover their core intent. What brought them to Fulcra? What do they want to track, remember, or build?
   - **Crucial: Grounded Brainstorming:** Never ask open-ended questions like "What do you want to track?" without providing immediate inspiration. Always seed the conversation with 2-3 specific, tailored examples of what Fulcra can track (e.g., "We could build a tracker for your daily deep work hours, how many coffees you've had, or a log of the books you're reading."). If you have long-term memory or context about this specific user, use it to make these examples highly personalized. 
   - **Keep it frictionless:** Keep your messages extremely short and punchy. Assume the user has a low attention span. Do not send walls of text. 
   - **Quick Start Fallback:** If the user is still unsure or gives a vague answer (e.g., "just trying it out"), offer a brief "multiple choice" menu to spark ideas. Tailor these to the user if you have prior context, or use these default archetypes:
     - *Productivity:* Tracking daily mood or deep work sessions.
     - *Health:* Logging coffee intake, water, or sleep quality.
     - *Media:* Keeping a log of books read or movies watched.

2. **Authentication:**

   > **Correctness notes for every shell command in this section** (these
   > prevent the most common agent improvisations that break this flow):
   >
   > - **Always invoke the CLI as `uv tool run fulcra-api …`.** Don't use
   >   bare `fulcra-api` — your runtime's spawned subshells may not have it
   >   on PATH even when it's installed. Don't use `which fulcra-api` — it
   >   returns empty in that case and will mislead you into thinking the CLI
   >   isn't installed. `uv tool run fulcra-api` always works once `uv` is
   >   available (which the parent skill's pre-flight already ensured).
   > - **Run each shell snippet below as a single foreground string** in
   >   your standard terminal/exec tool. Do **not** route them through a
   >   separate background-process / spawn tool whose stdout you poll —
   >   stdout from a still-running child process is not reliably readable
   >   in most agent runtimes; that's why the login-launch line writes to
   >   a log file on disk for you to `cat`.

   - **Check current auth status (no consent needed — read-only):**

     ```bash
     uv tool run fulcra-api user-info
     ```

     If it exits 0 and returns JSON, the user is already authenticated → skip
     to step 3. If it fails (any non-zero exit), they are not authenticated;
     proceed to login.

   - **Start the login in the BACKGROUND and capture the URL + code from a
     log file on disk.** The device-flow command needs to keep polling auth0
     for the ~10 minutes the code is valid; a foreground `timeout` would
     terminate that polling and the user's sign-in would never reach disk.
     Reading from a log file on disk is reliable even while the producer
     process is still running, unlike trying to read stdout from a hanging
     pipe. Run **exactly** this single line:

     ```bash
     rm -f /tmp/fulcra-auth.log && nohup uv tool run fulcra-api auth login > /tmp/fulcra-auth.log 2>&1 & for i in $(seq 1 10); do grep -q 'activate?user_code=' /tmp/fulcra-auth.log 2>/dev/null && break; sleep 1; done; cat /tmp/fulcra-auth.log
     ```

     The output (from `cat /tmp/fulcra-auth.log`) contains two pieces you
     **MUST** relay to the user immediately and verbatim:
       - an **authorization URL** (e.g. `https://fulcra.us.auth0.com/activate?user_code=XXXX-YYYY`)
       - a **device code** (e.g. `XXXX-YYYY`)

     Present them using **exactly** this template. Render the URL wrapped in
     **backticks** (inline code) — do **NOT** format it as a markdown link
     `[label](url)`; the user must see the literal URL string so they can
     verify the code matches and (if needed) copy it. (Note for context: the
     URL already includes the device code as a query parameter, so the auth0
     page pre-fills it — the user just clicks Confirm and signs in.)

     > 🔐 Open this URL in your browser to sign in or create your Fulcra
     > account:
     >
     > `https://fulcra.us.auth0.com/activate?user_code=XXXX-YYYY`
     >
     > Confirm the code on that page matches: **XXXX-YYYY**
     >
     > Reply "done" when you've finished signing in.

     The `uv tool run fulcra-api auth login` process started above is
     **STILL RUNNING in the background**, polling auth0 for the user to
     complete the flow. **Do NOT kill it. Do NOT start another one.** It will
     write credentials to disk and exit on its own when the user finishes.

     **Do NOT preemptively run `user-info` while waiting** — it will return
     401 until the user actually completes the browser flow, and a premature
     check followed by "401 means failure, let me restart" reasoning will
     invalidate the user's current code. Wait for the user's explicit "done".

     **DO NOT** run a foreground `uv tool run fulcra-api auth login` (with or
     without `timeout`). The bare foreground command blocks indefinitely; a
     `timeout`-wrapped one returns the URL but also terminates the polling so
     the user's eventual sign-in is never received.

   - **When the user replies "done", verify the login completed:**

     ```bash
     uv tool run fulcra-api user-info
     ```

     If it returns 401, the background poll hasn't received the token yet —
     wait 3 seconds and retry `user-info` (up to 3 times). **Do NOT start a
     new `auth login`** — there is already one running in the background.
     Starting a new one creates a new code and invalidates the user's
     current sign-in. If still 401 after 3 retries, ask the user to confirm
     they clicked Confirm on the device-code page AND signed in to Fulcra.

   - **Security note:** the authorization URL and device code grant access
     to the user's Fulcra account. In a public or group channel, warn the
     user about the sensitivity and advise them to treat the link as a
     secret (don't paste it into shared chats, don't share it with others).

3. **Proactive Suggestions:**
   - Suggest simple, concrete examples of how they could use Fulcra (e.g., specific Annotations to track).
   - Tailor these suggestions using your existing memory and knowledge of the user.
   - Keep the pace brisk to reach the "wow" factor quickly.

## Handoff

Once the user is authenticated and you have clearly identified 2-3 specific custom data types or streams (Annotations) they want to track, hand control back to the main `fulcra-onboarding` flow to proceed with Data Modeling.
