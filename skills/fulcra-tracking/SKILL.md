---
name: fulcra-tracking
description: "Allows the user to record custom data annotations and agent visibility metrics, and generates simple HTML dashboards for visualization. Use when the user wants to track custom data such as habits, moods, or metrics, record entries, or see a quick dashboard preview of tracked data."
license: "MIT"
metadata:
  homepage: "https://github.com/fulcradynamics/agent-skills"
  user-invocable: "true"
  openclaw: "{\"emoji\": \"📊\"}"
---

# Fulcra Tracking & Dashboards

This skill guides the user through discovering data they want to track in Fulcra, setting up the necessary schemas (including the Agent Visibility Package), recording data, and generating a custom HTML dashboard to display it.

## General Guidelines

- **Tone & Vibe:** Engaging, conversational, and focused on demonstrating the immediate value ("Time-to-Wow") of Fulcra's data tracking capabilities.
- **Maintain Momentum:** Guide the user quickly from schema creation to data entry to dashboard generation.

## Workflow Context

Before executing this skill, determine your current context:
- **Standalone Mode:** If the user directly asks you to track something new and you lack broader project context, follow the full workflow below (starting with Discovery).
- **Project/Team Mode:** If you are invoking this skill as part of an ongoing project, team workspace (`fulcra-workspaces`), or an overarching onboarding flow, the required data types are usually already dictated by the project scope. In this case, **skip Step 1 (Discovery) and Step 4 (Quick Visibility)**. Jump straight to creating the required schemas (Data Modeling) and recording the data.

## Workflow

1.  **User Intent Discovery (Standalone Mode Only):** 
    - Read the `references/fulcra-tracking-cli.md` file to understand the custom tracking CLI commands, and `references/fulcra-tracking-usecases.md` for example tracking setups.
    - Ask the user what kind of specific data, events, or outputs they want to track for their project or life.
    - Propose the Universal Agent Visibility Package if they want visibility into background agent work or team accomplishments.
2.  **Data Modeling:** 
    - Use the `fulcra-api data-type create` command to create the custom schemas based on the user's intent. 
    - Remember the `id`s returned by the create command.
3.  **Record Data:** 
    - Prompt the user to enter their first piece of data for the new schema, or explain how they can automate it via other skills or apps.
4.  **Quick Visibility (Optional):** 
    - Emphasize visibility into work being done. While the full dashboard creation is handled elsewhere, if the conversation centers heavily on the data being recorded, you can whip up a quick, lightweight HTML preview page to show them the data layout. 
    - **Theming & Creativity:** If you do create a quick preview, stop and ask the user for a fun theme or vibe *before* generating it. Be creative with the CSS and styling to demonstrate the flexibility of the data.
    - **Architectural Rules:** If you create a quick HTML preview dashboard, it should be just a single file (HTML/CSS/JS all in one), not the triad. If the dashboard goes beyond a simple preview, transition the user to the `fulcra-dashboard` skill to implement the full Static Triad. **Do not use Tailwind via CDN** due to CSP conflicts.
5.  **Integration with Projects & Dashboards:**
    - Tell the user that the primary way to manage and visualize this data over time is through the `fulcra-dashboard` skill, and if working with a team, to ensure these data types are recorded in the `fulcra-workspaces` knowledge base.
