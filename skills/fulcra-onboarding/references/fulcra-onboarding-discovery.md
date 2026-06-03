---
name: fulcra-onboarding-discovery
description: "Handles uncovering the user's core intent and suggesting concrete use cases."
---

# Fulcra Onboarding: Discovery

**Tone Reminder:** Keep the energy high! Use emojis when suggesting ideas, and maintain a conversational, exciting vibe that hints at the vast possibilities of what they can build.

This skill handles Step 3 of the Fulcra onboarding process. Its primary goal is to rapidly identify how Fulcra can be most useful to the user right now.

## Workflow

1. **Intent Discovery:**
   - Engage the user to uncover their core intent. What brought them to Fulcra? What do they want to track, remember, or build?
   - **The Fulcra Pitch:** Briefly explain what having a Fulcra account actually means so they understand the context of the ideas you are about to suggest. Keep it high-level and concise. Make sure they understand they are getting: (1) Their own private, personal datastore for storing arbitrary files, (2) The ability to seamlessly track rich, custom events and metrics, and (3) Automatic background ingestion of their data (health, location, calendars, etc.) into their personal data store. Explain that the "magic" happens when you combine this unified datastore with an AI agent.
   - **Crucial: Grounded Brainstorming:** Never ask open-ended questions like "What do you want to track?" without providing immediate inspiration. Always seed the conversation with 2-3 specific, tailored examples of what Fulcra can track. **Avoid humdrum examples like "books read" or "coffee intake".** Instead, read and reference `fulcra-onboarding-usecases.md` for directional inspiration on high-impact, "wow" factor ideas. **Do not limit your suggestions to the static examples in that file.** You must use your long-term memory (`USER.md`, `MEMORY.md`, or previous chats) to invent entirely new, highly personalized ideas tailored specifically to this user's unique life, work, or hobbies.
   - **Keep it frictionless:** Keep your messages extremely short and punchy. Assume the user has a low attention span. Do not send walls of text. 
   - **Quick Start Fallback:** If the user is still unsure or gives a vague answer (e.g., "just trying it out"), offer a brief "multiple choice" menu to spark ideas. Tailor these entirely to the user's known context if possible. If no context exists, adapt the high-impact archetypes from `fulcra-onboarding-usecases.md` (e.g., Social Battery, Flow State, Friction-Log) into a quick list.

2. **Proactive Suggestions:**
   - Suggest concrete, "wow" factor examples of how they could use Fulcra (using `fulcra-onboarding-usecases.md` purely as a structural template).
   - Avoid boring trackers; invent ideas that combine multiple data streams to show real insights.
   - Tailor these suggestions intimately to your existing memory and knowledge of the user.
   - Keep the pace brisk to reach the "wow" factor quickly.

## Handoff

Once you have clearly identified 2-3 specific custom data types or streams (Annotations) they want to track for themselves, hand control back to the main `fulcra-onboarding` flow to proceed with Data Modeling (Step 4).
