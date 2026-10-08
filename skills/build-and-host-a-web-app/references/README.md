# Build and Host a Web App References

This directory contains reference implementations and documentation for the build-and-host-a-web-app skill.

## Structure

### Framework-Specific Components

- **`svelte/`** - SvelteKit reference implementations
  - `HarnessDashboard.svelte` - Main dashboard component
  - `OwnerNav.svelte` - Owner-only navigation bar
  - `harness-page.svelte` - Harness route page
  - `harness-api-server.js` - Backend API endpoints (contains both runs and issues)

- **`react/`** - React/Next.js reference implementations
  - `HarnessDashboard.tsx` - Main dashboard component

### Shared Documentation

- **`harness-control-flow.md`** - Harness design and tracking system
- **`harness-dashboard-setup.md`** - M1 dashboard implementation and required handoff checks
- **`deploy.md`** - Deploy projects on a Fulcra domain, the deploy command, and the Vercel account fallback
- **`workspace.md`** - Workspace structure and patterns
