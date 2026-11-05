# fulcra-control-panel

A local-only admin console for your Fulcra data — chat directly with your agent, and browse the files it reads and writes.

Fulcra keeps your real-world data in one place that belongs to you rather than to any single agent. This skill gives you a window onto it: a small web interface, running on your own machine, where you can watch what is actually in the file store and talk to the agent working on it.

Two panels:

- **Chat Envoy** — send messages to your agent and see its replies.
- **File Store Explorer** — browse and inspect the contents of your Fulcra file store.

It also gets built to your taste rather than handed to you plain. The agent asks what kind of console you want — a starship bridge, a retro command line, a cosy oak-panelled study — retitles the panels to suit, and generates original artwork for the header to match.

**It never goes on the internet.** The panel binds to `localhost`, needs a Python backend running alongside it, and can read sensitive files and issue commands to your agent. It is not built to be published, and it should not be. If you want something shareable, use `fulcra-dashboard`, which is kept deliberately separate for exactly this reason.

Ask your agent to "set up the control panel" and it will scaffold and start it for you.
