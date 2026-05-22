---
name: fulcra-onboarding
description: "Guides a new user or agent through the initial setup, configuration, and capabilities of the Fulcra environment."
---

# Fulcra Onboarding

Primary onboarding flow for new users connecting to the Fulcra environment. Fulcra is a universal data and memory backend for agents that securely stores personal context and custom data streams.

## Workflow

1. **Discovery:**
   - Authenticate the user if necessary using `uv tool run fulcra-api auth login` (guide them through the device code flow).
   - Have a brief, natural conversation to capture the user's core intent. Ask questions dynamically based on their responses. Keep it moving—the goal is to get to the "wow" factor quickly.
   - When asking the user for direction (e.g., what Annotations to create), always suggest simple, concrete examples of how Fulcra can be used. Use your knowledge and memory of the user to tailor these examples, if possible.
2. **Data Modeling:**
   - Translate their intent into 2-3 specific custom data types/streams (Annotations).
   - Use the `fulcra-create-annotations` skill to define and create these schemas.
3. **First Ingestion:**
   - Always ask the user for input or confirmation to inform the value that's recorded. For example, if recording a numeric "drank coffee" annotation, ask "how many coffees have you had today?" and record the value from their answer.
   - Record this data using the appropriate Fulcra tools or skills.
4. **Time-to-Wow (The Demonstration):**
   - Retrieve the recorded data from Fulcra using the `fulcra-context` (https://clawhub.ai/arc-claw-bot/fulcra-context) skill.
   - Ask the user how they would like their dashboard themed. Suggest 2-3 creative options based on your sense of their personality (e.g., cyberpunk, fantasy, newspaper, modern fashion magazine, professional workplace tool).
   - Generate a custom, themed HTML dashboard/view using the Canvas system matching their chosen aesthetic. This dashboard must visually demonstrate their intent coming to life.
5. **Handoff & Next Steps:**
   - Suggest specific next actions based on the momentum:
     - Gather continuous background data via the iOS app.
     - Run the dashboard as an interactive local web app to iterate on it.
     - Ingest bulk historical data or integrate diverse external sources (e.g., Apple Health, Google Calendar) via other Fulcra skills.
