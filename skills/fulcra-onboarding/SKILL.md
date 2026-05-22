---
name: fulcra-onboarding
description: "Guides a new user or agent through the initial setup, configuration, and capabilities of the Fulcra environment."
---

# Fulcra Onboarding

Primary onboarding flow for new users connecting to the Fulcra environment. Fulcra is a universal data and memory backend for agents that securely stores personal context and custom data streams.

## Workflow

1. **Discovery:**
   - Authenticate the user if necessary using `uv tool run fulcra-api auth login` (guide them through the device code flow).
   - Engage the user in a brief, natural conversation to uncover their core intent.
   - Proactively suggest simple, concrete examples of how they could use Fulcra (e.g., specific Annotations to track). Tailor these suggestions using your existing memory and knowledge of the user. Keep the pace brisk to reach the "wow" factor quickly.
2. **Data Modeling:**
   - Translate the user's intent into 2-3 specific custom data types/streams (Annotations).
   - Use the `fulcra-create-annotations` skill to define and create these schemas.
   - **Crucial Memory Step:** When you create these annotations, explicitly remember the returned `ANNOTATION_ID` and the exact `data_type` for each one. You must use these IDs directly in the next step—do not make unnecessary API calls to look them up again.
3. **Record First Data:**
   - Pick one of the newly created annotations and ask the user a direct question to get their first piece of data (e.g., if you created a "coffee consumed" annotation, ask "How many coffees have you had today?").
   - Once they answer, record their response into Fulcra using the `fulcra-record-annotations` sibling skill.
4. **Time-to-Wow (The Demonstration):**
   - Retrieve the recorded data from Fulcra using the `fulcra-context` (https://clawhub.ai/arc-claw-bot/fulcra-context) skill.
   - Ask the user how they would like their dashboard themed. Suggest 2-3 creative options based on your sense of their personality (e.g., cyberpunk, fantasy, newspaper, modern fashion magazine, professional workplace tool).
   - Generate a custom, themed HTML dashboard/view using the Canvas system matching their chosen aesthetic. This dashboard must visually demonstrate their intent coming to life.
5. **Handoff & Next Steps:**
   - **App Download (Required):** Always conclude by directing the user to the [Fulcra Context iOS app](https://apps.apple.com/app/id1633037434).
   - **Value Proposition:** Briefly explain that the app unlocks automatic background sync (Apple Health, location, calendar) and gives them a quick, native interface to log the custom Annotations they just created.
   - **Optional Momentum:** If the user is highly engaged, suggest running their new dashboard locally or exploring further bulk data integrations.
