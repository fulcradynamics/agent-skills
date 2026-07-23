---
name: fulcra-onboarding
description: "Guides a new user or agent through the initial setup, configuration, and capabilities of the Fulcra environment."
homepage: "https://github.com/fulcradynamics/agent-skills"
license: "MIT"
user-invocable: true
metadata: { "openclaw": { "emoji": "🌱" } }
---

# Fulcra Onboarding

Guide the user through connecting to Fulcra.

Fulcra helps agents know their user, know what's happening in their user's world, work with their user's other agents, and become more helpful over time.

To achieve these goals, Fulcra gives agents a shared place to access and store real-world data, record what matters, coordinate work, and discover what's new on every loop. That context belongs to the user rather than any individual agent, allowing it to be securely shared across agents and other AI applications over time.

## General Guidelines

- **Tone & Vibe:** Fulcra unlocks capabilities that individual agents cannot achieve on their own. Be engaging, conversational, and optimistic. Help the user imagine what becomes possible once their agents know them, know what's happening in their world, work together, and become more helpful over time.
- **Optimize for Time-to-Wow:** Favor opinionated defaults over exhaustive discussion. The objective is to get the user to their first genuinely useful workflow as quickly as possible.
- **Maintain Momentum:** If the user becomes stuck or overwhelmed, choose or recommend a sensible default and keep the getting started process moving forward.

## Workflow: Getting Started

Getting started with Fulcra follows a dynamic path. First, you get the user connected. Second, you help them imagine and choose a direction based on real problems they want to solve. Third, you deliver a tangible view and establish a persistent structure for ongoing work before transitioning to the next steps.

### Phase 1: Core Setup & Inspiration

1. **Introduction to Fulcra:**
   - Read the `references/fulcra-cli.md` file to understand the `fulcra-api` CLI context and capabilities.
   - Start the conversation by giving the user a brief, exciting overview of what Fulcra is. Emphasize that getting started with Fulcra is about building something genuinely useful that solves a real problem or improves their existing systems.
   - **Show Possibilities:** Use your creativity and knowledge of Fulcra's capabilities to inspire the user. Provide examples of basic functionality (like data ingestion and situational awareness) as well as complete products (like agent coordination using the `fulcra-agent-coordination` skill from the `fulcradynamics/community-skills` repo). Your goal is to suggest ideas that make the user think, "I really want to make that."
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
   - Read and execute the instructions in `references/fulcra-onboarding-auth.md`. This step securely authenticates the user via the Fulcra CLI. 
   - Once authenticated, celebrate the milestone! You are now ready to start building.

### Phase 2: Direction & Tangible Delivery

Now that the user is connected, work with them to choose their direction—whether it's a project of their own inspired by your examples, or falling back on a "golden path" (like connecting a data source and establishing agent workspaces).

**Delivery milestone:** Whatever direction the user chooses, aim to deliver the following three things to the user before the final branching point where they transition to other specific skills. Try to do all three, but deliver whatever is viable based on their specific goals:

1. **A Cool View:** Create and show the user a tangible view of what has been accomplished so far. This should represent real work done toward their chosen direction (e.g., a sample data visualization, a generated HTML artifact, a snippet of insights, or an initial test output).
2. **Coordination of Continuing Work:** Establish how the work will continue. Leverage the `fulcra-agent-teams` skill to create a dedicated agent team for the project, and use the `fulcra-tracking` skill to establish specific data types (annotations) to track the project's milestones, tasks, or outputs in the Fulcra datastore. Ensure these data types are recorded in the team's knowledge.
3. **Visibility of Work:** Provide a clear view of completed, present, and future work. You can do this by using the `project-dashboard` skill (found in the community-skills repository) to build a robust management view of the team workspace. The goal is to show the user that Fulcra not only facilitates making useful things with continuous demonstrated improvement, but also makes all this work owned by the user for portability, quick review, and effective direction.

### Phase 3: Transition & Explore More

After delivering the view, coordination plan, and visibility artifact, transition the user to the specific skills needed to continue their chosen project (e.g., `project-dashboard`, `fulcra-agent-teams`, `fulcra-tracking`). 

If the user wants to explore further, you can present this scannable menu of additional options:

1.  📊 **Agent Visibility & Custom Tracking:** Discover how to track custom data, agent visibility metrics, and visualize them using a custom dashboard.
2.  🧠 **Agent Memory & Knowledge:** Record high-level knowledge, tasks, and progress directly to your Fulcra datastore.
3.  📱 **Get the App:** Download the iOS app for on-the-go logging and background sync.
4.  💻 **Context Web:** Explore your data on the desktop portal.

**When the user makes a choice, follow the corresponding path below:**

#### Path 1: Agent Visibility & Custom Tracking
1. Explain that you can set up data schemas to track their custom data, as well as an "Agent Visibility Package" to record agent activities, and visualize it all on a custom HTML dashboard.
2. If they consent and are interested, transition them to the `fulcra-tracking` skill.

#### Path 2: Agent Memory & Knowledge
1. Explain that you can record high-level knowledge, track tasks, and log ongoing progress directly to their Fulcra datastore in a structured, readable way.
2. If they consent, transition them to the `fulcra-memory` skill to set up their memory tracking.

#### Path 3: Get the App
1. Direct them to the [Fulcra Context iOS app](https://apps.apple.com/app/id1633037434).
2. Mention it unlocks automatic background sync (Health, location, calendar). **PRIVACY WARNING:** Explicitly inform the user these are highly sensitive data types requiring explicit iOS permissions, and they have full control to decline.

#### Path 4: Context Web
1. Direct them to [Context Web](https://context.fulcradynamics.com/) to explore their datastore on desktop.
