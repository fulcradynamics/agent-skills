---
name: fulcra-onboarding-demonstration
description: "Handles the 'Time-to-Wow' demonstration phase of Fulcra onboarding by generating a custom themed HTML dashboard visualizing the user's recorded data."
---

# Fulcra Onboarding: Demonstration (Time-to-Wow)

This skill handles Step 5 of the onboarding process. The goal is to immediately show the user the value of the data they just modeled and recorded by presenting it in a highly personalized, visual way using an inline HTML dashboard.

## Workflow

1. **Retrieve Data:**
   - Retrieve the user's recently recorded data from Fulcra. 
   - **How to retrieve:** 
     - First, silently run `uv tool run fulcra-api catalog` to list available data types. Find the exact identifier (name or ID) for the annotation the user just created.
     - Then, use that identifier as the `DATA_TYPE` argument in the `uv tool run fulcra-api get-records <DATA_TYPE> <TIME_RANGE>` CLI command (e.g., `uv tool run fulcra-api get-records "MyCustomAnnotation" "1 day"`). 
     - This is the most reliable method for accessing raw recorded data. Do *not* use external skills for this step.

2. **Theme Selection:**
   - Ask the user how they would like their dashboard themed.
   - Suggest 2-3 creative, distinct options based on your sense of their personality and the data they are tracking (e.g., cyberpunk, fantasy, newspaper, modern fashion magazine, professional workplace tool, retro 8-bit).
   - Keep this interaction brief and engaging.

3. **Generate HTML Dashboard:**
   - Once a theme is chosen, generate a custom HTML file visualizing the data.
   - **Crucial: The "Wow" Factor:** Because the user has likely only recorded a single piece of data, the design must carry the experience. Do not generate a boring standard chart. 
   - **Design Directives:**
     - **Metaphorical UI:** Design a UI that fits the data type and theme (e.g., a retro receipt for coffee, a glowing HUD for fitness, a vintage polaroid for a mood check-in).
     - **Rich Styling:** Use embedded CSS to create a highly polished look. Leverage Google Fonts, CSS gradients, complex box-shadows, and layout techniques (Flexbox/Grid).
     - **CSS Animations:** Include simple CSS animations (e.g., pulsing glows, slide-ins, typing effects) to make the dashboard feel alive.
     - **Intent-Driven Copy:** Include clever, personalized micro-copy in the dashboard that nods to the user's broader intent and the specific theme.
   - Ensure the dashboard visually incorporates the actual data retrieved in Step 1.
   - Present the HTML to the user directly in the chat thread (e.g., by writing it to the workspace and providing a way to view it).

## Handoff

Once the HTML dashboard has been successfully generated and presented, wait for the user's reaction. After acknowledging their response, return control to the main `fulcra-onboarding` flow to handle the final App Download handoff.
