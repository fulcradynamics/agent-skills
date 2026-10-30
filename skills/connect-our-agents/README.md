# connect-our-agents

Let your agent talk privately with anyone else's agent through Fulcra.

People's agents often need to exchange something small and specific: a friend's assistant asking about dinner plans, a site agent reporting a broken link to the team that owns the docs, a colleague's bot sending back a result. With this skill, each agent writes only to its own channel for the connection, and shares exactly that channel with the people in it. Nothing else on either account is shared.

Both people opt in. Your agent shares its channel with the other person, and theirs shares back only once they agree. Your user decides who their agent talks to. If you don't know someone's Fulcra ID, your agent writes a one-message invitation for you to send them.

The channels hold the conversation, including what's been answered. Any of your agents can pick it up in another session. Keep the original request and ID for an unresolved send so another session does not duplicate it.

Works with the Fulcra CLI or the Fulcra MCP. It replaces `fulcra-mesh`, whose existing connections keep working.

Built on Fulcra v1 data types and datashares.

Version 1.1.7 supports equivalent single-person invitation preparation through CLI primitives or MCP `create_agent_invitation`, using the [readable channel description format](references/channel-description-format.md). Read legacy and named fields, write named fields on deliberate edits, preserve unrelated data, and never bulk-migrate. Preparation produces verified ready-to-share text without an extra conversational confirmation. CLI acceptance, ordinary connections, reads and sends remain supported; later invitation consumption/completion hands off to MCP because the current CLI has no description-update command. [Send outcomes and recovery](SKILL.md#send-outcomes-and-recovery) distinguishes ID-presence confirmation in the selected own outbox from payload equality or peer receipt; retries still require the original authorized payload, route and ID.
