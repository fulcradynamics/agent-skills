# fulcra-mesh

Let your agent talk to someone else's agent — across accounts, without either of you handing over the keys.

Two people's agents often need to exchange something small and specific: a site agent reporting a broken link to the team that owns the docs, a friend's assistant passing along a question, a teammate's bot sending back a result. The usual ways to do that are all too much — a shared login, a broad data grant, a bot sitting in the middle. This skill does it with the narrowest thing that works: each agent writes only to its own dedicated outbox, and reads a peer's outbox through a share naming exactly that one channel.

**Nobody gets write access to anybody.** A peer cannot post into your account and you cannot post into theirs — you each publish to your own channel and the other side reads it. Shares are narrow by construction: one dedicated channel per peer relationship, never a general-purpose channel your other workflows already write to, and never `share_all_data`. If someone asks for the broad version, the skill's answer is to stop and show them the narrow one instead. Your user decides who their agent talks to, and says so explicitly before any share is created.

Two habits it insists on, both learned the hard way. **Read back each saved message** — an upload receipt proves the request was accepted; finding its exact id and body in the channel confirms it was saved. A peer acknowledgment confirms receipt. And **reading is done forward from a durable cursor**, so a sweep that was down for a day still picks up the day it missed instead of quietly skipping it.

Built on `fulcra-api` data types and datashares.
