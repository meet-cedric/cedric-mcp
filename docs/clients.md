# Connect an MCP client to Cedric

Cedric is a remote MCP server at one address:

```
https://app.meet-cedric.com/api/v1/mcp
```

Give your client that address and sign in once in your browser. From then on the client works in your Cedric workspace as you: the same memory, the same connected apps and the same approvals as chat. No account yet? [Start free](https://app.meet-cedric.com), no card needed.

Two ways in, and both work for every client below:

- **Sign in from the client (recommended).** The client opens your browser, you approve once, and it keeps a token that refreshes on its own. Nothing secret to paste. A sign-in runs in standard mode, so the tools marked **Direct key only** in [tools.md](tools.md) are refused; hand that work to `ask_cedric`, which puts each send in your Action Centre for you to approve, or use a direct key.
- **API key (headless).** For scripts, CI and agents with no browser. Create a key in Cedric's **Settings → MCP** and send it as `Authorization: Bearer cedric_sk_...`. See [API keys](#api-keys).

## Claude Code

```bash
claude mcp add --transport http cedric https://app.meet-cedric.com/api/v1/mcp
```

Then run `/mcp`, pick `cedric` and choose **Authenticate**. Your browser opens to sign in.

## Cursor

Add it under **Settings → MCP**, or in `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "cedric": {
      "url": "https://app.meet-cedric.com/api/v1/mcp"
    }
  }
}
```

Click **Needs login** next to `cedric` to sign in.

## VS Code

```bash
code --add-mcp '{"name":"cedric","type":"http","url":"https://app.meet-cedric.com/api/v1/mcp"}'
```

Or in `.vscode/mcp.json`:

```json
{
  "servers": {
    "cedric": {
      "type": "http",
      "url": "https://app.meet-cedric.com/api/v1/mcp"
    }
  }
}
```

Start the server in the MCP view; VS Code asks you to sign in. MCP servers run in Copilot agent mode.

## Claude

**Settings → Connectors → Add custom connector**, paste the address, click **Connect** and sign in. Custom connectors need a paid Claude plan; once added, the connector works in every chat.

## ChatGPT

**Settings → Connectors → Create** (with developer mode on), paste the address, choose **OAuth**, click **Create** and sign in. Custom connectors need a paid plan, and availability varies by account.

## Codex CLI

```bash
codex mcp add cedric --url https://app.meet-cedric.com/api/v1/mcp
codex mcp login cedric
```

`codex mcp login` opens your browser.

## Gemini CLI

```bash
gemini mcp add --transport http cedric https://app.meet-cedric.com/api/v1/mcp
```

Then run `/mcp auth cedric` to sign in.

## Windsurf

**Settings → Cascade → MCP servers**, or in `mcp_config.json`:

```json
{
  "mcpServers": {
    "cedric": {
      "serverUrl": "https://app.meet-cedric.com/api/v1/mcp"
    }
  }
}
```

Refresh, and Windsurf opens the sign-in.

## Any other client

Add Cedric as an HTTP MCP server with the address above. Any client that speaks Streamable HTTP MCP with OAuth discovers the sign-in by itself. No browser? Use an API key.

## API keys

For a script, a CI job, or an agent that cannot open a browser, skip the sign-in and send a key:

```bash
claude mcp add --transport http cedric \
  https://app.meet-cedric.com/api/v1/mcp \
  --header "Authorization: Bearer $CEDRIC_KEY"
```

The same header works in any client that accepts custom headers, for example Cursor:

```json
{
  "mcpServers": {
    "cedric": {
      "url": "https://app.meet-cedric.com/api/v1/mcp",
      "headers": { "Authorization": "Bearer ${env:CEDRIC_KEY}" }
    }
  }
}
```

Create the key in **Settings → MCP**. A key acts as you. A standard key refuses the direct-key-only tools and holds the rest of the risky ones for a person's approval; a direct key runs them all immediately, so creating one is the approval and revoking it is the off-switch. See [approvals](api.md#approvals). A key stays masked in Settings, and only its owner can reveal it.

## How the sign-in works

You don't need this to connect. It is for anyone building or debugging an MCP client. Cedric is a standard OAuth 2.1 authorization server, following the MCP authorization spec, so a compliant client connects with no manual setup:

1. The client calls the address with no token and gets `401` with a `WWW-Authenticate` header pointing at the resource metadata.
2. It reads `/.well-known/oauth-protected-resource`, which names this origin as the authorization server, then `/.well-known/oauth-authorization-server` for the endpoints.
3. It registers itself (Dynamic Client Registration, RFC 7591). Public clients only: PKCE, no client secret.
4. It sends you to the authorization endpoint with a PKCE S256 challenge. You sign in and approve on Cedric's consent screen.
5. It exchanges the code and the PKCE verifier for an access token and a refresh token, then calls `tools/list` and `tools/call` with `Authorization: Bearer ...`.

| Endpoint | Purpose |
| --- | --- |
| `/.well-known/oauth-protected-resource` | Resource metadata (RFC 9728) |
| `/.well-known/oauth-authorization-server` | Server metadata (RFC 8414) |
| `/api/oauth/register` | Dynamic client registration |
| `/api/oauth/authorize` | Authorize and consent |
| `/api/oauth/token` | Code exchange and refresh |
| `/api/oauth/revoke` | Token revocation |

All endpoints are under `https://app.meet-cedric.com`. Redirect URIs must be https, an app scheme, or loopback http. Tokens issued this way always run in standard mode. They work on the MCP server and the file upload; the chat endpoint takes an API key.

## Troubleshooting

- **A tool came back "pending approval".** That is by design: posting in a channel, moving an event hook and starting a build wait for a person to approve them in chat or the dashboard. Approve it there, then ask the agent to continue.
- **A tool came back `requires_direct_key`.** Sending mail or DMs, changing the calendar, calling, batching or uploading to a connected app, running code and compiled automations (`schedule_automation`) only run with a direct key. Under a sign-in or a standard key, hand the task to `ask_cedric` instead, or create a direct key in **Settings → MCP**.
- **Cedric says something is waiting in your Action Centre.** Under a sign-in or a standard key, work handed to `ask_cedric` doesn't send on its own: each email, DM, calendar change or app write waits on a card showing exactly what goes out. Press **Send** there.
- **A tool you know from chat is missing.** `dashboard_link`, `connect_telegram`, `connect_discord`, `connect_whatsapp` and `create_event_hook` only work from chat or the dashboard, so `tools/list` leaves them out.
- **A key stopped working: "no longer in the workspace".** Keys and sign-ins belong to a person, and removing them from the workspace revokes both.
- **The connection stopped working after a while.** Access tokens expire and a compliant client refreshes on its own. If yours doesn't, sign in again from the client.
- **You want to cut an agent off.** **Settings → MCP → Connected agents → Disconnect** signs it out everywhere.
- **Registration or sign-in fails.** Check the address is exactly `https://app.meet-cedric.com/api/v1/mcp`, with https, then check your client's own MCP docs.
