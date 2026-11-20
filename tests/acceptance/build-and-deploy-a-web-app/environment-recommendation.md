# Advisory coding-agent recommendation

## Scope and setup

Test the skill's opening replies, not app generation or deployment. Load the current `SKILL.md` in a fresh, neutral agent context for each host below. Disable tools, connectors, memory and project instructions. No Fulcra login, resource creation, uploads or cleanup are needed.

The host labels below are explicit test context, not claims that a test runner is actually ChatGPT or Claude chat. Judge behavior rather than exact wording.

## Turns and expected behavior

Start each case with: “Use build-and-deploy-a-web-app to help me start a new app.”

- **ChatGPT web chat:** the reply starts with a Codex recommendation and brief switching instructions, then asks about the app in the same reply. Continuing in chat is explicitly allowed.
- **Claude web chat:** the same behavior, recommending Claude Code instead.
- **Codex, Claude Code, or another coding-agent host:** no switching notice; proceed to the app question.
- **Unknown host:** no warning or host-detection question; proceed to the app question. A model name alone must not trigger a recommendation.

Continue the ChatGPT case with: “I want to stay here. Help me plan a simple habit tracker for myself.” The agent continues planning without repeating the recommendation or asking for switching approval.

In a separate ChatGPT case, start with: “Use build-and-deploy-a-web-app to continue my habit tracker. The project is ~/habits and the Fulcra workspace is workspace/habits/.” After its opening reply, say: “I'll switch to Codex. Give me a handoff.” The handoff names the skill, project and workspace, preserves any stated decisions, and does not claim the conversation transfers automatically.

## Pass criteria

All host cases follow their expected route. Recommendations precede planning, remain advisory and do not recur after the user chooses to stay. The switch handoff preserves the existing project/workspace. No tools are called and no resources are created. Keep the prompts, replies, model and skill commit with the test result; these are isolated prompt checks, not native ChatGPT/Claude UI or deployed-app acceptance.
