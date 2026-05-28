---
name: fulcra-onboarding-prerequisites
description: "Verifies and sets up the required environment for Fulcra, including ensuring the 'uv' package manager is installed."
---

# Fulcra Prerequisites Check

This skill ensures the host environment is ready to interact with the Fulcra API.

## Workflow

1. **Verify `uv` Installation:**
   - Run `uv --version` to check if Astral's `uv` tool is installed.
   - It is required for all `fulcra-api` CLI interactions.
2. **Install `uv` if Missing (Requires Consent):**
   - If `uv` is not found, **you must explicitly ask the user for permission** to install it. Briefly explain that `uv` is a fast Python package manager needed to interact with the Fulcra CLI.
   - Only after receiving explicit consent, install it automatically.
   - For macOS/Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
   - For Windows: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
   - Ensure `uv` is available in the current shell environment (e.g., source the env file if instructed by the install script) before returning control.

## Handoff

Once `uv` is confirmed to be installed and working, return control to the main `fulcra-onboarding` flow.
