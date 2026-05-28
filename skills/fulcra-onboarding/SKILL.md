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
- **Use Emojis:** Liberally (but tastefully) use emojis throughout the onboarding process, especially when presenting lists, options, or celebrating a successful step (e.g., "Would you like to track ☕ Coffee, 📚 Books, or 🏃 Fitness?").
- **Maintain Momentum:** Keep the user moving forward. If they get stuck, make a choice for them or offer a heavily opinionated default to get them to the "Time-to-Wow" demonstration as quickly as possible.

## Workflow

1. **Pre-flight Check:**
   - Read and execute the instructions in `references/fulcra-onboarding-prerequisites.md` to verify and install `uv` if necessary, asking the user for confirmation before installation. This must pass before proceeding.

2. **Discovery:**
   - Read and execute the instructions in `references/fulcra-onboarding-discovery.md` to handle user authentication, uncover their core intent, and suggest concrete use cases. Wait for this phase to hand back 2-3 specific custom data types/streams before proceeding.

3. **Data Modeling:**
   - Translate the user's intent into 2-3 specific custom data types/streams (Annotations).
   - Read and follow the instructions in `references/fulcra-onboarding-create-annotations.md` to define and create these schemas.
   - **Crucial Memory Step:** When you create these annotations, explicitly remember the returned `ANNOTATION_ID` and the exact `data_type` for each one. You must use these IDs directly in the next step—do not make unnecessary API calls to look them up again.

4. **Record First Data:**
   - Pick one of the newly created annotations and ask the user a direct question to get their first piece of data (e.g., if you created a "coffee consumed" annotation, ask "How many coffees have you had today?").
   - Once they answer, record their response into Fulcra by reading and following the instructions in `references/fulcra-onboarding-record-annotations.md`.

5. **Time-to-Wow (The Demonstration):**
   - Read and execute the instructions in `references/fulcra-onboarding-demonstration.md` to retrieve the recorded data, ask the user for a preferred aesthetic, and generate a custom themed HTML dashboard to display directly in the chat.

6. **Handoff & Next Steps:**
   - Read and execute the instructions in `references/fulcra-onboarding-handoff.md` to cleanly present the final steps (downloading the app, iterating on the dashboard, tracking more data) without overwhelming the user.
