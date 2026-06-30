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

## Workflow: Hub and Spoke Model

The onboarding process follows a strict three-phase model. First, you get the user connected. Second, you demonstrate immediate value ("Time-to-Wow") by modeling custom data and generating an embedded Canvas dashboard. Third, you present a menu of options and let the user choose what to do next.

### Phase 1: Core Setup (The Hub)

1. **Introduction to Fulcra:**
   - Read the `references/fulcra-cli.md` file to understand the `fulcra-api` CLI context and capabilities.
   - Start the conversation by giving the user a brief, exciting overview of what Fulcra is (a universal data and memory platform that collects and records any data from any source).
   - Tell the user that the first step is to get them connected to Fulcra by setting up the Fulcra CLI. **Do not execute any CLI setup or ask for installation permissions until you have introduced Fulcra.**

2. **Pre-flight Check & Context:**
   - Read and execute the instructions in `references/fulcra-onboarding-prerequisites.md` to verify and install `uv` if necessary, asking the user for confirmation before installation. This must pass before proceeding.

3. **Authentication:**
   - Read and execute the instructions in `references/fulcra-onboarding-auth.md`. This step securely authenticates the user via the Fulcra CLI. 
   - Once authenticated, declare that the core onboarding is complete! Celebrate this milestone.

### Phase 2: The Time-to-Wow (Custom Tracking & Canvas Dashboard)

Immediately after authentication, do not just give them a menu. Show them the power of Fulcra by building a custom data tracker and dashboard right inside the chat.

1. **User Intent Discovery:** 
   - Ask the user for one simple thing they'd like to track in their daily life (e.g., mood, cups of coffee, energy level, tasks completed).
   - If they are unsure, suggest "Energy Level" (1-10) as a default.
2. **Data Modeling:** 
   - Use the `uv tool run fulcra-api data-type create` command to create the custom schema based on their choice (e.g. `uv tool run fulcra-api data-type create "EnergyLevel" "Number from 1-10 representing daily energy"`).
3. **Record First Data:** 
   - Ask for their current value for that metric and record it using a `curl` POST to the Ingest API (using `$(uv tool run fulcra-api auth print-access-token)` for auth).
4. **The Canvas Demonstration:** 
   - Generate a single-file HTML dashboard ("Single-Scroll Artifact") using Alpine.js and Vanilla CSS (and optionally D3.js) to visualize this new data concept. Make it beautiful and on-theme.
   - **Crucial:** Save this file to the active Canvas profile root: `~/.openclaw/canvas/documents/fulcra-demo/index.html` (create the directory if it doesn't exist).
   - Present the dashboard inline in the chat using the OpenClaw Canvas Embed tag: `[embed url="/__openclaw__/canvas/documents/fulcra-demo/index.html" title="Fulcra Data Demo" height="400" /]`
   - Tell the user this is just a quick taste, and a fully interactive local web app can be built later.

### Phase 3: Next Steps (The Spokes)

After they experience the Canvas demonstration, present the following menu of next steps to the user. Do not force them down any path automatically.

**Present this exact scannable menu to the user:**

1.  📊 **Advanced Dashboards & Agent Visibility:** Discover how to track complex data, agent visibility metrics, and build a permanent live dashboard web app.
2.  📡 **Situational Awareness:** Enable your agent to proactively scan for recent updates, team messages, and new data.
3.  🧠 **Agent Memory & Knowledge:** Record high-level knowledge, tasks, and progress directly to your Fulcra datastore.
4.  🤝 **Agent Coordination:** Set up shared team namespaces so your different agents can coordinate tasks.
5.  📱 **Get the App:** Download the iOS app for on-the-go logging and background sync.
6.  💻 **Context Web:** Explore your data on the desktop portal.

**When the user makes a choice, follow the corresponding path below:**

#### Path 1: Advanced Dashboards & Agent Visibility
1. Explain that what they just saw was a quick preview. You can set up much more complex data schemas (including an "Agent Visibility Package" to track your own agent work) and generate a permanent, interactive React-based or Alpine-based web dashboard.
2. If they consent and are interested, transition them to the `fulcradynamics/agent-skills/fulcra-dashboard` skill.

#### Path 2: Situational Awareness
1. Explain that you can set up a proactive habit where the agent checks Fulcra for new files, team messages, and recently ingested data at the start of new conversations, keeping it highly context-aware.
2. If they consent, transition them to the `fulcradynamics/agent-skills/fulcra-situational-awareness` skill to enable this behavior.

#### Path 3: Agent Memory & Knowledge
1. Explain that you can record high-level knowledge, track tasks, and log ongoing progress directly to their Fulcra datastore in a structured, readable way.
2. If they consent, transition them to the `fulcradynamics/agent-skills/fulcra-memory` skill to set up their memory tracking.

#### Path 4: Agent Coordination
1. Explain that Fulcra isn't just for dashboards—it acts as a universal backend that allows multiple agents to coordinate their work using shared Team namespaces.
2. If they consent and are interested, transition them to the `fulcradynamics/agent-skills/fulcra-agent-teams` skill so they can get set up.

#### Path 5: Get the App
1. Direct them to the [Fulcra Context iOS app](https://apps.apple.com/app/id1633037434).
2. Mention it unlocks automatic background sync (Health, location, calendar). **PRIVACY WARNING:** Explicitly inform the user these are highly sensitive data types requiring explicit iOS permissions, and they have full control to decline.

#### Path 6: Context Web
1. Direct them to [Context Web](https://context.fulcradynamics.com/) to explore their datastore on desktop.
