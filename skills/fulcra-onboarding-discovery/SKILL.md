---
name: fulcra-onboarding-discovery
description: "Handles the initial discovery and authentication phase for new Fulcra users. Guides the user through login, uncovers their core intent, and suggests concrete use cases."
---

# Fulcra Onboarding: Discovery

This skill handles the first phase of the Fulcra onboarding process (Step 1). Its primary goals are to ensure the user is authenticated and to rapidly identify how Fulcra can be most useful to them right now.

## Workflow

1. **Intent Discovery (PRE-AUTH):**
   - *Before* asking the user to authenticate or click any links, engage them to uncover their core intent. What brought them to Fulcra? What do they want to track, remember, or build?
   - **Keep it frictionless:** Keep your messages extremely short and punchy. Assume the user has a low attention span. Do not send walls of text. Ask one simple, conversational question to get them invested.
   - **Quick Start Fallback:** If the user is unsure, gives a vague answer (e.g., "just trying it out"), or seems stuck, offer a brief "multiple choice" menu to spark ideas. Tailor these to the user if you have prior context, or use these default archetypes:
     - *Productivity:* Tracking daily mood or deep work sessions.
     - *Health:* Logging coffee intake, water, or sleep quality.
     - *Media:* Keeping a log of books read or movies watched.

2. **Authentication Check (STRICTLY ISOLATED):**
   - Once the user has shared their intent and is excited about what they are about to build, verify if they are currently authenticated with Fulcra.
   - **How to verify:** Silently run `uv tool run fulcra-api user-info`. If it returns valid JSON, the user is authenticated. If it returns an error or fails, they are not authenticated.
   - If not authenticated, run `uv tool run fulcra-api auth login` and guide the user through the device code flow.
   - **CRITICAL:** Do *not* combine the authentication instructions with further brainstorming. Present the auth link and code, explain it's the required next step to build what they just asked for, and wait for them to complete it.

3. **Proactive Suggestions:**
   - Suggest simple, concrete examples of how they could use Fulcra (e.g., specific Annotations to track).
   - Tailor these suggestions using your existing memory and knowledge of the user.
   - Keep the pace brisk to reach the "wow" factor quickly.

## Handoff

Once the user is authenticated and you have clearly identified 2-3 specific custom data types or streams (Annotations) they want to track, hand control back to the main `fulcra-onboarding` flow to proceed with Data Modeling.
