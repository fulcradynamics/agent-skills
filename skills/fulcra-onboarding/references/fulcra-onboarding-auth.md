---
name: fulcra-onboarding-auth
description: "Handles initial authentication for the Fulcra CLI."
---

# Fulcra Onboarding: Authentication

This reference handles Step 2 of the onboarding process, securely establishing the user's connection to Fulcra.

## Workflow

1. **Authentication Check & Login (Requires Consent):**
   - Briefly explain that you need to connect to their Fulcra account via the command line.
   - **Ask for their explicit permission** to check their Fulcra authentication state and initiate a login flow.
   - **How to verify:** After obtaining consent, run `uv tool run fulcra-api user-info`. If it returns valid JSON, the user is authenticated and you can proceed immediately to the next step.
   - If not authenticated, explain that you will now generate a secure login link, and then run `uv tool run fulcra-api auth login` using the `exec` tool. 
   - **CRITICAL EXECUTION NOTE:** You are likely running in a remote or headless environment where opening a browser automatically is impossible. The `auth login` command will output an authorization URL and a device code, and then hang in the background waiting for completion. You **MUST** extract the login URL and device code from the stdout, present them directly to the user in your chat message as a clickable markdown link where the URL itself is the text (e.g., `[https://...](https://...)`) along with the code, and wait for them to confirm completion. Remind them not to share the link or code. Do *not* combine the authentication instructions with further brainstorming.

2. **Completion:**
   - Once the user successfully authenticates (or if they were already authenticated), declare the core onboarding complete!
   - Hand control back to the main `fulcra-onboarding` flow to present the Next Steps menu.