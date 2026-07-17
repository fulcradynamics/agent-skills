---
name: fulcra-control-panel
description: "Sets up a secure, local-only administration control panel for the Fulcra environment. Features an interactive Chat Envoy for direct agent communication, and a File Store Explorer for browsing the user's data backend."
homepage: "https://github.com/fulcradynamics/agent-skills"
license: "MIT"
user-invocable: true
metadata: { "openclaw": { "emoji": "🎛️" } }
---

# Fulcra Control Panel

This skill provides the automated setup for a local-only administration interface. It is purposefully isolated from the `fulcra-dashboard` visualizer for strict security separation, ensuring that read/write liabilities (such as agent chat and file exploration) cannot be accidentally published to the web.

## Strictly Local First

**CRITICAL SECURITY DECREE:** This control panel **must NEVER** be published to the public internet or served via Surge, GitHub Pages, or Vercel. It is a strictly local administrative tool that binds to `localhost` and requires a persistent Python backend to function. It has access to sensitive files and has the power to send commands to the agent.

## Usage

When a user requests to "set up the control panel" or "enable the chat envoy" for their Fulcra setup, execute the scaffolding script.

```bash
# Run the setup script to scaffold the Control Panel
./scripts/setup-control-panel.sh <target-directory>
```

If no `<target-directory>` is provided, it defaults to creating a `fulcra-control-panel` folder in the current working directory.

## Workflow

1. **Scaffold:** The script copies a clean, styled Alpine.js administration panel into the target directory, alongside the robust Python `server.py` backend.
2. **Theming:**
   - **Discover Vibe:** Ask the user what kind of administrative interface they prefer (e.g., a high-tech starship bridge, a retro command-line terminal, a cozy oak-paneled study).
   - **Original Art:** Generate one piece of highly creative thematic art using the `image_generate` tool and use it as the header hero image.
   - **CSS and HTML Adaptation:** Update `theme.css` and `index.html` to reflect the chosen theme. Adjust colors, labels (e.g., rename "Relay" and "File Store" if appropriate), and fonts. Maintain the Bento Grid layout to ensure responsive structural integrity.
3. **Run the Backend:**
   - Start the local Python server to boot the control plane:
     ```bash
     cd <target-directory>
     python3 server.py 8080 > dev.log 2>&1 &
     ```
   - Provide the user with the `http://localhost:8080` link.
4. **Connect the Chat Envoy (Agent Loop):**
   - The Control Panel has a built-in Chat Envoy that relies on you (the agent) checking for new messages.
   - The Python server exposes `GET /api/chat/unread` which returns the latest user commands from the chat window.
   - Set up a background `bash` script using the `exec` tool (or propose an OpenClaw native `cron` heartbeat based on the user's token preference) that loops and checks `http://localhost:8080/api/chat/unread`.
   - When new messages appear in the JSON payload, the script should invoke OpenClaw via the CLI (`openclaw agent --to main --message "ENVOY MESSAGE: <text>"`) to trigger your response, which you will then write back to the `chat.json` log or via standard output routing.
