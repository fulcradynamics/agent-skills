---
name: fulcra-memory-cli
description: "CLI command references for executing the memory backup, restore, and cloning operations with Fulcra."
---

# Fulcra Memory CLI Reference

This reference dictates the exact shell commands required to execute the `fulcra-memory` skill's operations. Ensure all tar and CLI operations run in the agent's root workspace (`~/.openclaw/workspace`).

## 1. Creating a Backup and Uploading

To back up the agent's memory, you must generate a `top_of_mind.md` summary, compress the core identity files, and upload both to Fulcra.

**Step A: Create Top of Mind**
Generate a concise markdown file summarizing your current tasks, thoughts, and context.
```bash
# Ensure you are in the workspace
cd ~/.openclaw/workspace
mkdir -p memory
echo "# Current Agent State..." > memory/top_of_mind.md
# (Write your actual summary content to this file)
```

**Step B: Compress the files**
Before compressing, create a `README.md` file that explains the archive's purpose and usage constraints. This ensures any agent or human inspecting the archive understands its contents and the rules for restoration.

```bash
# Generate the README.md
cat << 'EOF' > README.md
# Fulcra Agent Memory Archive

This archive was created by the `fulcra-memory` skill. It contains an agent's core identity and memory state (e.g., `SOUL.md`, `IDENTITY.md`, `MEMORY.md`, and the `memory/` directory).

## Usage
The contents of this archive can be used to roll back an agent's memory or identity to a previous state, or to clone them to a new agent.

## CRITICAL RULES FOR RESTORATION/CLONING
1. **Explicit Permission Required:** The restoring/cloning agent MUST always get direct user permission and confirmation before overwriting its local files with the contents of this archive.
2. **Verification Responsibility:** The backup may have been performed by a different harness or agent than the one restoring it. It is the active agent's responsibility to verify that it is overwriting or merging the correct files and to warn the user about any potential data loss.
3. **Pre-Restore Backup:** Before performing the restore or clone operation, the active agent MUST make a local backup of its own current identity and memory files and inform the user of the backup's location so the operation can be undone if needed.
EOF

# Create a gzip tarball containing the essential memory files (ignore if some are missing)
tar -czvf /tmp/memory.tar.gz README.md SOUL.md IDENTITY.md MEMORY.md memory/ 2>/dev/null || true
```

**Step C: Upload to Fulcra**
Upload the files using the standardized agent path convention. Determine the agent's name (lowercase) to use in the path.

```bash
# Replace <agent_name> with the agent's actual name (e.g., treecle, wazir) in lowercase
uv tool run fulcra-api file upload /tmp/memory.tar.gz "agent/<agent_name>/memory/memory.tar.gz"
uv tool run fulcra-api file upload memory/top_of_mind.md "agent/<agent_name>/memory/top_of_mind.md"
```

## 2. Listing Memory History

Because Fulcra versions files automatically, you can see all previous backups of the memory using the `stat` command.

```bash
uv tool run fulcra-api file stat "agent/<agent_name>/memory/memory.tar.gz"
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
uv tool run fulcra-api file download "agent/<agent_name>/memory/memory.tar.gz" /tmp/restored_memory.tar.gz
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

To clone, skip the restore step and simply download the target agent's `memory.tar.gz` archive.

```bash
# Download the target agent's memory
uv tool run fulcra-api file download "agent/<other_agent_name>/memory/memory.tar.gz" /tmp/restored_memory.tar.gz
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

