# Build and Deploy a Web App References

This directory contains reference implementations and documentation for the build-and-deploy-a-web-app skill.

## Structure

### Framework-Specific Components

- **`svelte/`** - SvelteKit reference implementations
  - `HarnessDashboard.svelte` - Main dashboard component
  - `OwnerNav.svelte` - Owner-only navigation bar
  - `harness-page.svelte` - Harness route page
  - `harness-api-server.js` - Owner-gated v1 runs and owner endpoints
  - `harness-owner.js` - Unchanged server-side owner claim gate
  - `harness-state.js` - JSONL parsing, query construction and run state
  - `harness-feed.js` - Latest discovery, incremental/reconciliation reads and history

### Shared Documentation

- **`harness-control-flow.md`** - Harness design and tracking system
- **`harness-events.md`** - Public CLI/MCP/REST contracts, recording and query policy
- **`harness-event-fields.json`** - Reusable v1 Event additional-field schema
- **`harness-dashboard-setup.md`** - M1 dashboard implementation and required handoff checks
- **`deploy.md`** - Deploy projects on a Fulcra domain, the deploy command, and the Vercel account fallback
- **`discoverability.md`** - Confirm search discoverability, implement opt-out, and verify the deployed policy
- **`workspace.md`** - Workspace structure and patterns
