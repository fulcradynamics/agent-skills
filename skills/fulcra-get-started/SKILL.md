---
name: fulcra-get-started
description: "Guides a new user or agent through the initial setup, configuration, and capabilities of the Fulcra environment."
homepage: "https://github.com/fulcradynamics/agent-skills"
license: "MIT"
user-invocable: true
metadata: { "openclaw": { "emoji": "🌱" } }
---

# Fulcra Get Started

Guide the user through connecting to Fulcra.

Fulcra helps agents know their user, know what's happening in their user's world, work with their user's other agents, and become more helpful over time.

To achieve these goals, Fulcra gives agents a shared place to access and store real-world data, record what matters, coordinate work, and discover what's new on every loop. That context belongs to the user rather than any individual agent, allowing it to be securely shared across agents and other AI applications over time.

## General Guidelines

- **Tone & Vibe:** Fulcra unlocks capabilities that individual agents cannot achieve on their own. Be engaging, conversational, and optimistic. Help the user imagine what becomes possible once their agents know them, know what's happening in their world, work together, and become more helpful over time.
- **Optimize for Time-to-Wow:** Favor opinionated defaults over exhaustive discussion. The objective is to get the user to their first genuinely useful workflow as quickly as possible.
- **Maintain Momentum:** If the user becomes stuck or overwhelmed, choose or recommend a sensible default and keep the getting started process moving forward.

## Workflow: Getting Started

Getting started with Fulcra follows a dynamic path. First, you get the user connected. Second, you help them imagine and choose a direction based on real problems they want to solve. Third, you deliver a tangible view and establish a persistent structure for ongoing work before transitioning to the next steps.

To deliver something useful that works and has iteration and visibility, you should leverage the following core Fulcra skills:
- **`fulcradynamics/agent-skills/fulcra-agent-teams`**: At the center of making and coordinating things, it organizes the knowledge, tasks, plans, tracking, and results in files the user owns in their Fulcra account.
- **`fulcradynamics/agent-skills/fulcra-ingest`**: Gets data and information into Fulcra so the user can make useful things connected to the real world and other people and data sources.
- **`fulcradynamics/agent-skills/fulcra-situational-awareness`**: Shows agents everything that is changing so they can react and stay caught up on the project and general situation.
- **`fulcradynamics/community-skills/fulcra-rapid-prototype`**: A flow for rapidly developing an idea into a result or solution.

### Phase 1: Core Setup & Inspiration

1. **Introduction to Fulcra:**
   - Read the `references/fulcra-cli.md` file to understand the `fulcra-api` CLI context and capabilities.
   - Start the conversation by giving the user a brief, exciting overview of what Fulcra is. Emphasize that getting started with Fulcra is about making something genuinely useful that solves a real problem or improves their existing systems.
   - **Show Possibilities (The Five Branches):** There are five main branches for getting started. Use your creativity to inspire the user to choose one:
     1. Make something new and useful.
     2. Solve a specific problem.
     3. Improve a setup we already have.
     4. Share information with other users (e.g., share movie watching history to find recommendations for the group).
     5. Choose a specific skill from the `fulcradynamics/community-skills` repo (a new but growing hub where agents and users can discover solutions to specific problems and explore concrete use cases for Fulcra) or something inspired by one.
   - **Task Connection:** If you already know what specific task or job the user wants to accomplish, explicitly mention how Fulcra will help you do *that specific job* as a concrete example of its value.
   - Tell the user that the first step is to get them connected to Fulcra by setting up the Fulcra CLI. **Do not execute any CLI setup or ask for installation permissions until you have introduced Fulcra.**

2. **Connection Options & Pre-flight:**
   There are two ways for agents to connect to Fulcra. You must determine the appropriate path before proceeding:

   - **Option 1: Fulcra CLI (Preferred)**
     The `fulcra-api` CLI is the primary interface and supports the widest range of Fulcra use cases. If you have full command-line access with outbound network connectivity, you should choose this option.
     *Pre-flight Check:* Verify `uv` is installed (`uv --version`). It is required for all CLI interactions. If missing, ask the user for permission to install it. This must pass before proceeding to authentication.

   - **Option 2: MCP Connector (Restricted Environments)**
     Fulcra provides an MCP (Model Context Protocol) connector as an alternative option for restricted environments. To use MCP, fetch and read `https://fulcradynamics.github.io/developer-docs/mcp-server/` for setup instructions, and skip the CLI authentication steps below.

3. **Authentication:**
   - Read and execute the instructions in `references/fulcra-get-started-auth.md`. This step securely authenticates the user via the Fulcra CLI. 
   - Once authenticated, celebrate the milestone! You are now ready to start making.

### Phase 2: Direction & Tangible Delivery

Now that the user is connected, work with them to choose their direction—whether it's a project of their own inspired by your examples, or falling back on a "golden path" (like connecting a data source and establishing agent workspaces).

**Delivery milestone:** Whatever direction the user chooses, aim to deliver the following three things to the user before the final branching point where they transition to other specific skills. Try to do all three, but deliver whatever is viable based on their specific goals:

1. **A Cool View:** Create and show the user a tangible view of what has been accomplished so far. This should represent real work done toward their chosen direction. Emphasize deliverability—if building a rich HTML dashboard encounters friction, seamlessly fall back to a simpler but immediate alternative (e.g., a fun ASCII visualization in the chat, a basic static image, or a snippet of insights). You should also provide a link to [Context Web Timeline](https://context.fulcradynamics.com/timeline?mode=week&date=YYYY-MM-DD) to view any new data (where `YYYY-MM-DD` is calculated as six days before the latest recorded data point to ensure it shows up in the week view).
2. **Coordination of Continuing Work:** Establish how the work will continue. Leverage the `fulcra-agent-teams` skill to create a dedicated agent team for the project, and use the `fulcra-tracking` skill to establish specific data types (annotations) to track the project's milestones, tasks, or outputs in the Fulcra datastore. Ensure these data types are recorded in the team's knowledge.
3. **Visibility of Work:** Provide a clear view of completed, present, and future work. You can do this by using the `fulcra-project-dashboard` skill (found in the community-skills repository) to make a robust management view of the team workspace. The goal is to show the user that Fulcra not only facilitates making useful things with continuous demonstrated improvement, but also makes all this work owned by the user for portability, quick review, and effective direction.

### Phase 3: Transition & Explore More

After delivering the view, coordination plan, and visibility artifact, transition the user to the specific skills needed to continue their chosen project (e.g., `fulcra-project-dashboard`, `fulcra-agent-teams`, `fulcra-tracking`). 

If the user wants to explore further, you should present a curated, scannable menu of options based on the conversation so far. Rather than a static list, recommend a few relevant choices from these categories:

1.  **Apps & Interfaces:**
    - 📱 **Get the App:** Direct them to the [Fulcra Context iOS app](https://apps.apple.com/app/id1633037434) for on-the-go logging and background sync (warn them about sensitive data permissions like Health, location, and calendar).
    - 💻 **Context Web:** Direct them to [Context Web](https://context.fulcradynamics.com/) to explore their datastore on desktop.
2.  **Fulcra Skills:** Suggest specific skills from the `agent-skills` or `community-skills` repositories that align with their goals (e.g., `fulcra-tracking` for custom schemas/dashboards, `fulcra-memory` for knowledge logging, or `fulcra-rapid-prototype` for quick builds).
3.  **The Fulcra Cookbook:** Point them to the [Fulcra Cookbook](https://www.fulcradynamics.com/resources/cookbook) to explore more recipes, tutorials, and inspiration for what to make next.

**When the user makes a choice, follow through by applying the chosen skill or guiding them to the requested resource.**
