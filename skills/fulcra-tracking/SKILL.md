---
name: fulcra-tracking
description: "Allows the user to record custom data annotations and agent visibility metrics, and generates simple HTML dashboards for visualization."
homepage: "https://github.com/fulcradynamics/agent-skills"
license: "MIT"
user-invocable: true
metadata: { "openclaw": { "emoji": "📊" } }
---

# Fulcra Tracking & Dashboards

This skill guides the user through discovering data they want to track in Fulcra, setting up the necessary schemas (including the Agent Visibility Package), recording data, and generating a custom HTML dashboard to display it.

## General Guidelines

- **Tone & Vibe:** Engaging, conversational, and focused on demonstrating the immediate value ("Time-to-Wow") of Fulcra's data tracking capabilities.
- **Maintain Momentum:** Guide the user quickly from schema creation to data entry to dashboard generation.

## Workflow

1.  **User Intent Discovery:** 
    - Read the `references/fulcra-tracking-cli.md` file to understand the custom tracking CLI commands.
    - Read and execute `references/fulcra-tracking-discovery.md` to uncover what the user wants to track and pitch the Universal Agent Visibility Package.
2.  **Data Modeling:** 
    - Use the `fulcra-api data-type create` command to create the custom schemas based on the user's intent. 
    - **Crucial:** If they opted into the Agent Visibility Package, create those schemas (e.g., Tasks Completed, Agent Friction, Current Agent Work) alongside their personal schemas and actively record your high-level milestones into them from this point forward. Remember the `id`s returned by the create command.
3.  **Record First User Data:** 
    - Ask a direct question to get their first piece of data for one of their new schemas, then record it using `references/fulcra-tracking-record-annotations.md`. 
    - Do not use `curl` for this. Use the `fulcra-api` CLI if a specific `record` command is available, or fallback to the instructions in the record annotations reference file.
4.  **Time-to-Wow (The Demonstration):** 
    - Read and execute `references/fulcra-tracking-demonstration.md` to fetch the data and generate a custom HTML dashboard. 
    - **Architectural Rules:** Follow the "Static Triad" (index.html, app.js, theme.css) or single-scroll artifact paradigm using Alpine.js, D3.js, and pure Vanilla CSS. **Do not use Tailwind via CDN** due to CSP conflicts. 
    - Stop and ask for a theme *before* generating.
5.  **Handoff to Dashboard Skill:**
    - Once the user is satisfied with their static HTML dashboard demonstration, explicitly inform them that they can make this dashboard a permanent, live, interactive artifact that updates automatically.
    - Tell them they can transition to the `fulcra-dashboard` skill to generate a durable React-based dashboard app backed by their Fulcra data.
