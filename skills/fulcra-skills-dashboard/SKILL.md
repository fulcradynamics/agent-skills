---
name: fulcra-skills-dashboard
description: "Scaffolds and sets up a customizable SvelteKit web application designed to visualize Fulcra data. Use this skill when the user wants a graphical web dashboard instead of ASCII charts to view their compiled Fulcra insights."
homepage: "https://github.com/fulcradynamics/agent-skills"
license: "MIT"
user-invocable: true
metadata: { "openclaw": { "emoji": "📊" } }
---

# Fulcra Skills Dashboard

This skill provides the automated setup for a SvelteKit-based dashboard. It is designed to act as a highly customizable graphical UI for the user's Fulcra data.

## Usage

When a user requests to "set up the Svelte web app" or "create a dashboard for the Fulcra skills", you should execute the setup script provided by this skill. 

```bash
# Run the setup script to scaffold the SvelteKit app
./scripts/setup-dashboard.sh <target-directory>
```

If no `<target-directory>` is provided, it defaults to creating a `fulcra-dashboard` folder in the current working directory.

## Post-Scaffold: Git Repository Initialization

As part of this skill, after the dashboard is scaffolded, **you MUST prompt the user to initialize a git repository** for the new project.

1. First, check if `git` is installed (`git --version`). If it is not installed, skip repository creation entirely.
2. If `git` is installed, suggest 1 or 2 fun but appropriate repository names (e.g., `fulcra-data-lens`, `fulcra-observatory`, etc.) and ask the user which name they prefer.
3. Once they choose a name, **always initialize the repository locally first** (`git init && git add . && git commit -m "Initial commit"`). *Note: During testing or onboarding flows, you can stop here and just keep it local. Do not push to GitHub during the initial onboarding flow unless explicitly requested.*
4. If not in an onboarding flow, ask if they would like to push this to GitHub. If so, check if they are authenticated (`gh auth status`) and use `gh repo create <name> --private --source . --remote origin --push`. Always default to private unless specifically asked otherwise.

## Workflow

1. **Scaffold:** The script copies a clean, un-styled SvelteKit dashboard template (which includes the OpenClaw Control UI embed and D3 timeline components) and installs dependencies.
2. **Theming (Agent Task):** Because the scaffolded dashboard is deliberately un-styled, you must heavily stylize it based on the user's preference. 
   - **Theme Discovery:** If the user already established a theme in a previous step (e.g., during the `fulcra-onboarding` HTML dashboard generation), you must automatically carry over that exact theme, aesthetic, and visual language to this new SvelteKit dashboard. If no previous theme exists, immediately ask the user what "theme" or "vibe" they want (e.g., minimalist dark mode, cyberpunk, a retro diner, a space station). 
   - **Apply the Theme:** Directly edit the components in `src/routes/` to apply CSS that matches the requested theme:
     - `ThemeStyles.svelte` (Global backgrounds and typography)
     - `HeroHeader.svelte` (Titles, banners, and hero art injection)
     - `DashboardGrid.svelte` (Card containers and layout)
       - **Chart Title Art:** You must inject themed emojis, SVG icons, or small generated art assets into the `<h2>` tags for each chart in `DashboardGrid.svelte` (e.g., `<h2>🦖 Agent Victories</h2>` or `<h2><img src={customIcon} class="inline-icon"/> Records Processed</h2>`) to give each section more visual personality.
     - `AgentChat.svelte` (The floating chat window)
     - `D3Timeline.svelte` (Chart specific styling and custom icons)
       - **Crucial Icon Theming:** The `D3Timeline.svelte` component has a `getIcon(d)` function that defaults to returning generic emojis (e.g., '📝', '💾'). You must modify this function to return theme-appropriate emojis or SVGs that match the user's requested vibe (e.g., if the theme is "Subterranean Garden", it should return '🐉', '🐢', '🐕', etc., instead of the default icons).
   - **Original Art (Required):** You must provide one piece of highly creative thematic art for the dashboard (e.g., a mascot, a landscape, a retro poster) and inject it into the dashboard layout. You have two options:
     1. **Generate it:** Use the `image_generate` tool, save it to `src/lib/assets/`, and import it into `HeroHeader.svelte` (e.g., `import heroImg from '$lib/assets/hero.png';` in the `<script>` block, then `<img src={heroImg} />`). Do not use string-based `onerror` handlers in SvelteKit 5 (e.g., avoid `onerror="this.style.display='none'"`).
     2. **Web Fallback:** If image generation fails or takes too long, simply find a highly relevant image URL from the web and use that URL directly in the `src` attribute. 
     Ensure the art is placed off to the side (or in a non-obtrusive corner) so it adds massive personality without interfering with the data visualizations. 
   - **Go all out:** Honor the user's theme to the max. Use CSS or additional generated images to create background textures and decorative UI elements. *Also, don't forget to update the favicon in `src/lib/assets/favicon.svg` to something that matches the user's theme!*
   - **Dynamic Animated Elements:** The dashboard must have at least one highly visible, themed animated element near the top of `HeroHeader.svelte` to bring the scene to life. This shouldn't just be a subtle text glow—it should be a tangible animated entity. For example, if the theme is a primordial swamp, create a CSS-animated `<div>` containing a bug (🦟) that flies erratically across the header, or a creature that peeks out from the side. If it's a spaceship, create a radar sweep or blinking control panel element. **Crucial Safety:** Keep all animations strictly within the `<style>` blocks using standard CSS `@keyframes`. Do not use JS-based animation libraries or string-based DOM manipulation, as this will crash the Svelte compiler.
3. **Data Ingestion:** Automatically fetch the user's relevant Fulcra data using the `fulcra-api` CLI. 
   - **Discover Annotations:** Silently run `uv tool run fulcra-api catalog` to check for any user-created annotations. Annotation data types will be identified by the pattern `*Annotation/${ANNOTATION_ID}` (e.g., `Annotation/00000000-0000-0000-0000-000000000000`).
   - **Fetch Total Data Processed:** Use `uv tool run fulcra-api get-records RecordsProcessed "30 days"` (or an appropriate time range) to fetch the user's overarching data ingestion stats. You must include a chart in the dashboard that visualizes this `RecordsProcessed` data. **Crucial:** Do not just show a single total line. The chart must break down the volume by the type of record, and the UI should display the earliest and latest dates for the data fetched to give a sense of scale and timeline.
   - **Crucial JSON Array Formatting:** The `fulcra-api get-records` command outputs JSONL (JSON Lines), not a single JSON array. You *must* convert this output into a valid JSON array before saving it to `src/lib/data/` so that it can be imported cleanly by SvelteKit. (e.g., `cat output.jsonl | jq -s '.' > output.json`).
   - **Crucial Type Mapping:** When mapping the raw `recordsProcessed` JSON data in your Svelte component for the `D3BarChart`, you *must* map the `fulcra_data_type` field to `type` so the chart can group the data properly (e.g., `type: record.fulcra_data_type`).
   - If the user has custom Annotations (either from the `fulcra-onboarding` flow or found via the catalog check), you must *also* fetch and display the data for those specific annotations.
   - Inject this data strictly into the dashboard's `src/lib/data/` folder and load it dynamically in the Svelte components. Do not hardcode user data directly into the `.svelte` source code files.
4. **Run & Verify:** Start the dev server and explicitly monitor the logs to ensure there are no syntax or compiler errors from your theming edits.
   ```bash
   cd <target-directory>
   npm run dev > dev.log 2>&1 &
   sleep 2 && cat dev.log
   ```
   - **Crucial Error Recovery:** SvelteKit (`vite dev`) will crash with a 500 error if your CSS/HTML edits in step 2 introduced invalid syntax (e.g., duplicated `</style>` tags, missing brackets). You *must* check the output of `dev.log` immediately after starting the server. If you see Vite/Svelte compiler errors, use your file editing tools to fix the syntax in `src/routes/+page.svelte` or `src/routes/AgentChat.svelte` until `dev.log` shows the server is running cleanly without 500 errors. Only present the dashboard to the user once you confirm it compiles successfully.
   - **Crucial Chat API Scope Approval:** The `AgentChat.svelte` component uses `openclaw sessions send` in the background to send messages from the dashboard to you. Because the dev server runs in your sandbox, it will trigger a pending scope upgrade request the first time it tries to send a message. You must actively monitor `openclaw devices list` for this pending request. When you see it, ask the user for permission in chat, and then execute `openclaw devices approve <request-id>` so the dashboard chat works out of the box.
5. **Next Steps:** At the end of the dashboard setup and theming, ask the user what they want to do next. **Crucial:** Provide your own personalized suggestions for next steps based on your knowledge of the user (e.g., specific annotations to track, other data streams to visualize, or goals they are working towards). You can also suggest:
   - Starting to upload data from the agent as a new annotation or file upload.
   - Downloading the Context app (see fulcradynamics.com) to get personal data into the Fulcra database. **Important:** Before suggesting the Context app, perform a quick check for step count data in the user's Fulcra account using the CLI (e.g., checking `RecordsProcessed` or querying for step count). If the user already has step count data, assume they have the Context app installed and *do not* suggest downloading it.

## Notes for the Agent

- After running the setup script, you may need to write specific Svelte components (`+page.svelte`) to parse and visualize the specific JSON schemas of the data you fetched.
