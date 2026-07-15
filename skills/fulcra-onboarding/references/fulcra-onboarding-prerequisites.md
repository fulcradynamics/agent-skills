---
name: fulcra-onboarding-prerequisites
description: "Verifies and sets up the required environment for Fulcra, including ensuring the 'uv' package manager is installed."
---

# Fulcra Prerequisites Check

This skill ensures the host environment is ready to interact with the Fulcra API.

## Connection Options

There are two ways for agents to connect to Fulcra. You must determine the appropriate path before proceeding:

1. **Option 1: Fulcra CLI (Preferred)**
   The `fulcra-api` CLI is the primary interface and supports the widest range of Fulcra use cases. If you have full command-line access with outbound network connectivity, you should choose this option and proceed with the CLI workflow below.

2. **Option 2: MCP Connector (Restricted Environments)**
   Fulcra provides an MCP (Model Context Protocol) connector as an alternative option for restricted environments. To use MCP, fetch and read `https://fulcradynamics.github.io/developer-docs/mcp-server/` for setup instructions, and skip the CLI steps below.

## Workflow

1. **Verify `uv` Installation:**
   - Run `uv --version` to check if Astral's `uv` tool is installed.
   - It is required for all `fulcra-api` CLI interactions.
2. **Install `uv` if missing
   - If `uv` is not found, ask permission to install it in accordance with the user's approval process. Briefly explain that `uv` is a fast Python package manager needed to interact with the Fulcra API.
   - If the user agrees to install `uv`, use your web fetching capabilities to read the official installation instructions at `https://docs.astral.sh/uv/getting-started/installation/` and execute the appropriate installation method for their operating system.
   - Ensure `uv` is available in the current shell environment (e.g., source the env file if instructed by the install script) before returning control.

## Handoff

Once `uv` is confirmed to be installed and working, return control to the main `fulcra-onboarding` flow.
