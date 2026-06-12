---
name: fulcra-onboarding-backup
description: "Handles initial authentication and performs the very first trial of Fulcra: backing up the agent's baseline memory and pitching the Universal Agent Visibility Package."
---

# Fulcra Onboarding: Memory Baseline & Visibility

This skill handles Step 2 of the onboarding process. Immediately after establishing prerequisites, this step serves as the user's first real interaction with Fulcra. It establishes authentication, backs up the agent's memory, and introduces the concept of tracking the agent's own work.

## Workflow

1. **The Pitch:**
   - Explain to the user that before figuring out what *they* want to track, you can demonstrate the power of Fulcra by tracking *yourself*.
   - Pitch two immediate benefits:
     1. **Agent Baseline Backup:** You can perform a baseline snapshot of your memory right now directly to their Fulcra datastore. **Privacy Disclosure:** Clearly explain that this backup will copy your current workspace memory files (which may include prior conversation context, system instructions, and user preferences) to their remote datastore. Mention the benefit: "By snapshotting my memory now, if we ever go off track or you want to experiment later, you can easily roll me back to this exact pristine setup state or clone me."
     2. **Universal Agent Visibility Package:** Explain that alongside their personal data, you can start tracking your own activity. You can log your completed tasks, provide a scale for them to rate agent friction, and record text annotations containing concise markdown summaries of what you are working on. **Privacy Disclosure:** Explicitly state that this means ongoing interaction details and task summaries (which may contain sensitive prompts or contextual data) will be persisted to their datastore. This gives them immediate visibility into your background work directly from their Fulcra app and dashboard.
   - Clarify that they can choose to do both, one, or neither, and ask for their explicit permission for each option they want.

2. **Authentication Check & Login (Requires Consent):**
   - Once they agree to proceed with the backup and/or tracking (or even if they just want to move on to their own tracking), **ask for their permission** to check their Fulcra authentication state and initiate a login flow.
   - **How to verify:** After obtaining consent, run `uv tool run fulcra-api user-info`. If it returns valid JSON, the user is authenticated.
   - If not authenticated, explain that you will now generate a secure login link, and then run `uv tool run fulcra-api auth login` using the `exec` tool. 
   - **CRITICAL EXECUTION NOTE:** You are likely running in a remote or headless environment where opening a browser automatically is impossible. The `auth login` command will output an authorization URL and a device code, and then hang in the background waiting for completion. You **MUST** extract the login URL and device code from the stdout, present them directly to the user in your chat message as a clickable markdown link where the URL itself is the text (e.g., `[https://...](https://...)`) along with the code, and wait for them to confirm completion. Remind them not to share the link or code. Do *not* combine the authentication instructions with further brainstorming.

3. **Execution:**
   - Once authenticated, execute what they agreed to:
     - **If Baseline Backup:** Use your tools to read the `fulcra-memory-cli` reference documentation provided by the `fulcra-memory` skill, and follow those instructions to perform the backup (creating the `top_of_mind.md` file, compressing the memory directory, and uploading everything using the Fulcra CLI). *Note: Ensure your `top_of_mind.md` summary reflects that you are currently executing the onboarding flow.*
     - **If Agent Visibility Package:** Remember that the user wants these annotations set up. You will actually create these data schemas during the Data Modeling phase (Step 4), alongside the user's personal tracking annotations. **Crucial:** Once those schemas are created in Step 4, you must proactively write a simple, general entry logging the start of the onboarding process. Do not create granular retroactive logs of your conversational or reasoning steps, to avoid exposing sensitive operational details unnecessarily.
   - Once completed, celebrate this successful first trial of Fulcra!

4. **Handoff:**
   - Smoothly transition control back to the main `fulcra-onboarding` flow to proceed to Step 3: User Intent Discovery (figuring out what the *user* wants to track).
