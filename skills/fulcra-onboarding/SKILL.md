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
- **Maintain Momentum:** If the user becomes stuck or overwhelmed, choose or recommend a sensible default and keep the onboarding moving forward.

## Workflow: Guided Path

The onboarding process follows a guided three-phase model. First, you get the user connected. Second, you recommend a powerful "golden path" of core agent capabilities. Third, you present a menu of additional options.

### Phase 1: Core Setup

1. **Introduction to Fulcra:**
   - Read the `references/fulcra-cli.md` file to understand the `fulcra-api` CLI context and capabilities.
   - Start the conversation by giving the user a brief, exciting overview of what Fulcra is. Explain Fulcra conceptually in your own natural words, but make sure to include this core value proposition: it gives agents a way to access real-world data, coordinate tasks, "and know what's new on every loop, from a place that lives and moves with you across agents."
   - **Task Connection:** If you already know what specific task or job the user wants you to accomplish, explicitly mention how Fulcra will help you do *that specific job* as a concrete example of its value.
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
   - Once authenticated, declare that the core onboarding is complete! Celebrate this milestone.

### Phase 2: Task-Driven or Recommended Flow

Immediately after declaring the core onboarding complete, you must determine the best path forward based on your current context:

**Option A: The Task-Driven Path (Prioritize this!)**
If you already know what specific task, job, or goal the user wants you to accomplish (e.g., they asked you to "build a health dashboard", "ingest my Spotify history", or "set up my inbox"), you should prioritize that specific task to deliver value as quickly as possible.
- Briefly explain how Fulcra will facilitate their specific goal.
- Ask for their confirmation to branch off and immediately start working on that task (transitioning to the relevant skills), rather than going through the generic tour.

**Option B: The Standard Recommended Path**
If the user hasn't given you a specific task and is just exploring Fulcra generally, recommend this specific post-onboarding sequence. Ask them if they'd like to be guided through this sequence, explaining that it is the most truly useful way to get started with Fulcra:

1.  **Connect a Data Source:** Bring real-world data into the datastore (using the `fulcradynamics/agent-skills/fulcra-ingest` skill).
2.  **Know What's New:** Set up an automated loop so the agent knows what is new every loop (using the `fulcradynamics/agent-skills/fulcra-situational-awareness` skill).
3.  **Set Up Workspaces:** Create an agent workspace that gives your agent an inbox, a place to save things it creates, and a way to coordinate and work with other agents and people (using the `fulcradynamics/agent-skills/fulcra-agent-teams` skill).

If they agree to the recommended path, transition them sequentially through these skills.

### Phase 3: Explore More (The Menu)

After they complete the recommended path, or if they decide they do not want to do it, present the following menu of additional options to explore the Fulcra skills, app, and web dashboard.

**Present this exact scannable menu to the user:**

1.  📊 **Agent Visibility & Custom Tracking:** Discover how to track custom data, agent visibility metrics, and visualize them using a custom dashboard.
2.  🧠 **Agent Memory & Knowledge:** Record high-level knowledge, tasks, and progress directly to your Fulcra datastore.
3.  📱 **Get the App:** Download the iOS app for on-the-go logging and background sync.
4.  💻 **Context Web:** Explore your data on the desktop portal.

**When the user makes a choice, follow the corresponding path below:**

#### Path 1: Agent Visibility & Custom Tracking
1. Explain that you can set up data schemas to track their custom data, as well as an "Agent Visibility Package" to record agent activities, and visualize it all on a custom HTML dashboard.
2. If they consent and are interested, transition them to the `fulcradynamics/agent-skills/fulcra-tracking` skill.

#### Path 2: Agent Memory & Knowledge
1. Explain that you can record high-level knowledge, track tasks, and log ongoing progress directly to their Fulcra datastore in a structured, readable way.
2. If they consent, transition them to the `fulcradynamics/agent-skills/fulcra-memory` skill to set up their memory tracking.

#### Path 3: Get the App
1. Direct them to the [Fulcra Context iOS app](https://apps.apple.com/app/id1633037434).
2. Mention it unlocks automatic background sync (Health, location, calendar). **PRIVACY WARNING:** Explicitly inform the user these are highly sensitive data types requiring explicit iOS permissions, and they have full control to decline.

#### Path 4: Context Web
1. Direct them to [Context Web](https://context.fulcradynamics.com/) to explore their datastore on desktop.
