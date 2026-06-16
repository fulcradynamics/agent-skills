---
name: fulcra-dashboard
description: "Builds a highly customizable, interactive HTML dashboard using Alpine.js, modern Vanilla CSS, and a Python backend to display private data from the user's Fulcra data store locally. Includes workflows to securely export a sanitized, non-interactive version for public sharing."
homepage: "https://github.com/fulcradynamics/agent-skills"
license: "MIT"
user-invocable: true
metadata: { "openclaw": { "emoji": "📊" } }
---

# Fulcra Dashboard

This skill provides the automated setup for a lightweight, build-less web dashboard. It relies entirely on **Alpine.js** for state management and **Vanilla CSS** for styling. It eschews complex frameworks (like SvelteKit) and utility-class libraries in favor of a "Single-Scroll Artifact" or a "Static Triad".

## Local First & Secure Exports

This dashboard is designed fundamentally as a **local, private interface**. By default, it runs on localhost using a Python server, granting it safe access to the user's private data, local agent memory (`memory.gz`), and enabling interactive features like a Chat Envoy that triggers local agent shell commands, as well as a local-only File Browser for exploring the Fulcra file store.

**Crucially:** The local application and its sensitive capabilities must NEVER be published to the public internet directly. If the user wishes to share a dashboard, you must generate a separate, sanitized **export** that strips out the Python backend, interactive agent features, and unapproved private data.

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
6. **Public Publication (Requires Consent & Preview):**
   - The user may wish to publish a version of their dashboard to the public internet.
   - **MANDATORY ISOLATION & SCRATCH BUILD:** The local dashboard is private. You MUST NOT copy the local dashboard files to the public internet. Instead, you must build the public dashboard from scratch as a separate entity:
     1. Ask the user explicitly which specific data timelines and metrics they want to make public.
     2. Create a separate `public-export` directory.
     3. Scaffold a fresh HTML structure into `public-export` by copying the necessary components from the `template-dashboard` directory. **CRITICAL:** Do NOT include the Chat Envoy or the File Browser in the public HTML structure. The public dashboard must be strictly read-only.
     4. Copy ONLY the explicitly approved data files (e.g., specific `.jsonl` files) into `public-export`, and create a new, sanitized `data.json` referencing only those files. Copy over the `app.js`, `theme.css`, and required images, ensuring they do not contain sensitive local state.
     5. Start a new local server on a different port (e.g., 8082) serving ONLY the `public-export` directory.
     6. Provide the user with this new localhost link and explicitly ask them to verify that the data shown is safe for public consumption.
   - Wait for their explicit confirmation before proceeding.
   - If they agree, offer them three deployment options, ordered by ease of use:
     - **Option 1: Surge (Easiest, No Git Required)**
       - Installation: `npm install -g surge`
       - Deployment: Run `surge` inside the `public-export` directory.
       - UX: The user will be prompted in the terminal for an email/password to create a free account on the fly, and then an auto-generated domain will be provided. Instantly deploys the folder.
     - **Option 2: GitHub Pages (Best for Version Control)**
       - Installation: Ensure `gh` (GitHub CLI) is installed and authenticated (`gh auth status`).
       - Deployment: Navigate into the `public-export` directory, initialize git, create the repository, and push (`git init && git add . && git commit -m "Initial public export" && gh repo create <name> --public --source=. --remote=origin --push`).
       - Enable Pages: `gh api repos/{owner}/{repo}/pages -X POST -f "source[branch]=main" -f "source[path]=/"`.
       - UX: Creates a standard GitHub repository and publishes to `https://<username>.github.io/<repo>/`.
     - **Option 3: Vercel (No Git Required, Professional Hosting)**
       - Installation: `npm i -g vercel`
       - Deployment: Run `vercel deploy --prod` inside the `public-export` directory.
       - UX: Opens a browser for authentication if needed, then asks a few interactive setup questions in the terminal before uploading the folder directly to Vercel's edge network.
   - Execute the chosen deployment path and provide the user with the final public URL.
7. **Handoff & Next Steps:**
   - Once the user has seen the live local dashboard, do not just stop. Outline possible next directions to keep the momentum going:
     - **Enrich the Data:** Pull in passive data from the Fulcra Context app (e.g., location, heart rate) or ingest data from other external sources to correlate with their custom annotations.
     - **Connect the Chat Envoy:** Work on wiring up the Chat Envoy so they can chat with you directly from within the dashboard itself.
     - **Advanced Visualizations:** Build more complex D3.js charts or specific data rollups.
     - **Python Data Analysis:** Set up scripts on the Python backend (`server.py`) to analyze their data before sending it to the frontend.

## Advanced Modifications

**Connecting the Chat Envoy:**
If the user asks you to "connect the chat envoy" (as prompted by the default placeholder error message in the dashboard), you must edit `server.py` to route messages and set up a polling mechanism.

**🚨 SECURITY CONSIDERATION:** We avoid having the web server execute shell commands directly (like triggering OpenClaw via subprocess) to prevent security audit flags and reduce RCE risks. Instead, the backend acts as a passive queue, and the agent polls it.

1. Modify `server.py` to use a persistent `chat.json` file rather than an in-memory `chat_history` list.
2. Update the `do_POST` handler for `/api/chat` to simply record the new user message into `chat.json` and mark it as "unread".
3. Add a new endpoint to `server.py` (e.g., `GET /api/chat/unread`) that returns any unread messages from `chat.json` and simultaneously marks them as read.
4. Set up a polling mechanism (e.g., a background bash script or an OpenClaw native cron job, pending user approval) that checks the `/api/chat/unread` endpoint periodically.
   - *Note on token usage:* If using OpenClaw's native `cron` tool, the model is invoked every time the cron triggers. To avoid burning tokens every 5 seconds, either use a longer interval (e.g., checking via `HEARTBEAT.md` every 30 minutes) or write an external bash script that loops every 5 seconds, checks the endpoint via `curl`, and ONLY invokes the agent via `openclaw agent --to main --message ...` when unread messages are found. Discuss these tradeoffs with the user before setting up the schedule.
5. When the agent receives an unread message, it should read the local `chat.json` file for context, respond to the user's latest message, and append the response to `chat.json` as role 'assistant' with a timestamp.
