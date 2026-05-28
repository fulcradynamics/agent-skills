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
   - **Crucial: Grounded Brainstorming:** Never ask open-ended questions like "What do you want to track?" without providing immediate inspiration. Always seed the conversation with 2-3 specific, tailored examples of what Fulcra can track (e.g., "We could build a tracker for your daily deep work hours, how many coffees you've had, or a log of the books you're reading."). If you have long-term memory or context about this specific user, use it to make these examples highly personalized. 
   - **Keep it frictionless:** Keep your messages extremely short and punchy. Assume the user has a low attention span. Do not send walls of text. 
   - **Quick Start Fallback:** If the user is still unsure or gives a vague answer (e.g., "just trying it out"), offer a brief "multiple choice" menu to spark ideas. Tailor these to the user if you have prior context, or use these default archetypes:
     - *Productivity:* Tracking daily mood or deep work sessions.
     - *Health:* Logging coffee intake, water, or sleep quality.
     - *Media:* Keeping a log of books read or movies watched.

2. **Authentication Check & Login (Requires Consent):**
   - Once the user has shared their intent and is excited about what they are about to build, **ask for their permission** to check their Fulcra authentication state and initiate a login flow if necessary.
   - **How to verify:** After obtaining consent, run `uv tool run fulcra-api user-info`. If it returns valid JSON, the user is authenticated. If it returns an error or fails, they are not authenticated.
   - If not authenticated, explain that you will now generate a secure login link, and then run `uv tool run fulcra-api auth login` using the `exec` tool. 
   - **CRITICAL EXECUTION NOTE:** This command will output an authorization URL and a device code, and then the process will hang/wait in the background while it waits for the user to authenticate in their browser. Do *not* kill the process thinking it is stuck. If there is a chance you are running on a remote machine, the browser will not open automatically for the user. You *must* extract the login URL and code from the output and send the link directly to the user in the chat so they can click it.
   - **SECURITY WARNING:** The authorization URL and device code are highly sensitive. If you are in a public or group channel, warn the user about the sensitivity and consider messaging them directly or advising them to treat the link securely. Warn the user not to share these artifacts, as they grant access to their account.
   - Extract the URL and code from the stdout, present them to the user (adhering to the security warning above), explain it's the required next step to build what they just asked for, and wait for them to tell you they have completed the login. Do *not* combine the authentication instructions with further brainstorming.

3. **Proactive Suggestions:**
   - Suggest simple, concrete examples of how they could use Fulcra (e.g., specific Annotations to track).
   - Tailor these suggestions using your existing memory and knowledge of the user.
   - Keep the pace brisk to reach the "wow" factor quickly.

## Handoff

Once the user is authenticated and you have clearly identified 2-3 specific custom data types or streams (Annotations) they want to track, hand control back to the main `fulcra-onboarding` flow to proceed with Data Modeling.
