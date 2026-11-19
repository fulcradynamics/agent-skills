# map-our-team

Give every agent on a team one shared map of where the team's work lives, how to reach it, and whose agent to ask.

Teams rarely use one AI. One person works in Claude, another in Muse, another in something released last week. Moving the company's knowledge into yet another store is a project nobody wants. This skill moves nothing: Notion stays in Notion, the CRM stays the CRM. One person's agent, the steward's, keeps a short read-only map in Fulcra, and every teammate's agent reads it, connects to each tool with its own person's login, and checks that those connections still work.

When an agent can't reach something, the map says who owns it, and [connect-our-agents](../connect-our-agents/) reaches that person's agent. Agents send links rather than content, so each tool keeps applying its own permissions, and revoking someone's access at the tool still ends it.

The map holds pointers only: no content and no credentials. Everyone it's shared with can read all of it, and only the steward's agent can change it. The map lives in the steward's Fulcra account, so moving stewards means copying it over and re-sharing.

Works with the Fulcra CLI or the Fulcra MCP. Built on Fulcra file shares and connect-our-agents.
