---
name: fulcra-onboarding
description: "Guides a new user or agent through the initial setup, configuration, and capabilities of the Fulcra environment."
homepage: "https://github.com/fulcradynamics/agent-skills"
license: "MIT"
user-invocable: true
metadata: { "openclaw": { "emoji": "🌱" } }
---

# Fulcra Onboarding

Primary onboarding flow for new users connecting to the Fulcra environment. Fulcra is a universal data and memory backend for agents that securely stores personal context and custom data streams.

## General Guidelines

- **Tone & Vibe (The "Wow" Factor):** Fulcra unlocks massive potential because it acts as a universal memory and data backend for agents. Your tone should reflect this excitement and vast possibility. Be engaging, conversational, and fun.
- **Use Emojis:** Liberally (but tastefully) use emojis throughout the onboarding process, especially when presenting lists, options, or celebrating a successful step.
- **Maintain Momentum:** Keep the user moving forward. If they get stuck, make a choice for them or offer a heavily opinionated default to get them to the "Time-to-Wow" demonstration as quickly as possible.

## Workflow

1. **Pre-flight Check:**
   - Read and execute the instructions in `references/fulcra-onboarding-prerequisites.md` to verify and install `uv` if necessary, asking the user for confirmation before installation. This must pass before proceeding.

2. **Memory Baseline & Agent Visibility:**
   - Read and execute the instructions in `references/fulcra-onboarding-backup.md`. This step handles authentication, introduces the power of Fulcra by pitching a baseline agent memory backup, and offers to set up the Universal Agent Visibility Package. This serves as their very first trial of Fulcra's capabilities.

3. **User Intent Discovery:**
   - Read and execute the instructions in `references/fulcra-onboarding-discovery.md` to uncover their core tracking intent and suggest concrete "wow" factor use cases. Wait for this phase to hand back 2-3 specific custom data types/streams before proceeding.

4. **Data Modeling & Continuous Agent Tracking:**
   - Translate the user's intent into 2-3 specific custom data types/streams (Annotations).
   - Read and follow the instructions in `references/fulcra-onboarding-create-annotations.md` to define and create these schemas.
   - **If the user agreed to the Agent Visibility Package in Step 2:** You must create those specific schemas (Tasks Completed, Agent Friction, Current Agent Work) right now alongside the user's personal schemas. **Crucially:** From this point forward through the end of the onboarding flow, you must actively record your own high-level milestones into these agent-specific annotations so that the final dashboard is populated with a timeline of your work. Ensure you do not log sensitive reasoning or user prompts without explicit need.
   - **Crucial Memory Step:** When you create these annotations, explicitly remember the returned `ANNOTATION_ID` and the exact `data_type` for each one. You must use these IDs directly in the next step—do not make unnecessary API calls to look them up again.

   - **Continuous Agent Logging Check:** If you are tracking the Agent Visibility Package, ensure you are actively recording basic background data points (e.g., "Created user annotations", "Awaiting user input for first record") into your agent-specific annotations as the flow progresses.

5. **Record First User Data:**
   - Pick one of the user's newly created personal annotations and ask a direct question to get their first piece of data (e.g., if you created a "coffee consumed" annotation, ask "How many coffees have you had today?").
   - Once they answer, record their response into Fulcra by reading and following the instructions in `references/fulcra-onboarding-record-annotations.md`.

6. **Time-to-Wow (The Demonstration):**
   - Read and execute the instructions in `references/fulcra-onboarding-demonstration.md` to retrieve the recorded data. **CRITICAL:** You must stop the conversation to ask the user for a preferred theme *before* generating the HTML dashboard. Do not automatically generate the dashboard until they have explicitly answered with their theme choice.

7. **Agent Coordination:**
   - Read and execute the instructions in `references/fulcra-onboarding-coordination.md` to introduce the concept of coordinating multiple agents through Fulcra.

8. **Handoff & Next Steps:**
   - Read and execute the instructions in `references/fulcra-onboarding-handoff.md` to cleanly present the final steps (downloading the app, iterating on the dashboard, tracking more data) without overwhelming the user.
