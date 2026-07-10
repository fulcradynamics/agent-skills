---
name: fulcra-onboarding
description: "Guides a new user or agent through the initial setup, configuration, and capabilities of the Fulcra environment."
homepage: "https://github.com/fulcradynamics/agent-skills"
license: "MIT"
user-invocable: true
metadata: { "openclaw": { "emoji": "🌱" } }
---

# Fulcra Onboarding

Primary onboarding flow for new users connecting to the Fulcra environment. Fulcra is a universal data and memory backend for agents that securely stores personal context and custom data streams.

## General Guidelines

- **Tone & Vibe (The "Wow" Factor):** Fulcra unlocks massive potential because it acts as a universal memory and data backend for agents. Your tone should reflect this excitement and vast possibility. Be engaging, conversational, and fun.
- **Use Emojis:** Liberally (but tastefully) use emojis throughout the onboarding process, especially when presenting lists, options, or celebrating a successful step. **However, always defer to the user's overarching formatting preferences or memory instructions. If a user explicitly asks for no emojis or a more professional tone, respect their constraints over this guideline.**
- **Maintain Momentum:** Keep the user moving forward. If they get stuck, make a choice for them or offer a heavily opinionated default to get them to the "Time-to-Wow" demonstration as quickly as possible.

## Workflow: Guided Path

The onboarding process follows a guided three-phase model. First, you get the user connected. Second, you recommend a powerful "golden path" of core agent capabilities. Third, you present a menu of additional options.

### Phase 1: Core Setup

1. **Introduction to Fulcra:**
   - Read the `references/fulcra-cli.md` file to understand the `fulcra-api` CLI context and capabilities.
   - Start the conversation by giving the user a brief, exciting overview of what Fulcra is. **Specifically describe Fulcra as giving your agents a way to access and store real-world data, coordinate tasks, and know what's new on every loop, from a place that lives and moves with you across agents.**
   - Tell the user that the first step is to get them connected to Fulcra by setting up the Fulcra CLI. **Do not execute any CLI setup or ask for installation permissions until you have introduced Fulcra.**

2. **Pre-flight Check & Context:**
   - Read and execute the instructions in `references/fulcra-onboarding-prerequisites.md` to verify and install `uv` if necessary, asking the user for confirmation before installation. This must pass before proceeding.

3. **Authentication:**
   - Read and execute the instructions in `references/fulcra-onboarding-auth.md`. This step securely authenticates the user via the Fulcra CLI. 
   - Once authenticated, declare that the core onboarding is complete! Celebrate this milestone.

### Phase 2: The Recommended Flow

Immediately after declaring the core onboarding complete, recommend a specific post-onboarding path to the user. Ask them if they'd like to be guided through this sequence, explaining that it is the most truly useful way to get started with Fulcra:

1.  **Connect a Data Source:** Bring real-world data into the datastore (using the `fulcradynamics/agent-skills/fulcra-ingest` skill).
2.  **Know What's New:** Set up an automated loop so the agent knows what is new every loop (using the `fulcradynamics/agent-skills/fulcra-situational-awareness` skill).
3.  **Set Up Agent Teams:** Set up an agent team for one or more agents to build knowledge and complete tasks (using the `fulcradynamics/agent-skills/fulcra-agent-teams` skill).

If they agree, transition them sequentially through these skills.

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
