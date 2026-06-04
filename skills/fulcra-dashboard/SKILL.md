---
name: fulcra-dashboard
description: "Builds a highly customizable, single-file HTML dashboard using Alpine.js and modern Vanilla CSS to visualize Fulcra data. Use this skill when the user wants a graphical web dashboard instead of ASCII charts to view their compiled Fulcra insights."
homepage: "https://github.com/fulcradynamics/agent-skills"
license: "MIT"
user-invocable: true
metadata: { "openclaw": { "emoji": "📊" } }
---

# Fulcra Dashboard

This skill provides the automated setup for a lightweight, build-less web dashboard. It relies entirely on **Alpine.js** for state management and **Vanilla CSS** for styling. It eschews complex frameworks (like SvelteKit) and utility-class libraries in favor of a "Single-Scroll Artifact" or a "Static Triad" that is instantly deployable to simple hosts like GitHub Pages without any build tools or Content Security Policy conflicts.

## Architecture Decrees

When constructing this dashboard, you **MUST** follow these strict architectural rules to prevent the file from becoming a tangled, unmaintainable monolith:

1. **Monumental Landmarks (Banner Comments):** Divide the HTML file into distinct provinces using highly visible comments. This ensures you (the agent) can navigate and edit surgical blocks safely.
   ```html
   <!-- ========================================== -->
   <!-- 🏛️ PROVINCE: DASHBOARD LAYOUT & UI         -->
   <!-- ========================================== -->
   <main> ... </main>

   <!-- ========================================== -->
   <!-- 🧠 PROVINCE: ALPINE.JS STATE & LOGIC       -->
   <!-- ========================================== -->
   <script> ... </script>

   <!-- ========================================== -->
   <!-- 🎨 PROVINCE: D3.js VISUALIZATIONS          -->
   <!-- ========================================== -->
   <script> ... </script>
   ```

2. **The Separation of Domains:** Do not write massive inline Alpine logic (e.g., `x-data="{ huge object }"`). You must use `Alpine.data()` within the "Alpine.js State & Logic" province to extract the logic into a clean script block. The HTML should only contain the bindings (`x-data="dashboard()"`, `x-text`, `x-show`, etc.).

3. **The Static Triad (Escape Hatch):** While a single `index.html` is preferred, if the dashboard grows too vast, you may split it into three files:
   - `index.html` (Structure & Semantic HTML)
   - `app.js` (Alpine `Alpine.data()` and D3 functions)
   - `styles.css` (Custom overriding aesthetics)
   No build step is allowed.

## Usage

When a user requests to "set up the web app" or "create a dashboard for the Fulcra skills" (or if they are transitioning from the `fulcra-onboarding` skill), you should execute the setup script provided by this skill. 

```bash
# Run the setup script to scaffold the Alpine dashboard
./scripts/setup-dashboard.sh <target-directory>
```

If no `<target-directory>` is provided, it defaults to creating a `fulcra-dashboard` folder in the current working directory.

## Workflow

**Contextual Awareness (Standalone vs. Post-Onboarding):** 
Do not assume this skill is always run immediately after `fulcra-onboarding`. 
- **If transitioning from Onboarding:** The user has likely just seen a static HTML preview of their data. Acknowledge this transition and frame this step as *building out* and *upgrading* their existing preview into a live, interactive web app. Leverage the context of the annotations they just built, skip redundant discovery, and carry over their preferred theme.
- **If running Standalone:** You must first discover what data the user wants to visualize (run `uv tool run fulcra-api catalog` to check for user annotations and discuss options before proceeding).

1. **Scaffold:** The script copies a clean, un-styled Alpine.js dashboard template into the target directory.
2. **Data Ingestion (Requires Consent):** Automatically fetch the user's relevant Fulcra data using the `fulcra-api` CLI. 
   - **Important:** Always ask the user for permission to query the Fulcra API to build the dashboard before fetching records.
   - Run `uv tool run fulcra-api catalog` to discover available data. **CRITICAL:** Prioritize user-configured data over passive metrics (like step count). Explicitly filter for items where `categories` includes `"user_configured"`, or where the `id` follows the format `*Annotation/<UUID>` (e.g., `ScaleAnnotation/1234-abcd...`).
   - Fetch records for the user's custom annotations (e.g., `uv tool run fulcra-api get-records "ScaleAnnotation/<UUID>" "30 days" > timeline_name.jsonl`).
   - **Agent Visibility Package:** If the user previously enabled the Universal Agent Visibility Package (or if you see "Agent Tasks Completed" and "Current Agent Work" in their catalog), you MUST fetch these agent annotations as well and explicitly include them in the `data.json` timelines array so your background work is visualized alongside their personal data.
   - **Records Processed:** You MUST fetch the `RecordsProcessed` metric for the timeline (e.g., `uv tool run fulcra-api get-records "RecordsProcessed" "30 days" > records_processed.jsonl`) to populate the Data Velocity chart. Do not skip this step or set it to null.
   - Keep the files as raw JSONL in the dashboard directory.
   - **Agent Memory Dashboard Status:** Automatically check if the user has agent backup files stored in Fulcra. Run `uv tool run fulcra-api file list "agent/<lowercase-agent-name>/memory/"` to check for `memory.gz` or `top_of_mind.md`. The dashboard template natively includes an "Agent Vault" module. You must update the `href` paths in this module to use your actual agent name (e.g., replacing `agent/treecle/memory/memory.gz` with `agent/your_name_here/memory/memory.gz`), and you can optionally update the modified dates if you fetched them.
   - The `data.json` config file acts as a manifest. It should map your layout to the `.jsonl` files you downloaded, and you **must** include the annotation `description` in the timeline block, like this: `{"summary": "A concise overview of the current data and recent activity...", "timelines": [{"id": "...", "title": "...", "description": "The description from the catalog...", "icon": "...", "color": "...", "data": "timeline_name.jsonl"}], "recordsProcessed": "records_processed.jsonl"}`. **Crucial:** For the `"summary"` field, you MUST read the downloaded `.jsonl` data and write a short, personalized text summary of the actual real-world activity shown in the data (e.g., "You've been consistently tracking your mood, with a slight dip this week"). Do not write meta-descriptions like "This is a retro dashboard."
   - You do not need to write an aggregation script; the dashboard will automatically parse `.jsonl` files and aggregate records for the charts natively on `init()`.
3. **Theming & Visualization:**
   - **Theme Discovery:** Ask the user what "theme" or "vibe" they want (e.g., minimalist dark mode, cyberpunk, a retro diner, a space station, a cozy bakery). 
   - **Embrace the Theme (HTML & Copy):** Do not leave default boilerplate intact! Modify `index.html` directly to rewrite the main title, subtitle, and all component headers to fit the theme (e.g., change "Fulcra Dashboard" to "The Cybernetic Core", "Records Processed" to "Baguettes Baked", and "Relay" to something thematically appropriate for the chat interface like "The Oracle's Ear" or "Comms Link"). Replace all default emojis (like 📊 or 🛰️) with theme-appropriate icons.
   - **Preserve the Bento Layout (CRITICAL):** The base HTML and CSS files use a `.dashboard-bento-grid` layout that features a sticky left column and a flexible right column. **Do not rewrite or remove the core structural HTML** (e.g. `.layout-container`, `.dashboard-bento-grid`, `.bento-col-left`, `.bento-col-right`). When you edit the CSS, you must leave the structural grid properties (`grid-template-columns`, `sticky` positioning, `flex` directions) intact to prevent breaking the layout. Limit your CSS edits to colors (by updating the root variables), fonts, borders, box-shadows, and backgrounds.
   - **Original Art (Required):** Generate one piece of highly creative thematic art using the `image_generate` tool. Save it to the folder and reference it via an `<img>` tag in the dashboard header. **Style Directive:** The image must be extremely high-quality and perfectly cohesive with the user's chosen theme. Whether the vibe calls for retro 2D pixel art, a minimalist vector illustration, or a sleek 3D render, ensure the specific art style, color palette, and lighting strictly match the CSS variables and overall aesthetic you are building.
   - **Hero Text Legibility & Scale:** When styling the hero header, ensure the text overlaid on the image is highly legible. Adapt the technique to fit the theme (e.g., use a frosted glass `backdrop-filter: blur()` block for tech/modern themes, an ambient `radial-gradient` vignette for dark/moody themes). Additionally, the hero must not dominate the viewport. Keep it compact (e.g., `min-height: 250px`) so the core telemetry data is visible "above the fold."
   - **Dynamic Animated Elements:** Inject at least one CSS animation (using standard CSS `@keyframes` in `theme.css`) that fits the theme (e.g., a floating asteroid, a blinking cursor, a buzzing fly) and attach it to the `.animation-layer` or other suitable elements.
4. **Git Repository Initialization:**
   - Once scaffolded, **you MUST prompt the user to initialize a git repository**.
   - Check if `git` is installed. Suggest 1 or 2 fun repository names based on their theme.
   - Initialize locally (`git init && git add . && git commit -m "Initial commit"`). *Do not push to GitHub yet.*
5. **Run & Verify:**
   - Start the local Python server to preview the dashboard:
     ```bash
     cd <target-directory>
     python3 server.py 8081 > dev.log 2>&1 &
     ```
   - Provide the user with the localhost link.
6. **Chat Envoy & GitHub Deployment:** 
   - The dashboard includes a chat envoy component (default title "Relay"). Remind the user that this envoy only functions locally via the Python server.
   - If the user pushes the repository to GitHub Pages, the CSS is designed to automatically hide the envoy to prevent user confusion, as the chat interface cannot route messages to the local Python bridge from a remote host.
   - **GitHub Pages Offer:** Explicitly ask if they would like to publish this dashboard live to the internet using GitHub Pages so they can view it anywhere.
   - If they agree, ensure the `gh` (GitHub CLI) is installed and authenticated (`gh auth status`). If it is not, provide instructions or execute the installation (`brew install gh` or equivalent) and wait for the user to complete `gh auth login`.
   - Once authenticated, create the repository and push the code (`gh repo create <name> --public --source=. --remote=origin --push`).
   - *Crucially*, after pushing, execute the command to enable GitHub pages for the repository from the main branch: `gh api repos/{owner}/{repo}/pages -X POST -f "source[branch]=main" -f "source[path]=/"`.
   - Provide the user with the final public `https://<username>.github.io/<repo>/` URL.
7. **Handoff & Next Steps:**
   - Once the user has seen the live local dashboard, do not just stop. Outline possible next directions to keep the momentum going:
     - **Enrich the Data:** Pull in passive data from the Fulcra Context app (e.g., location, heart rate) or ingest data from other external sources to correlate with their custom annotations.
     - **Connect the Chat Envoy:** Work on wiring up the Chat Envoy so they can chat with you directly from within the dashboard itself.
     - **Advanced Visualizations:** Build more complex D3.js charts or specific data rollups.
     - **Python Data Analysis:** Set up scripts on the Python backend (`server.py`) to analyze their data before sending it to the frontend.

## Advanced Modifications

**Connecting the Chat Envoy:**
If the user asks you to "connect the chat envoy" (as prompted by the default placeholder error message in the dashboard), you must edit `server.py` to route messages back to your main OpenClaw session.
1. Modify `server.py` to use a persistent `chat.json` file rather than an in-memory `chat_history` list.
2. In the `do_POST` handler for `/api/chat`, instead of appending a simulated reply, use Python's `subprocess` module to trigger an OpenClaw background command that targets the main session:
   ```python
   import subprocess
   # ... inside do_POST after saving the user's message to chat.json ...
   prompt = f'A new user message was posted in the Fulcra dashboard chat: "{user_msg}". Read the local chat.json file in this directory to get full context. Respond to the user\'s latest message, and append your response to the chat.json file as role \\\'assistant\\\' with a timestamp. Do not modify the history. Reply with a short summary when done.'
   
   # We use subprocess.Popen without shell=True to avoid bash quoting nightmares
   subprocess.Popen(["openclaw", "agent", "--to", "main", "--message", prompt])
   ```
3. After the python server is restarted, the chat envoy will successfully pipe messages from the web dashboard directly into your OpenClaw session!
