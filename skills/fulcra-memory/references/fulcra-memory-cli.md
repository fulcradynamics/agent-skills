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
```bash
# Create a gzip tarball containing the essential memory files (ignore if some are missing)
tar -czvf /tmp/memory.gz SOUL.md IDENTITY.md MEMORY.md memory/ 2>/dev/null || true
```

**Step C: Upload to Fulcra**
Upload the files using the standardized agent path convention. Determine the agent's name (lowercase) to use in the path.

```bash
# Replace <agent_name> with the agent's actual name (e.g., treecle, wazir) in lowercase
uv tool run fulcra-api file upload /tmp/memory.gz "agent/<agent_name>/memory/memory.gz"
uv tool run fulcra-api file upload memory/top_of_mind.md "agent/<agent_name>/memory/top_of_mind.md"
```

## 2. Listing Memory History

Because Fulcra versions files automatically, you can see all previous backups of the memory using the `stat` command.

```bash
uv tool run fulcra-api file stat "agent/<agent_name>/memory/memory.gz"
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
uv tool run fulcra-api file download "agent/<agent_name>/memory/memory.gz" /tmp/restored_memory.gz
```

**Step C: Extract and overwrite local memory**
```bash
cd ~/.openclaw/workspace
tar -xzvf /tmp/restored_memory.gz
```
*(This will overwrite the local `SOUL.md`, `IDENTITY.md`, `MEMORY.md`, and the `memory/` directory with the state from the downloaded archive.)*

## 4. Cloning Another Agent's Memory

To clone, skip the restore step and simply download the target agent's `memory.gz` archive.

```bash
# Download the target agent's memory
uv tool run fulcra-api file download "agent/<other_agent_name>/memory/memory.gz" /tmp/restored_memory.gz

# Extract locally (Overwrites current identity and memory)
cd ~/.openclaw/workspace
tar -xzvf /tmp/restored_memory.gz
```

## 5. Uploading User Artifacts

When an agent generates a file (like an HTML dashboard, an image, or a report), and the user explicitly approves saving it to their Fulcra account, upload it to the `artifacts/` subdirectory.

```bash
# Replace <agent_name> with the agent's name, and <artifact_name> with the file's name
uv tool run fulcra-api file upload /path/to/local/file "agent/<agent_name>/artifacts/<artifact_name>"
```