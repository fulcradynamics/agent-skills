---
name: fulcra-onboarding-prerequisites
description: "Verifies and sets up the required environment for Fulcra, including ensuring the 'uv' package manager is installed."
---

# Fulcra Prerequisites Check

This skill ensures the host environment is ready to interact with the Fulcra API.

## Environment Check: Command Line vs. Chat

Before attempting to verify or install CLI tools, determine if you are running in an environment with command-line access.

- **Command Line Access (Most Likely):** You are likely running as an autonomous agent or in an environment with terminal/shell access (e.g., OpenClaw, standard agent workspaces). If so, proceed with the CLI workflow below.
- **Chat/MCP Environment (Fallback):** If you are running in a restricted chat environment without command-line access, you cannot use the `fulcra-api` CLI tool. Instead, advise the user that Fulcra provides an MCP (Model Context Protocol) connector. You should then fetch and read `https://fulcradynamics.com/AGENTS.md` for instructions appropriate to chat environments, and skip the CLI steps below.

## Workflow

1. **Verify `uv` Installation:**
   - Run `uv --version` to check if Astral's `uv` tool is installed.
   - It is required for all `fulcra-api` CLI interactions.
2. **Install `uv` if Missing (Requires Explicit Consent):**
   - If `uv` is not found, you **must explicitly ask the user for permission** to install it on their machine. Briefly explain that `uv` is a fast Python package manager needed to interact with the Fulcra API.
   - **CRITICAL SECURITY NOTE:** Do not guess the installation commands. If the user agrees to install `uv`, use your web fetching capabilities to read the official installation instructions at `https://docs.astral.sh/uv/getting-started/installation/` and execute the appropriate installation method for their operating system.
   - Ensure `uv` is available in the current shell environment (e.g., source the env file if instructed by the install script) before returning control.

## Handoff

Once `uv` is confirmed to be installed and working, return control to the main `fulcra-onboarding` flow.
