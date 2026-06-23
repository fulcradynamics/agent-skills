---
name: fulcra-agent-backup-cli
description: "CLI command references for executing the memory backup, restore, and cloning operations with Fulcra."
---

# Fulcra Agent Backup CLI Reference

This reference dictates the exact shell commands required to execute the `fulcra-agent-backup` skill's operations. Ensure all tar and CLI operations run in the agent's root workspace (`~/.openclaw/workspace`).

## 1. Creating a Backup and Uploading

To back up the agent's memory, compress the core identity files and upload them to Fulcra.

**Step A: Compress the files**
Before compressing, dynamically generate an `INSTRUCTIONS.md` file using your standard file writing tools. It must explain that the archive was created with the `fulcra-agent-backup` skill, provide the URL to the skill (https://github.com/fulcradynamics/agent-skills/tree/main/skills/fulcra-agent-backup) for restoring or cloning, and include any other pertinent notes you want to leave for the agent that extracts this backup. Do not blindly copy an example template; write a thoughtful and contextual `INSTRUCTIONS.md` tailored to the current backup state. This file will be uploaded directly to Fulcra, not bundled inside the tarball.

```bash
# Ensure you are in the workspace
cd ~/.openclaw/workspace

# (Ensure INSTRUCTIONS.md was written successfully before proceeding)

# Create a gzip tarball containing the essential memory files (ignore if some are missing)
# Notice INSTRUCTIONS.md is INTENTIONALLY OMITTED from the tarball contents
tar -czvf /tmp/memory.tar.gz SOUL.md IDENTITY.md MEMORY.md memory/ 2>/dev/null || true
```

**Step B: Upload to Fulcra**
Upload the files using the standardized agent path convention. Determine the agent's name (lowercase) to use in the path. You must upload both the artifact tarball and the `INSTRUCTIONS.md` file.

```bash
# Replace <agent_name> with the agent's actual name (e.g., treecle, wazir) in lowercase
uv tool run fulcra-api file upload /tmp/memory.tar.gz "agent/<agent_name>/backup/artifact/memory.tar.gz"
uv tool run fulcra-api file upload INSTRUCTIONS.md "agent/<agent_name>/backup/INSTRUCTIONS.md"
```

## 2. Listing Memory History

Because Fulcra versions files automatically, you can see all previous backups of the memory using the `stat` command.

```bash
uv tool run fulcra-api file stat "agent/<agent_name>/backup/artifact/memory.tar.gz"
```
*(This command will output information about the file, including all previously uploaded versions and their UUIDs. Present these to the user so they can select a version to restore.)*

## 3. Safe Restoration / Rollback

**CRITICAL:** Before performing a restore, you MUST perform a fresh backup (Step 1 above) to ensure the current state isn't lost.

Once the pre-restore backup is complete, use the Fulcra CLI to set the active version, then download and extract it.

**Step A: Restore the version in Fulcra**
```bash
# Instruct Fulcra to make the older version the active file
uv tool run fulcra-api file restore <version_id>
```

**Step B: Download the restored file**
```bash
uv tool run fulcra-api file download "agent/<agent_name>/backup/artifact/memory.tar.gz" /tmp/restored_memory.tar.gz
```

**Step C: Inspect and Confirm**
**STOP.** You MUST explicitly warn the user that extracting the archive will overwrite their current identity and memory files (`SOUL.md`, `IDENTITY.md`, `MEMORY.md`, and `memory/`). Before asking for confirmation, inspect the contents of the archive to ensure it looks safe and expected:
```bash
tar -ztvf /tmp/restored_memory.tar.gz
```
Share the list of files with the user and ask for their explicit confirmation before proceeding.

**Step D: Extract and overwrite local memory**
```bash
cd ~/.openclaw/workspace
tar -xzvf /tmp/restored_memory.tar.gz
```
*(This will overwrite the local `SOUL.md`, `IDENTITY.md`, `MEMORY.md`, and the `memory/` directory with the state from the downloaded archive.)*

## 4. Cloning Another Agent's Memory

Cloning involves an "old" (source) agent and a "new" (destination) agent. The first step is to determine which role you are playing.

**If you are the OLD agent:**
1. Perform a full backup of your current state (Follow Step 1: Creating a Backup and Uploading).
2. Stop and tell the user the exact Fulcra path where the backup was saved (e.g., `agent/<your_agent_name>/backup/artifact/memory.tar.gz`).
3. Instruct the user to install the `fulcra-agent-backup` skill on the new agent and ask it to clone from that path.

**If you are the NEW agent:**
1. Ask the user to confirm the old agent has recently backed itself up using the `fulcra-agent-backup` skill. (Instruct them to have the old agent install the skill and back up if it hasn't already). Then, ask them for the specific Fulcra path to the old agent's memory archive.
2. Download the target agent's memory using the path provided by the user:

```bash
# Download the target agent's memory
uv tool run fulcra-api file download "agent/<old_agent_path>/backup/artifact/memory.tar.gz" /tmp/restored_memory.tar.gz
```

**STOP.** You MUST explicitly warn the user that extracting the cloned archive will overwrite your current identity and memory files with the cloned agent's state. Before asking for confirmation, inspect the contents of the cloned archive:
```bash
tar -ztvf /tmp/restored_memory.tar.gz
```
Share the list of files with the user and ask for their explicit confirmation before proceeding.

```bash
# Extract locally (Only after user confirmation!)
cd ~/.openclaw/workspace
tar -xzvf /tmp/restored_memory.tar.gz
```

**Step 3: Demonstrate Clone Success**
After extraction, read your newly updated `IDENTITY.md` and `MEMORY.md` files. In your next message to the user, explicitly mention a few specific facts, past actions, or preferences you have just learned from those files to prove the cloning was successful.