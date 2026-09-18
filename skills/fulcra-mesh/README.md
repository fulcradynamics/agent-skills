# fulcra-mesh

Let your agent talk to someone else's agent through shared outboxes in Fulcra.

Two people's agents often need to exchange something small and specific: a site agent reporting a broken link to the team that owns the docs, a friend's assistant passing along a question, a teammate's bot sending back a result. With this skill, each agent writes only to its own dedicated outbox, and reads a peer's outbox through a share naming exactly that one channel.

Each person shares read access to one dedicated message channel, including its history. Other workflows stay on their own channels. If a proposed mesh share includes other data, the agent asks for a share of the dedicated outbox instead. Your user decides who their agent talks to, and says so explicitly before any share is created.

Two habits it insists on, both learned the hard way. **A send is not delivered until you have read it back** — an upload receipt only proves the request was accepted, so every message carries its own id and is confirmed by finding that id in the channel. And **reading is done forward from a durable cursor**, so a sweep that was down for a day still picks up the day it missed instead of quietly skipping it.

Built on `fulcra-api` data types and datashares.
