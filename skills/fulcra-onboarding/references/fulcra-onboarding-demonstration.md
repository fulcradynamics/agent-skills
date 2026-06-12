---
name: fulcra-onboarding-demonstration
description: "Handles the 'Time-to-Wow' demonstration phase of Fulcra onboarding by generating a custom themed HTML dashboard visualizing the user's recorded data."
---

# Fulcra Onboarding: Demonstration (Time-to-Wow)

**Tone Reminder:** This is the payoff! Present this dashboard with excitement. Use emojis and a fun, conversational tone that celebrates what they just built and hints at what else is possible.

This skill handles Step 7 of the onboarding process. The goal is to immediately show the user the value of the data they just modeled and recorded by presenting it in a highly personalized, visual way using an inline HTML dashboard.

## Workflow

1. **Retrieve Data (Requires Consent):**
   - Retrieve the user's recently recorded data from Fulcra to build the dashboard. 
   - **Before fetching:** Briefly explain that you need to retrieve their recorded data to visualize it, and ask for permission to query the Fulcra API.
   - **How to retrieve:** 
     - After consent is given, run `uv tool run fulcra-api catalog` to list available data types. Find the exact identifier (name or ID) for the annotation the user just created.
     - Then, use that identifier as the `DATA_TYPE` argument in the `uv tool run fulcra-api get-records <DATA_TYPE> <TIME_RANGE>` CLI command (e.g., `uv tool run fulcra-api get-records "MyCustomAnnotation" "1 day"`). Make sure to capture **all** returned records, not just the first one.
     - This is the most reliable method for accessing raw recorded data. Do *not* use the `fulcra-dashboard` skill for this demonstration step. The dashboard generated in this step should be a single, standalone HTML file generated from scratch using the user's chosen theme.

2. **Theme Selection (MANDATORY BLOCKER):**
   - **CRITICAL:** You must explicitly pause the conversation and wait for the user to choose a theme before generating the HTML. Do **not** generate the dashboard in the same turn that you retrieve the data.
   - Suggest 2-3 creative, distinct thematic options based on your sense of their personality and the data they are tracking (e.g., if tracking coffee, suggest a "retro diner receipt" or a "cyberpunk neon HUD").
   - Wait for their reply. Only proceed to generation once they have confirmed a theme.

3. **Generate HTML Dashboard (Post-Theme Selection):**
   - Once a theme has been explicitly chosen by the user, generate a custom HTML file visualizing the data.
   - **Crucial: The "Wow" Factor:** Because the user has likely only recorded a single piece of data, the design must carry the experience. Do not generate a boring standard chart. 
   - **Design Directives:**
     - **Metaphorical UI:** Design a UI that fits the data type and theme (e.g., a retro receipt for coffee, a glowing HUD for fitness, a vintage polaroid for a mood check-in).
     - **Rich Styling:** Use embedded CSS to create a highly polished look. Leverage Google Fonts, CSS gradients, complex box-shadows, and layout techniques (Flexbox/Grid).
     - **CSS Animations:** Include simple CSS animations (e.g., pulsing glows, slide-ins, typing effects) to make the dashboard feel alive.
     - **Intent-Driven Copy:** Include clever, personalized micro-copy in the dashboard that nods to the user's broader intent and the specific theme.
     - **Visual Extensibility:** Design the layout to explicitly convey that this is a living, expandable surface. Include UI hints like "Empty Slots," grayed-out "Coming Soon" sections, or placeholder modules for other related data types they might want to track in Fulcra next.
   - Ensure the dashboard visually incorporates **all** the actual data points retrieved in Step 1 (e.g., mapped out as a timeline or a list of recent entries).
   - **Agent Memory Status:** If you performed an Agent Baseline Backup during Step 2 of this onboarding session, add a simple, discreet indicator (like a checkmark or a small "Memory Vault: Secured" badge) to the dashboard showing that your memory was successfully backed up. Do not list specific filenames, sizes, or metadata.
   - **Bulletproof Presentation:** To avoid permission or rendering errors, present the HTML to the user using this resilient approach:
     1. **Primary Display (Optional):** If you are confident you can display the dashboard in a richer way (e.g., using a native Canvas integration or Control UI embed), you may attempt it. However, do not attempt to reconfigure the agent's settings to achieve this.
     2. **File Fallback (Required):** Always save the generated HTML to a file in the workspace (e.g., `fulcra-dashboard.html`). 
        - **Important:** Clearly inform the user that a local HTML file will be created in their workspace before you write to it.
        - Attach the file directly to your message in the chat thread so the user can easily download/view it. **Crucial Formatting:** Ensure you write a short introductory sentence and a line break *before* the file attachment directive in your message. If the media attachment is the very first thing in your final reply, the chat UI parsing may break and display raw formatting tags.
        - Output the absolute path and tell the user they can open it directly in their web browser (e.g., `open /absolute/path/to/fulcra-dashboard.html`) to view the final rendered result. Do not output the raw HTML source code in the chat, as this clutters the experience.

## Handoff

Once the dashboard has been successfully generated and presented, wait for the user's reaction. After acknowledging their response, return control to the main `fulcra-onboarding` flow to handle the final Next Steps (Step 8).
