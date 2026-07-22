---
name: fulcra-getting-started-auth
description: "Handles initial authentication for the Fulcra CLI."
---

# Fulcra Getting Started: Authentication

This reference handles Step 2 of the getting started process, securely establishing the user's connection to Fulcra.

## Workflow

1. **Authentication Check & Login (Requires Consent):**
   - Briefly explain that you need to connect to their Fulcra account via the command line.
   - **Ask for their explicit permission** to check their Fulcra authentication state and initiate a login flow.
   - **How to verify:** After obtaining consent, run `uv tool run fulcra-api user-info`. If it returns valid JSON, the user is authenticated and you can proceed immediately to the next step.
   - If not authenticated, explain that you will now generate a secure login link.
   - Run `uv tool run fulcra-api auth login --get-auth-url` using the `exec` tool.
   - **CRITICAL EXECUTION NOTE:** You must ALWAYS execute this command using the `--get-auth-url` flag so it does not hang and poll. The command will output a web auth URL, a web auth user code, and a device code.
   - You **MUST** present the URL and the user code directly to the user in your chat message as a clickable markdown link where the URL itself is the text (e.g., `[https://...](https://...)`), tell them the user code, and tell them to complete the flow in their browser.
   - **Important:** Keep the device code secret/safe; you will need it for the next step. Do *not* combine the authentication instructions with further brainstorming.
   - Wait for the user to confirm they have completed the flow in their browser.
   - Once they confirm, run `uv tool run fulcra-api auth login --device-code <DEVICE CODE> --poll-timeout=5` to complete the authentication process. The timeout ensures the command fails quickly if they haven't actually completed the flow.

2. **Completion:**
   - Once the device code login succeeds (or if they were already authenticated), declare the core setup complete!
   - Hand control back to the main getting started flow to present the Next Steps menu.