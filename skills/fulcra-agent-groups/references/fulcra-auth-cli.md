# Fulcra CLI Authentication

Use the `auth login` subcommand to authenticate to Fulcra on behalf of a user.

1. Request a web auth URL and device code:
   ```bash
   uvx fulcra-api auth login --get-auth-url
   ```
   This will output a URL for the user to visit, a web auth code, and a device code.
2. Present the URL and web auth code to the user and ask them to complete the web flow.
3. Once the user confirms they have authorized the application, retrieve the access token using the device code:
   ```bash
   uvx fulcra-api auth login --device-code <device code>
   ```

Credentials will be persisted to `~/.config/fulcra/credentials.json` and the CLI will refresh tokens automatically.

> **⚠️ Network Restriction Troubleshooting**
> If the login command immediately fails or prints a raw `<http.client.HTTPResponse object...>` error, your shell likely lacks outbound network access. Do not attempt to retry or troubleshoot the network. Inform the user that the CLI method cannot be used in this environment, and advise them they will need to use an MCP connector.
