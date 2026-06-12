---
name: fulcra-onboarding-coordination
description: "Handles the agent coordination step (Step 4) of Fulcra onboarding, asking about multiple agents and suggesting the fulcra-agent-teams skill."
---

# Fulcra Onboarding: Agent Coordination

**Tone Reminder:** Conversational, helpful, and focused on unlocking more capability.

This skill handles Step 4 of the onboarding process, introducing the user to the concept of coordinating multiple agents through Fulcra's shared memory backend.

## Workflow

1. **Ask About Multiple Agents & Explain Coordination:**
   - In a single, friendly message, ask the user if they currently use multiple agents (e.g., OpenClaw, Claude Code, Cursor, ChatGPT, etc.).
   - In the same message, explain that Fulcra isn't just for dashboards—it acts as a universal backend that allows multiple agents to coordinate their work. Instead of relying on isolated chat histories, agents can use shared Team namespaces to coordinate tasks and drop files in each other's inboxes.

2. **Offer the `fulcra-agent-teams` Skill:**
   - If they are using multiple agents and express interest in this capability, explain that you can help them get set up.
   - Ask for their explicit permission to install the `fulcra-agent-teams` skill.
   - If you have the necessary capabilities (e.g., through an execution tool), install it for them upon confirmation. If you cannot install it yourself, politely provide them with the instructions to install it.

3. **Proceed to Data Modeling:**
   - Once this coordination conversation is concluded (whether they install the skill, decline, or aren't using multiple agents), seamlessly transition to Data Modeling & Continuous Agent Tracking (Step 5).