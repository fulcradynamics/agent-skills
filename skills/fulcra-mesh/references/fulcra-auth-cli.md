# Fulcra CLI authentication

Check `uvx --from fulcra-api@latest fulcra user-info` first. Reuse an authenticated session for the intended user.

If login is needed:

1. Run `uvx --from fulcra-api@latest fulcra auth login --get-auth-url`.
2. Show the returned URL and web auth code to the user so they can complete browser authentication.
3. Complete login with `uvx --from fulcra-api@latest fulcra auth login --device-code <device-code>` and verify the account with `user-info`.

The CLI persists credentials and refreshes tokens automatically. Keep the device code within the login flow.

If a command fails, use its error to distinguish authentication from connectivity problems. Follow the host's normal network-access procedure; if CLI access is unavailable, use a Fulcra MCP connection. Explain the remaining setup step to the user.
