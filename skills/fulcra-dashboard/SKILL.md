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

When a user requests to "set up the web app" or "create a dashboard for the Fulcra skills", you should execute the setup script provided by this skill. 

```bash
# Run the setup script to scaffold the Alpine dashboard
./scripts/setup-dashboard.sh <target-directory>
```

If no `<target-directory>` is provided, it defaults to creating a `fulcra-dashboard` folder in the current working directory.

## Workflow

1. **Scaffold:** The script copies a clean, un-styled Alpine.js dashboard template (which includes the HTML, Python server, and external CSS) into the target directory.
2. **Data Ingestion (Requires Consent):** Automatically fetch the user's relevant Fulcra data using the `fulcra-api` CLI. 
   - **Important:** Always ask the user for permission to query the Fulcra API to build the dashboard before fetching records.
   - Run `uv tool run fulcra-api catalog` to check for user annotations.
   - Fetch records (e.g., `uv tool run fulcra-api get-records RecordsProcessed "30 days"`). Remember that `fulcra-api get-records` outputs JSONL. You *must* convert this to a valid JSON array (`cat output.jsonl | jq -s '.' > data.json`).
   - Store the resulting data in a `data.json` file beside the `index.html`, and have your Alpine.js component fetch it on `init()` (e.g., `fetch('data.json').then(...)`).
3. **Theming & Visualization:**
   - **Theme Discovery:** Ask the user what "theme" or "vibe" they want (e.g., minimalist dark mode, cyberpunk, a retro diner, a space station). 
   - **Apply the Theme:** You must edit the `theme.css` file to apply this aesthetic. The HTML structure (`index.html`) is fixed; do not edit it to add utility classes. Apply custom backgrounds, CSS variables, and specific animations directly to the semantic classes within `theme.css` (e.g., `.hero-header`, `.dashboard-title`).
   - **Original Art (Required):** Generate one piece of highly creative thematic art using the `image_generate` tool, save it to the folder, and reference it via an `<img>` tag in the dashboard header/hero section of `index.html`.
   - **Dynamic Animated Elements:** Inject at least one CSS animation (using standard CSS `@keyframes` in `theme.css`) that fits the theme (e.g., a floating asteroid, a blinking cursor, a buzzing fly) and attach it to the `.animation-layer` or other suitable elements.
4. **Git Repository Initialization:**
   - Once scaffolded, **you MUST prompt the user to initialize a git repository**.
   - Check if `git` is installed. Suggest 1 or 2 fun repository names.
   - Initialize locally (`git init && git add . && git commit -m "Initial commit"`). *Do not push to GitHub during the initial onboarding flow unless explicitly requested.*
5. **Run & Verify:**
   - Start the local Python server to preview the dashboard:
     ```bash
     cd <target-directory>
     python3 server.py 8081 > dev.log 2>&1 &
     ```
   - Provide the user with the localhost link.
6. **Chat Envoy & GitHub Deployment:** 
   - The dashboard includes a "Sub-Surface Relay" chat envoy. Remind the user that this envoy only functions locally via the Python server.
   - If the user pushes the repository to GitHub Pages, the CSS is designed to automatically hide the envoy to prevent user confusion, as the chat interface cannot route messages to the local Python bridge from a remote host.
