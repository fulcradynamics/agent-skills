---
name: fulcra-onboarding-demonstration
description: "Handles the 'Time-to-Wow' demonstration phase of Fulcra onboarding by generating a custom themed HTML Canvas dashboard visualizing the user's recorded data."
---

# Fulcra Onboarding: Demonstration (Time-to-Wow)

This skill handles Step 5 of the onboarding process. The goal is to immediately show the user the value of the data they just modeled and recorded by presenting it in a highly personalized, visual way.

## Workflow

1. **Retrieve Data:**
   - Retrieve the user's recently recorded data from Fulcra. 
   - *Note:* Use the `fulcra-context` skill (from https://clawhub.ai/arc-claw-bot/fulcra-context) to fetch this data if available, or use the `fulcra-api` CLI directly if necessary.

2. **Theme Selection:**
   - Ask the user how they would like their dashboard themed.
   - Suggest 2-3 creative, distinct options based on your sense of their personality and the data they are tracking (e.g., cyberpunk, fantasy, newspaper, modern fashion magazine, professional workplace tool, retro 8-bit).
   - Keep this interaction brief and engaging.

3. **Generate Canvas Dashboard:**
   - Once a theme is chosen, generate a custom HTML/CSS dashboard using the OpenClaw Canvas system.
   - Ensure the dashboard visually incorporates the actual data retrieved in Step 1.
   - Present the Canvas to the user (e.g., using the `[embed ...]` directive or the appropriate canvas tool command).
   - The design should heavily reflect their chosen aesthetic and make the data look interesting.

## Handoff

Once the dashboard has been successfully generated and presented, wait for the user's reaction. After acknowledging their response, return control to the main `fulcra-onboarding` flow to handle the final App Download handoff.
