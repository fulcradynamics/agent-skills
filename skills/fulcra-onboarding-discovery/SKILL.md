---
name: fulcra-onboarding-discovery
description: "Handles the initial discovery and authentication phase for new Fulcra users. Guides the user through login, uncovers their core intent, and suggests concrete use cases."
---

# Fulcra Onboarding: Discovery

This skill handles the first phase of the Fulcra onboarding process (Step 1). Its primary goals are to ensure the user is authenticated and to rapidly identify how Fulcra can be most useful to them right now.

## Workflow

0. **Prerequisites Check (`uv`):**
   - Before interacting with the Fulcra API, silently verify if `uv` is installed by running `uv --version`.
   - If `uv` is not installed, install it automatically (e.g., `curl -LsSf https://astral.sh/uv/install.sh | sh` on macOS/Linux) or gently guide the user to install it. Ensure `uv` is available in the environment before proceeding.

1. **Authentication Check:**
   - Verify if the user is currently authenticated with Fulcra.
   - If not authenticated, run `uv tool run fulcra-api auth login` and guide the user through the device code flow.

2. **Intent Discovery:**
   - Engage the user in a brief, natural conversation to uncover their core intent. What do they want to track, remember, or build?

3. **Proactive Suggestions:**
   - Suggest simple, concrete examples of how they could use Fulcra (e.g., specific Annotations to track).
   - Tailor these suggestions using your existing memory and knowledge of the user.
   - Keep the pace brisk to reach the "wow" factor quickly.

## Handoff

Once the user is authenticated and you have clearly identified 2-3 specific custom data types or streams (Annotations) they want to track, hand control back to the main `fulcra-onboarding` flow to proceed with Data Modeling.
