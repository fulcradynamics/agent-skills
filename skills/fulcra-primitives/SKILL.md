---
name: fulcra-primitives
description: "A plain, no-nonsense introduction to the Fulcra CLI, covering core primitives (data types and versioned file uploads)."
homepage: "https://github.com/fulcradynamics/agent-skills"
license: "MIT"
user-invocable: true
metadata: { "openclaw": { "emoji": "🧱" } }
---

# Fulcra Primitives

A straightforward introduction to the Fulcra CLI, focusing strictly on core concepts: Fulcra primitives, data types, and versioned file uploads. 

Unlike other skills focused on rapid deployment or dashboards, this skill is designed to explain the fundamental building blocks of Fulcra without flash or hyperbole. It should be used when a user wants to understand *how* Fulcra stores data under the hood and how to manually interact with it using the CLI.

## General Guidelines

- **Tone & Vibe (No-Nonsense):** Keep the tone plain, informative, and direct. Avoid excessive emojis, hype, or "sales pitches." The user wants to learn the technical fundamentals.
- **Focus:** Stick closely to explaining data types and versioned file uploads.
- **MCP Option:** Early in the conversation, mention that while we are focusing on the CLI here, Fulcra also offers an MCP (Model Context Protocol) option. Provide the link to [AGENTS.md](https://github.com/fulcradynamics/agent-skills/blob/main/AGENTS.md) (or the specific AGENTS.md link relevant to Fulcra MCP) for reference.

## Workflow

### 1. Introduction and MCP Mention
- Start by introducing the goal: understanding Fulcra's core primitives via the CLI.
- Mention that Fulcra offers an MCP option for agents. Direct the user to the `AGENTS.md` file for more information on the broader agent ecosystem, but clarify that this session will focus strictly on the CLI.
- Read `references/fulcra-cli.md` to load the CLI context.

### 2. Authentication
- Before interacting with the platform, the user must authenticate.
- Guide the user to authenticate using the CLI. Do not proceed until authentication is successful.

### 3. Core Concepts and CLI Usage
Once authenticated, explain the primary Fulcra primitives:
- **Data Types:** Explain how data is modeled and stored in Fulcra.
- **Versioned File Uploads:** Explain how to manage files and their versions using the CLI.
- Walk the user through practical examples using the `fulcra-api` CLI based on the `fulcra-cli.md` reference. Let them test uploading files or querying data types if they wish.

### 4. Ecosystem Resources
After the user has successfully authenticated and explored the primitives, casually mention the following resources as additional ways to interact with their Fulcra data:
- **Fulcra iOS App:** For on-the-go logging and mobile data capture.
- **Context Web Portal:** Explore their datastore directly at [https://context.fulcradynamics.com](https://context.fulcradynamics.com).
- **Fulcra Skills Repository:** Point them to the broader repository of Fulcra agent skills to expand their capabilities.
