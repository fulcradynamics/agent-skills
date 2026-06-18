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

The onboarding process follows a strict two-phase "Hub and Spoke" model. First, you get the user connected. Then, you present a menu of options and let the user choose what to do next.

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

### Phase 2: Next Steps (The Spokes)

Immediately after declaring the core onboarding complete, present the following menu of next steps to the user. Do not force them down any path automatically.

**Present this exact scannable menu to the user:**

1.  📊 **Agent Visibility & Custom Tracking:** Discover how to track custom data, agent visibility metrics, and visualize them using a custom dashboard.
2.  🧠 **Agent Memory Backup:** Back up agent memory and high level context directly to your Fulcra datastore.
3.  🤝 **Agent Coordination:** Set up shared team namespaces so your different agents can coordinate tasks.
4.  📱 **Get the App:** Download the iOS app for on-the-go logging and background sync.
5.  💻 **Context Web:** Explore your data on the desktop portal.

**When the user makes a choice, follow the corresponding path below:**

#### Path 1: Agent Visibility & Custom Tracking
1. Explain that you can set up data schemas to track their custom data, as well as an "Agent Visibility Package" to record agent activities, and visualize it all on a custom HTML dashboard.
2. If they consent and are interested, transition them to the `fulcra-tracking` skill.

#### Path 2: Agent Memory Backup
1. Explain that you can back up agent memory and high level context directly to their datastore. 
2. If they consent, transition them to the `fulcra-memory` skill to perform the backup.

#### Path 3: Agent Coordination
1. Explain that Fulcra isn't just for dashboards—it acts as a universal backend that allows multiple agents to coordinate their work using shared Team namespaces.
2. If they consent and are interested, transition them to the `fulcra-agent-teams` skill so they can get set up.

#### Path 4: Get the App
1. Direct them to the [Fulcra Context iOS app](https://apps.apple.com/app/id1633037434).
2. Mention it unlocks automatic background sync (Health, location, calendar). **PRIVACY WARNING:** Explicitly inform the user these are highly sensitive data types requiring explicit iOS permissions, and they have full control to decline.

#### Path 5: Context Web
1. Direct them to [Context Web](https://context.fulcradynamics.com/) to explore their datastore on desktop.
