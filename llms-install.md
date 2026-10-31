# Installing the Cedric MCP server (for AI agents)

Cedric is a remote MCP server. There is nothing to clone, build or run locally: you only add one entry to the client's MCP settings.

- Endpoint: `https://app.meet-cedric.com/api/v1/mcp`
- Transport: Streamable HTTP
- Auth: an API key `cedric_sk_...` sent as `Authorization: Bearer <key>`, or a browser sign-in (OAuth 2.1) in clients that support it

## Steps

1. Ask the user for a Cedric API key. If they have none:
   - No account yet: they sign up free at https://app.meet-cedric.com (no card needed).
   - Then they create a key in Cedric's **Settings → MCP** and paste it to you.
2. Add this entry to the MCP settings file (for Cline: `cline_mcp_settings.json`), keeping any servers already there:

```json
{
  "mcpServers": {
    "cedric": {
      "type": "streamableHttp",
      "url": "https://app.meet-cedric.com/api/v1/mcp",
      "headers": {
        "Authorization": "Bearer cedric_sk_REPLACE_ME"
      },
      "disabled": false
    }
  }
}
```

3. Replace `cedric_sk_REPLACE_ME` with the user's key. Never commit the key to a repository.
4. Reload the MCP servers and call the `getting_started` tool. It returns Cedric's usage guide and confirms the connection works.

## If something fails

- `401` or "missing or malformed API key": the key is absent, mistyped, or revoked. Ask the user for a fresh one from **Settings → MCP**.
- A tool returns `pending_approval`: that is expected for some actions. The user approves it in chat or the Cedric dashboard.
- A tool returns `requires_direct_key`: the key is a standard key. Hand the task to `ask_cedric`, or ask the user for a direct key.

Setup for other clients (Claude, Cursor, VS Code, Windsurf, Codex, Gemini CLI): [docs/clients.md](docs/clients.md). All tools: [docs/tools.md](docs/tools.md).
