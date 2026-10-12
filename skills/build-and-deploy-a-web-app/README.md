**Build a web app on Fulcra and put it online at its own address.**

Describe the app you want to your agent. It will plan the app, build it on Fulcra, and publish it to an address like `yourname.my.fulcra.ai`. You don't need a hosting account.

**What your app can do**
- Sign people in with their Fulcra account
- Save data for each user
- Share data and files between users
- Store files

**How it's built**
The agent starts from a ready-made template in Svelte or React (two common ways to build websites) that already includes sign-in. It then builds the app in small steps, checking each step against the live app before moving on.

**Your work is saved**
Your plan, decisions, and history live in your Fulcra account, so you or another agent can pick the project up later and keep improving it. A private dashboard, visible only to you, shows the test results for each step.

**Built with:** Fulcra app templates, the `fulcra-api` library, and Fulcra deploy projects.

---

## For developers

### Getting started
- Entry point: [CLI command / GitHub repo to clone / chat-only flow]
- Templates: Svelte and React, both with sign-in already configured. [Link to template repos]
- Requirements: a Fulcra account. Accounts start free with 5 GB of storage. [Confirm current storage and request limits]

### What the app can use
- **Authentication:** Users sign in with their Fulcra account. [Document how the app reads the signed-in user's identity]
- **User data:** Each user's saved data is stored in their Fulcra account. [List the `fulcra-api` operations for reading, writing, and deleting data]
- **Sharing:** [Describe how data or files are shared between users, and how permissions are scoped]
- **File storage:** [Supported file types, size limits, and how files are accessed]

### How apps are built and checked
- The agent builds the app in milestones. Each milestone is generated, then tested against the live app before it counts as done.
- [Describe what a failed milestone looks like, and how to inspect the logs or the failure]
- The dashboard, visible only to the app owner, shows each milestone's runs and test results. [Confirm the dashboard's URL and what it shows]

### Deployment
- Apps deploy to `yourname.my.fulcra.ai`. [Can you use a custom domain? Confirm yes or no]
- No hosting account needed. [Confirm whether there are request, bandwidth, or deploy limits]
- [Describe how redeploys work, and whether there's a rollback]

### Code and versioning
- [Can developers read and edit the generated code? Where is it stored?]
- Plans, specs, decisions, and history are kept in your Fulcra workspace, so another developer or agent can pick the project up later. [Confirm whether the workspace is exportable, and whether it lives in git]

### Limits and pricing
- [Storage, request, and deploy limits, and pricing beyond the free tier]

### Reference
- `fulcra-api` documentation: [link]
- Skill source: https://github.com/fulcradynamics/agent-skills/tree/main/skills/build-and-deploy-a-web-app
