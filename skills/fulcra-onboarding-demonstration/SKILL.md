---
name: fulcra-onboarding-demonstration
description: "Handles the 'Time-to-Wow' demonstration phase of Fulcra onboarding by generating a custom themed SVG dashboard visualizing the user's recorded data."
---

# Fulcra Onboarding: Demonstration (Time-to-Wow)

This skill handles Step 5 of the onboarding process. The goal is to immediately show the user the value of the data they just modeled and recorded by presenting it in a highly personalized, visual way using an inline SVG.

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

3. **Generate SVG Dashboard:**
   - Once a theme is chosen, generate a custom SVG file visualizing the data.
   - Ensure the dashboard visually incorporates the actual data retrieved in Step 1.
   - Present the SVG to the user directly in the chat thread (e.g., by writing it to the workspace and attaching it to your message).
   - The design should heavily reflect their chosen aesthetic and make the data look interesting.

## Handoff

Once the SVG dashboard has been successfully generated and presented, wait for the user's reaction. After acknowledging their response, return control to the main `fulcra-onboarding` flow to handle the final App Download handoff.
