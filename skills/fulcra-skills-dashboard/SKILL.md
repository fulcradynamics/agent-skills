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
   - **Theme Discovery:** If the user already established a theme in a previous step (e.g., during the `fulcra-onboarding` HTML dashboard generation), you must automatically carry over that exact theme, aesthetic, and visual language to this new SvelteKit dashboard. If no previous theme exists, immediately ask the user what "theme" or "vibe" they want (e.g., minimalist dark mode, cyberpunk, a swamp, a space station). 
   - **Apply the Theme:** Directly edit `src/routes/+page.svelte` and `src/routes/D3Timeline.svelte` to apply CSS that matches the requested theme!
   - **Go all out:** Honor the user's theme to the max. Use the `image_generate` tool to create background textures, decorative UI elements, or thematic hero images and save them to `src/lib/assets/` to include in the dashboard.
   - **Animations:** Inject CSS animations (glows, pulsing borders, scrolling backgrounds, or enter-transitions) to make the dashboard feel alive and highly polished.
3. **Data Ingestion:** Automatically fetch the user's relevant Fulcra data using the `fulcra-api` CLI. 
   - If the user previously set up custom Annotations during the `fulcra-onboarding` flow, you must fetch and display the data for *those* specific annotations instead of generic milestones.
   - Inject this data into the dashboard's `src/lib/data` or `static/data` folder, or directly into the Svelte components.
4. **Run:** Start the dev server.
   ```bash
   cd <target-directory>
   npm run dev
   ```
5. **Next Steps:** At the end of the dashboard setup and theming, ask the user what they want to do next. **Crucial:** Provide your own personalized suggestions for next steps based on your knowledge of the user (e.g., specific annotations to track, other data streams to visualize, or goals they are working towards). You can also suggest:
   - Starting to upload data from the agent as a new annotation or file upload.
   - Downloading the Context app (see fulcradynamics.com) to get personal data into the Fulcra database. **Important:** Before suggesting the Context app, perform a quick check for step count data in the user's Fulcra account using the CLI (e.g., checking `RecordsProcessed` or querying for step count). If the user already has step count data, assume they have the Context app installed and *do not* suggest downloading it.

## Notes for the Agent

- After running the setup script, you may need to write specific Svelte components (`+page.svelte`) to parse and visualize the specific JSON schemas of the data you fetched.
