---
name: fulcra-onboarding-discovery
description: "Handles the initial discovery and authentication phase for new Fulcra users. Guides the user through login, uncovers their core intent, and suggests concrete use cases."
---

# Fulcra Onboarding: Discovery

**Tone Reminder:** Keep the energy high! Use emojis when suggesting ideas, and maintain a conversational, exciting vibe that hints at the vast possibilities of what they can build.

This skill handles the first phase of the Fulcra onboarding process (Step 1). Its primary goals are to ensure the user is authenticated and to rapidly identify how Fulcra can be most useful to them right now.

## Workflow

1. **Intent Discovery (PRE-AUTH):**
   - *Before* asking the user to authenticate or click any links, engage them to uncover their core intent. What brought them to Fulcra? What do they want to track, remember, or build?
   - **The Fulcra Pitch:** Briefly explain what having a Fulcra account actually means so they understand the context of the ideas you are about to suggest. Keep it high-level and concise. Make sure they understand they are getting: (1) Their own private, personal datastore for storing arbitrary files, (2) The ability to seamlessly track rich, custom events and metrics, and (3) Automatic background ingestion of their data (health, location, calendars, etc.) into their personal data store. Explain that the "magic" happens when you combine this unified datastore with an AI agent.
   - **Crucial: Grounded Brainstorming:** Never ask open-ended questions like "What do you want to track?" without providing immediate inspiration. Always seed the conversation with 2-3 specific, tailored examples of what Fulcra can track. **Avoid humdrum examples like "books read" or "coffee intake".** Instead, read and reference `fulcra-onboarding-usecases.md` for high-impact, "wow" factor ideas (e.g., a "Social Battery" dashboard or a Creative Flow State mapper). If you have long-term memory or context about this specific user, use it to make these examples highly personalized. 
   - **Keep it frictionless:** Keep your messages extremely short and punchy. Assume the user has a low attention span. Do not send walls of text. 
   - **Quick Start Fallback:** If the user is still unsure or gives a vague answer (e.g., "just trying it out"), offer a brief "multiple choice" menu to spark ideas. Tailor these to the user if you have prior context, or use these high-impact archetypes from `fulcra-onboarding-usecases.md`:
     - *The Social Battery Dashboard:* Predict burnout by correlating calendar density and messaging volume.
     - *Creative Flow State Mapper:* Find their peak focus environment combining music history and work sessions.
     - *The Friction-Log Automator:* A voice-pipeline to track daily frustrations and prioritize what to automate next.

2. **Authentication Check & Login (Requires Consent):**
   - Once the user has shared their intent and is excited about what they are about to build, **ask for their permission** to check their Fulcra authentication state and initiate a login flow if necessary.
   - **How to verify:** After obtaining consent, run `uv tool run fulcra-api user-info`. If it returns valid JSON, the user is authenticated. If it returns an error or fails, they are not authenticated.
   - If not authenticated, explain that you will now generate a secure login link, and then run `uv tool run fulcra-api auth login` using the `exec` tool. 
   - **CRITICAL EXECUTION NOTE:** This command will output an authorization URL and a device code, and then the process will hang/wait in the background while it waits for the user to authenticate in their browser. Do *not* kill the process thinking it is stuck. If there is a chance you are running on a remote machine, the browser will not open automatically for the user. You *must* extract the login URL and code from the output and send the link directly to the user in the chat so they can click it.
   - **SECURITY WARNING:** The authorization URL and device code are highly sensitive. If you are in a public or group channel, warn the user about the sensitivity and consider messaging them directly or advising them to treat the link securely. Warn the user not to share these artifacts, as they grant access to their account.
   - Extract the URL and code from the stdout, present them to the user (adhering to the security warning above), explain it's the required next step to build what they just asked for, and wait for them to tell you they have completed the login. Do *not* combine the authentication instructions with further brainstorming.

3. **Proactive Suggestions & Agent Visibility:**
   - Suggest concrete, "wow" factor examples of how they could use Fulcra (referencing `fulcra-onboarding-usecases.md` for inspiration).
   - Avoid boring trackers; combine multiple data streams to show real insights.
   - Tailor these suggestions using your existing memory and knowledge of the user.
   - Keep the pace brisk to reach the "wow" factor quickly.
   - **Universal Agent Visibility Package:** Alongside their personal use cases, pitch the idea of tracking the agent's own activity. Explain that you can log your completed tasks, provide a scale for them to rate agent friction, and record text annotations containing concise markdown summaries of what you are currently working on. Confirm they want this added, framing it as a way to give them immediate visibility into your background work directly from their Fulcra app and dashboard.

## Handoff

Once the user is authenticated and you have clearly identified 2-3 specific custom data types or streams (Annotations) they want to track, hand control back to the main `fulcra-onboarding` flow to proceed with Data Modeling.
