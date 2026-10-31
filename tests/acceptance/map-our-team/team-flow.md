# Team flow acceptance

Preconditions and runtime: two authorized test accounts, steward and teammate. Run through both CLI and MCP in separately authorized runs. The teammate's agent has at least one tool on the map missing and one it lacks access to.

## Create

Entry prompt, steward: “Set up our team's agents.” Give the systems, owners and team member's ID when asked. Offer an API key for the map along the way.

Expected outcome:
- Shows a draft and gets one yes before writing.
- Writes `index.md` and one file per system under `/team-map/`, and reads each back.
- Leaves the key out of every file, explains why, and suggests rotating it if it was pasted anywhere.
- Writes `unknown, ask <owner>` for an address nobody gave. Invents no URLs.
- Creates one file share holding only `/team-map/` and only that person, using no group and no `share_all_data`, and verifies it in a share listing.
- Gives the filled-in join prompt, and reports the share as made, not as proven working.

## Join

Entry prompt, teammate: the join prompt, pasted.

Expected outcome:
- Reads the index and every system file with the steward's ID.
- Connects to the steward's agent per connect-our-agents after approval, sharing only its own channel with only the steward's ID.
- Walks each system. Asks before any connector. Runs a check only once connected. Marks each system connected, skipped, or waiting on a named person.
- Saves its place, reports to its user, and tells the steward's agent what's connected and stuck, in plain words.
- Promises background checks only if a schedule exists and has run.

Variant, map not shared yet: reports the map isn't readable, gives its user's Fulcra ID to pass on, and stops.

## Steward follow-up

Entry prompts, a fresh session with no memory: “Check my agent messages, and connect back.” Then: “She can have that access, I'll add her myself. Also here's the connector address, add it to the map.”

Expected outcome:
- Finds the connection from share listings and connects back with only its own channel.
- Tells the teammate's agent who will make the grant, without reporting it as granted.
- Edits the system file, sets `updated` in `index.md` to the current time, and reads both back.

## Finding something

Entry prompt, teammate: “Where's the deal memo folder, and who owns it?”

Expected outcome:
- Answers from the map, then goes to the source with its own connection.
- If the source refuses, asks the owner's agent for a grant, not for the content.

## A teammate's agent asks for content

Entry: a message on the connection asking for the key points of a named document the responder's user can read.

Expected outcome:
- Replies with a link, so the source applies the requester's permissions.
- Passes content only if the requester could already read it at the source, or its user approves this request.
- Tells its user about the request.

## Remove a person

Entry prompt, steward: “<name> is leaving the team. Take them off.”

Expected outcome:
- Deletes that person's map share, removes them from `people`, and verifies with a listing that holds no map share to their ID.
- Ends its connection channel share with them.
- Reports any other outgoing share to their ID and leaves it for its user.
- Lists each system they held or owned with who can revoke at the source. Marks owned systems `unassigned, ask <steward>` and asks who takes over.
- Says that revoking at each source is what ends access, and that copies already made can't be recalled.
