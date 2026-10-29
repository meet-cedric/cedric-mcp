# Cedric API

Talk to your Cedric workspace from code: scripts, tests, automations and your own agents. Every caller acts as the person who signed in or owns the key, in their workspace, with their access and the workspace's credits.

Base URL: `https://app.meet-cedric.com`

| Endpoint | What it does |
| --- | --- |
| `POST /api/v1/mcp` | MCP server: Cedric's tools for any MCP client or agent |
| `POST /api/v1/chat` | One request, one whole Cedric turn, reply as JSON |
| `POST /api/v1/files` | Upload local files (videos, images, documents) |

## Authentication

Two ways in, one permission model.

- **Sign in from your agent (OAuth 2.1 with PKCE).** Any MCP client given the MCP address discovers the sign-in by itself: it registers, opens your browser, you approve once, and it keeps a token that refreshes quietly. Metadata lives at `/.well-known/oauth-authorization-server` and `/.well-known/oauth-protected-resource`. These tokens always run in standard mode. Details in [clients.md](clients.md#how-the-sign-in-works).
- **API keys.** For scripts, CI and agents with no browser. Keys look like `cedric_sk_...`, are created in **Settings → MCP**, stay masked until their owner reveals them, and revoking one is the whole off-switch.

```
Authorization: Bearer cedric_sk_...
```

Neither a key nor a sign-in ever reaches another workspace or outranks its owner: it sees exactly your connections, your memory and this workspace's credits.

## MCP: Cedric's tools for your agent

`POST /api/v1/mcp` is a Model Context Protocol server (Streamable HTTP) exposing Cedric's toolbox: memory, channels, connected apps, files, workflows, scheduling and automations. Your agent is the brain; Cedric is the hands. The full list is in [tools.md](tools.md).

It speaks standard MCP: `initialize`, `tools/list`, `tools/call`. Call `getting_started` first; it returns the full guide, including when to act directly and when to hand a whole task to Cedric with `ask_cedric`.

List the tools:

```bash
curl -X POST https://app.meet-cedric.com/api/v1/mcp \
  -H "Authorization: Bearer $CEDRIC_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}'
```

Call one:

```bash
curl -X POST https://app.meet-cedric.com/api/v1/mcp \
  -H "Authorization: Bearer $CEDRIC_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0", "id": 2, "method": "tools/call",
    "params": { "name": "recall_memories", "arguments": { "query": "pricing decisions" } }
  }'
```

With the official MCP SDKs, see [examples/node/mcp-client.mjs](../examples/node/mcp-client.mjs) and [examples/python/mcp_client.py](../examples/python/mcp_client.py).

## Chat: one endpoint, whole turns

`POST /api/v1/chat` runs a normal Cedric turn, the same as every other surface (memory, connected tools, scheduling and credits all apply), and returns the reply as JSON.

```bash
curl -X POST https://app.meet-cedric.com/api/v1/chat \
  -H "Authorization: Bearer $CEDRIC_KEY" \
  -H "Content-Type: application/json" \
  -d '{"message": "Summarize this week for the team"}'
```

```json
{ "reply": "...", "session": "abc123" }
```

Each key talks in its own conversation by default. Pass `"session": "<key>"` to continue a specific session, or `"session": "new"` to start fresh; the response returns the session key for reuse.

```bash
curl -X POST https://app.meet-cedric.com/api/v1/chat \
  -H "Authorization: Bearer $CEDRIC_KEY" \
  -H "Content-Type: application/json" \
  -d '{"message": "Now post it in #team", "session": "abc123"}'
```

## Files: videos, images and documents

A tool call is JSON and has no room for a video, so a file on your machine comes in through `POST /api/v1/files`, with the same key, as multipart form-data: field `files`, up to 5 files per request, 100 MB each. The answer lists each file's `id`. Add `?share=1` to also get a public link.

```bash
curl -X POST https://app.meet-cedric.com/api/v1/files \
  -H "Authorization: Bearer $CEDRIC_KEY" \
  -F "files=@./teaser.mp4"
```

```json
{
  "files": [{ "id": "f_...", "filename": "teaser.mp4", "mimetype": "video/mp4",
              "sizeBytes": 18234001, "url": "...", "expiresInDays": 30 }],
  "refused": []
}
```

Optional form fields: `keep=1` keeps the file for good, `path=brand/videos` puts it in a folder.

```bash
curl -X POST "https://app.meet-cedric.com/api/v1/files?share=1" \
  -H "Authorization: Bearer $CEDRIC_KEY" \
  -F "files=@./deck.pdf" -F "keep=1" -F "path=sales/decks"
```

A file that already has a public link needs no upload: the `upload_file` tool fetches it. Either way the file is kept for 30 days (a year once shared), and its id works everywhere:

- pass it in `file_ids` on `send_channel_message` or `send_dm` to post the file with your text
- `get_file` fetches it back, `read_file` returns the text inside a document
- `manage_file` keeps, renames, moves or deletes it
- `run_code` takes stored files as `input_files`
- `list_files` shows everything the workspace holds

A workspace holds up to 1 GB. A key sees the files its owner may see.

## Approvals

Keys have a mode, chosen when you create them and fixed after:

- **Standard** (the default, and always the mode for browser sign-ins): anything risky, like sending messages or mail, running code or creating standing automations, raises an approval that a person decides in chat or the dashboard. The call returns `pending_approval` with a proposal id; check it with the `proposal_status` tool.
- **Direct:** risky actions run immediately. Creating a direct key is the standing approval (you are automating yourself), and revoking it ends everything.

## Limits

- 30 requests per minute per key.
- Request bodies are capped; long work belongs in sessions.
- Suspended or out-of-credit workspaces refuse API turns with the same message chat gives.
- Turns are metered as normal usage; direct tool calls count per call.

Questions or a missing endpoint? Write to sales@meet-cedric.com.
