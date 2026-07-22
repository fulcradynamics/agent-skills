---
name: fulcra-onboarding
description: "Guides a new user or agent through the initial setup, configuration, and capabilities of the Fulcra environment."
homepage: "https://github.com/fulcradynamics/agent-skills"
license: "MIT"
user-invocable: true
metadata: { "openclaw": { "emoji": "🌱" } }
---

# Fulcra Onboarding

Guide the user through connecting to Fulcra in a fluid, intent-driven way.

Fulcra helps agents know their user, know what's happening in their user's world, work with their user's other agents, and become more helpful over time. It provides a shared place to access and store real-world data, record what matters, coordinate work, and discover what's new on every loop.

## Playbook

Treat this as a fluid conversation. Avoid sounding like a rigid script.

### 1. Discover Intent
Before diving into technical setup, establish the user's goal.
- **Use Existing Context:** If the user has already stated a goal (e.g., "I want to track my Spotify data" or "Help me set up an agent workspace"), acknowledge it immediately. 
- **Open-Ended Start:** If their goal is ambiguous, have a lightweight chat to figure it out. You can suggest things like connecting 3rd-party data, setting up a shared agent workspace, or tracking custom metrics based on the core value propositions.
- Frame the upcoming setup not as "onboarding", but as the necessary step to unlock their specific goal.

### 2. The Auth Flow (Headless)
Because you are running in a headless terminal, you cannot open a browser for the user. To authenticate them smoothly, always use the `--get-auth-url` flag so you can hand them a clickable link.

**Pre-flight:** Verify `uv` is installed (`uv --version`). It is required for the CLI. If missing, ask permission to install it.

**Authentication Steps:**
1. Check if the user is already authenticated by running `uv tool run fulcra-api user-info`. If it succeeds, skip to Phase 3!
2. Run this exact command to generate a secure link:
   `uv tool run fulcra-api auth login --get-auth-url`
3. Present the generated web auth URL and `user_code` to the user in a friendly message. Tell them to click the link and enter the code. Do not proceed until they confirm they are done.
4. Once they confirm, complete the login using the device code you received in step 2:
   `uv tool run fulcra-api auth login --device-code <DEVICE_CODE> --poll-timeout=5`
5. Once authenticated, celebrate the milestone!

*(Note for Restricted Environments: If the CLI fails due to outbound network blocks, fallback to the MCP Connector. Fetch and read `https://fulcradynamics.github.io/developer-docs/mcp-server/` for setup instructions.)*

### 3. Fluid Branching
Once connected, seamlessly transition to their goal by loading the appropriate skill. Do not show them a rigid menu; instead, guide them based on what you discussed in step 1.

- If they want to **access and store real-world data**: transition to `fulcradynamics/agent-skills/fulcra-ingest`
- If they want to **discover what's new on every loop**: transition to `fulcradynamics/agent-skills/fulcra-situational-awareness`
- If they want to **coordinate work** with other agents: transition to `fulcradynamics/agent-skills/fulcra-agent-teams`
- If they want to **track custom metrics**: transition to `fulcradynamics/agent-skills/fulcra-tracking`
- If they want to **record what matters**: transition to `fulcradynamics/agent-skills/fulcra-memory`

**The Recommended "Golden Path" (For Open-Ended Users)**
If the user doesn't have a specific path in mind yet, you should strongly recommend this specific sequence to show them the true power of Fulcra. Ask if they'd like to be guided through it:
1. **Connect a Data Source:** Give agents a way to **access and store real-world data** (`fulcradynamics/agent-skills/fulcra-ingest`).
2. **Know What's New:** Set up an automated loop to **discover what's new on every loop** (`fulcradynamics/agent-skills/fulcra-situational-awareness`).
3. **Set Up Workspaces:** Create an agent workspace to **coordinate work** with other agents (`fulcradynamics/agent-skills/fulcra-agent-teams`).

If they decline the golden path, offer a quick conversational tour of the remaining options (Tracking, Memory, etc.) based on the value propositions and let them choose what sounds best.
