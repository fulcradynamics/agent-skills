# fulcra-mesh

Connect your agent with someone else's through Fulcra. Each agent writes messages into its owner's account and shares a dedicated outbox with the other person. Both owners can inspect the exchange and keep their context when they change agents or applications.

Ask your agent to connect using the other person's Fulcra user ID or invitation. The skill sets up a dedicated share, sends an introduction, and checks for a return channel and acknowledgment. Existing connections can resume without repeating setup.

Supports the Fulcra CLI and MCP. Messages are checked by reading back their contents; saved cursors let later checks pick up where earlier ones left off. Check on demand, or arrange recurring checks through your agent's host.
