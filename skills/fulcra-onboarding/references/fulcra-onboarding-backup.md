---
name: fulcra-onboarding-backup
description: "Prompts the user to back up the agent's initial state using the fulcra-memory skill before proceeding to the demonstration."
---

# Fulcra Onboarding: Agent Baseline Backup

This skill handles Step 5 of the onboarding process. Now that the user has authenticated and created their first annotations, it is the perfect time to capture a baseline snapshot of the agent's memory.

## Workflow

1. **The Pitch:**
   - Briefly explain to the user that since you've just established their core tracking intents and set up their Fulcra connection, this is a great time to perform a baseline backup of your (the agent's) memory directly to their Fulcra datastore.
   - Mention the benefit: "By snapshotting my memory now, if we ever go off track or you want to experiment later, you can easily roll me back to this exact pristine setup state."

2. **Ask for Consent:**
   - Explicitly ask them if they'd like you to perform this baseline backup right now.

3. **Execution (If Yes):**
   - If they agree, read and follow the instructions in `../../fulcra-memory/references/fulcra-memory-cli.md` to perform the backup (creating the `top_of_mind.md` file, compressing the memory directory, and uploading everything using the Fulcra CLI).
   - *Note: Ensure your `top_of_mind.md` summary for this backup reflects that you have just completed the onboarding discovery and data modeling phases.*
   - Once completed, celebrate the successful backup!

4. **Handoff:**
   - Whether they say yes or no (or immediately after the backup is complete), smoothly transition control back to the main `fulcra-onboarding` flow to proceed to the "Time-to-Wow" Demonstration.
