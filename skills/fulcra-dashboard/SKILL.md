---
name: fulcra-dashboard
description: "Builds a highly customizable, interactive HTML dashboard using Alpine.js, modern Vanilla CSS, and a Python backend to display private data from the user's Fulcra data store locally. Includes workflows to export a specific, previewable directory for public sharing."
homepage: "https://github.com/fulcradynamics/agent-skills"
license: "MIT"
user-invocable: true
metadata: { "openclaw": { "emoji": "📊" } }
---

# Fulcra Dashboard

This skill provides the automated setup for a lightweight, build-less web dashboard. It relies entirely on **Alpine.js** for state management and **Vanilla CSS** for styling. It eschews complex frameworks (like SvelteKit) and utility-class libraries in favor of a "Single-Scroll Artifact" or a "Static Triad".

## View Locally or Publish Publicly

This dashboard is designed to present the user's Fulcra data, which can be viewed locally or published publicly. By default, it runs on localhost using a simple Python static server. Please note that the dashboard includes and relies on scripts fetched from public CDNs (such as Alpine.js, D3.js, Plotly, etc.) for visualizing and presenting the data.

Important: The local working application root must never be published to the public internet directly, as it often contains intermediate files and full datasets. If the user wishes to share a dashboard, you must deploy only the isolated `public/` directory that contains only the specific data and files intended for publication.

## Architecture Decrees

When constructing this dashboard, you **must** follow these strict architectural rules to prevent the file from becoming a tangled, unmaintainable monolith:

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

## Adding Advanced Visualizations

When the user requests more complex or varied visualizations, you have two primary avenues:

### 1. Frontend: Multi-Dimensional & Interactive Charts (D3.js, Plotly, etc.)
The default template includes basic charts, but the "Static Triad" architecture gracefully supports highly advanced, multi-dimensional visualizations—including interactive 3D WebGL scenes—without ever needing a build step.
- **Workflow:** Include the required CDN library (e.g., `d3.js`, `plotly.js`, `d3-cloud`) in `index.html`. Add a new rendering method inside the `Alpine.data()` block (or the script tag) to bind the `.jsonl` timeline data to the DOM.
- **Supported Paradigms & Chart Types:** You can expand the dashboard with various chart types tailored to the user's data. **Do not restrict yourself to these examples; you are encouraged to pull in any chart type or lightweight CDN library that best fits the specific data.** Examples include:
  - **Temporal & Milestones:** Implement Timeline or Gantt charts using D3 or Plotly to visualize spans of time, project milestones, or overlapping events.
  - **Textual & Frequency:** Use Word Clouds (via `d3-cloud` or similar lightweight libraries) or Tag Clouds to show the frequency of text terms, keywords, or activity logs natively in the browser.
  - **Progress & Completion:** Build Gauges, Progress Bars, or Burn-down charts to track completion status, quotas, or project progression against a defined goal.
  - **Advanced Correlations:** Heatmaps for daily frequency, 2D D3 scatter plots, or fully interactive 3D WebGL scatter plots (e.g., mapping Sleep on X, Focus on Y, and Steps on Z) to explore complex relationships.
- **Styling Integration:** Ensure advanced charting libraries blend seamlessly with the user's chosen theme. Explicitly configure library backgrounds and grid lines to be `transparent` or translucent so the CSS glassmorphism, gradients, and custom themes shine through. Increase container dimensions (e.g., `.chart-tall { height: 400px; }`) to give 3D scenes enough physical space to be comfortably rotated by the user.
- **Constraint:** Keep the rendering code clean and modular. Isolate chart rendering functions so they can be easily re-rendered on window resize or data updates.

### 2. Backend: Python-Generated Visualizations
For highly complex, compute-intensive, or specialized visual outputs (like word clouds, network graphs, or composite rasterized images), leverage the Python backend.
- **Workflow:** Modify `server.py` (or create a secondary Python worker script) to read the local Fulcra `.jsonl` data, process it using libraries like `matplotlib`, `seaborn`, or `networkx`, and output a static image (e.g., `.png`, `.svg`) or pre-calculated JSON structure into the dashboard directory.
- **Integration:** Update `index.html` to reference the generated image (e.g., `<img src="/generated-network.png">`) or have the Alpine state fetch the advanced JSON artifact.
- **Constraint:** Ensure the Python generation step can be run independently or triggered reliably, so the dashboard always reflects the latest data without breaking the simple local server paradigm.

## Usage

When a user requests to "set up the web app" or "create a dashboard for the Fulcra skills" (or if they are transitioning from the `fulcradynamics/agent-skills/fulcra-onboarding` skill), you should execute the setup script provided by this skill. 

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
   - Run `uv tool run fulcra-api catalog` to discover available data. Note: Prioritize user-configured data over passive metrics (like step count). Explicitly filter for items where `categories` includes `"user_configured"`, or where the `id` follows the format `*Annotation/<UUID>` (e.g., `ScaleAnnotation/1234-abcd...`).
   - Fetch records for the user's custom annotations (e.g., `uv tool run fulcra-api get-records "ScaleAnnotation/<UUID>" "30 days" > timeline_name.jsonl`).
   - **Agent Visibility Package:** If the user previously enabled the Universal Agent Visibility Package (or if you see "Agent Tasks Completed" and "Current Agent Work" in their catalog), you must fetch these agent annotations as well and explicitly include them in the `data.json` timelines array so your background work is visualized alongside their personal data.
   - **Data Updates:** You must run the `data-updates` CLI command for the timeline (e.g., `uv tool run fulcra-api data-updates "30 days" > data_updates.json`), explicitly move it to `public/data_updates.json`, and link it as `"recordsProcessed": "data_updates.json"` in your config to populate the "Your data" chart. Do not skip this step.
   - Keep the raw dumps in the root directory, and move ONLY the approved, final `.jsonl` and `.json` files to the `public/` directory so the frontend can read them.
   - The `public/data.json` config file acts as a manifest. It should map your layout to the `.jsonl` files in the `public/` directory, and you **must** include the annotation `description` in the timeline block, like this: `{"summary": "An entertaining, thematic overview of the current data...", "timelines": [{"id": "...", "title": "...", "description": "The description from the catalog...", "icon": "...", "color": "...", "data": "timeline_name.jsonl"}], "recordsProcessed": "records_processed.jsonl"}`. **Crucial:** For the `"summary"` field, you must read the downloaded `.jsonl` data and write an interesting, entertaining, and highly thematic text summary of the actual real-world activity. Adopt the persona of the dashboard's theme (e.g., an observatory log, a captain's entry, a baker's notes) to make the data narrative fun and engaging. Do not write boring meta-descriptions or dry analytical text.
   - You do not need to write an aggregation script; the dashboard will automatically parse `.jsonl` files and aggregate records for the charts natively on `init()`.
3. **Theming & Visualization:**
   - **Theme Discovery:** Ask the user what "theme" or "vibe" they want (e.g., minimalist dark mode, cyberpunk, a retro diner, a space station, a cozy bakery). 
   - **Embrace the Theme (HTML & Copy):** Do not leave default boilerplate intact! Modify `index.html` directly to rewrite the main title, subtitle, and all component headers to fit the theme (e.g., change "Fulcra Dashboard" to "The Cybernetic Core" and "Records Processed" to "Baguettes Baked"). Replace all default emojis (like 📊 or 🛰️) with theme-appropriate icons.
   - **Preserve the Layout Container:** The base HTML and CSS files use a `.layout-container` for spacing. Keep this structure intact. Limit your CSS edits to colors (by updating the root variables), fonts, borders, box-shadows, and backgrounds.
   - **Original Art (Required):** Generate one piece of highly creative thematic art using the `image_generate` tool. Save it to the folder and reference it via an `<img>` tag in the dashboard header. **Style Directive:** The image must be extremely high-quality and perfectly cohesive with the user's chosen theme. Whether the vibe calls for retro 2D pixel art, a minimalist vector illustration, or a sleek 3D render, ensure the specific art style, color palette, and lighting strictly match the CSS variables and overall aesthetic you are building.
   - **Hero Image Prominence & Legibility:** Ensure the generated thematic art does not get lost behind the dashboard title. Instead of blindly overlaying text across the entire image, use creative layouts like a split-panel hero (text on one side, unobstructed art on the other), a bento-style hero block, or a targeted gradient mask that leaves the primary subject of the art perfectly visible. Keep the overall header compact enough (e.g., `min-height: 250px` to `350px`) so the core telemetry data remains visible "above the fold."
   - **Dynamic Animated Elements:** Do not settle for a simple moving dot or static icon. Create highly engaging, fun, and thematic animations. You are encouraged to pull in lightweight CDN libraries (e.g., `tsparticles` for rich particle systems like starfields or embers) or author complex, multi-layered CSS/SVG animations that genuinely delight the user.
4. **Git Repository Initialization:**
   - Once scaffolded, **you must prompt the user to initialize a git repository**.
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
   - **The built-in `public` directory:** Because the dashboard is already structured with a `public/` directory that only contains the UI and explicitly copied data files, you do not need to create a new folder from scratch.
     1. Ask the user to verify in the local preview that the data shown is exactly what they want to share.
     2. Ensure that `public/` contains *only* the specific data files needed by the frontend, and that any raw data dumps, `dev.log`, or python scripts remain safely outside it in the root directory.
   - **Crucial Warning & Confirmation:** Directly at the point of publishing (before running any deployment tools), you must present a clear warning to the user. State exactly which data files are inside the `public/` directory and will be made public, and explicitly ask for their final confirmation to proceed with the deployment.
   - Wait for their explicit confirmation before proceeding.
   - If they agree, offer them three deployment options, ordered by ease of use:
     - **Option 1: Surge (Easiest, No Git Required)**
       - Installation: `npm install -g surge`
       - Deployment: Run `surge` inside the `public/` directory.
       - UX: The user will be prompted in the terminal for an email/password to create a free account on the fly, and then an auto-generated domain will be provided. Instantly deploys the folder.
     - **Option 2: GitHub Pages (Best for Version Control)**
       - Installation: Ensure `gh` (GitHub CLI) is installed and authenticated (`gh auth status`).
       - Deployment: Navigate into the `public/` directory, initialize git, create the repository, and push (`git init && git add . && git commit -m "Initial public export" && gh repo create <name> --public --source=. --remote=origin --push`).
       - Enable Pages: `gh api repos/{owner}/{repo}/pages -X POST -f "source[branch]=main" -f "source[path]=/"`.
       - UX: Creates a standard GitHub repository and publishes to `https://<username>.github.io/<repo>/`.
     - **Option 3: Vercel (No Git Required, Professional Hosting)**
       - Installation: `npm i -g vercel`
       - Deployment: Run `vercel deploy --prod` inside the `public/` directory.
       - UX: Opens a browser for authentication if needed, then asks a few interactive setup questions in the terminal before uploading the folder directly to Vercel's edge network.
   - Execute the chosen deployment path and provide the user with the final public URL.
7. **Handoff & Next Steps:**
   - Once the user has seen the live local dashboard, do not just stop. Outline possible next directions to keep the momentum going:
     - **Enrich the Data:** Pull in passive data from the Fulcra Context app (e.g., location, heart rate) or ingest data from other external sources to correlate with their custom annotations.
     - **Advanced Visualizations:** Build more complex D3.js charts or specific data rollups.
     - **Python Data Analysis:** Set up scripts on the Python backend (`server.py`) to analyze their data before sending it to the frontend.
