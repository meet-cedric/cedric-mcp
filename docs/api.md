# Cedric API

Talk to your Cedric workspace from code: scripts, tests, automations and your own agents. Every caller acts as the person who signed in or owns the key, in their workspace, with their access and the workspace's credits.

Base URL: `https://app.meet-cedric.com`

| Endpoint | What it does | Takes |
| --- | --- | --- |
| `POST /api/v1/mcp` | MCP server: Cedric's tools for any MCP client or agent | Sign-in or API key |
| `POST /api/v1/chat` | One request, one whole Cedric turn, reply as JSON | API key |
| `POST /api/v1/files` | Upload local files (videos, images, documents) | Sign-in or API key |

## Authentication

Two ways in, one permission model. Use whichever suits the caller; the MCP server takes both.

- **Sign in from your agent (OAuth 2.1 with PKCE).** Any MCP client given the MCP address discovers the sign-in by itself: it registers, opens your browser, you approve once, and it keeps a token that refreshes quietly. Metadata lives at `/.well-known/oauth-authorization-server` and `/.well-known/oauth-protected-resource`. These tokens always run in standard mode (see [approvals](#approvals)). Details in [clients.md](clients.md#how-the-sign-in-works).
- **API keys.** For scripts, CI and agents with no browser, and the only way into `/api/v1/chat`. Keys look like `cedric_sk_...`, are created in **Settings → MCP**, stay masked until their owner reveals them, and revoking one is the whole off-switch.

```
Authorization: Bearer cedric_sk_...
```

Neither a key nor a sign-in ever reaches another workspace or outranks its owner: it sees exactly your connections, your memory and this workspace's credits. Both belong to a person, so removing someone from the workspace revokes their keys and agent sign-ins.

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

Every tool in `tools/list` carries a `title` and the standard behaviour labels in `annotations`: `readOnlyHint` (changes nothing), `destructiveHint` (can delete or overwrite), `idempotentHint` (the same call again has no further effect) and `openWorldHint` (reaches outside Cedric: mail, calendar, chat, connected apps, the web, or a public link). Clients can use them to tell a read from a write before calling. [tools.md](tools.md) shows the same labels as the Effect column.

Tools from MCP servers your workspace connected to Cedric are listed too, as `mcp__<key>__<tool>`, with the labels their own server gives them (or, when it gives none, labels read from the name, counting anything that is not plainly a read as able to delete or overwrite). A file a tool makes comes back with its `id` and a link, ready for `send_channel_message`, `get_file` or `manage_file`.

## Chat: one endpoint, whole turns

`POST /api/v1/chat` runs a normal Cedric turn, the same as every other surface (memory, connected tools, scheduling and credits all apply), and returns the reply as JSON. It takes an API key; a message can be up to 8,000 characters.

```bash
curl -X POST https://app.meet-cedric.com/api/v1/chat \
  -H "Authorization: Bearer $CEDRIC_KEY" \
  -H "Content-Type: application/json" \
  -d '{"message": "Summarize this week for the team"}'
```

```json
{ "reply": "...", "session": "abc123", "outcome": "answered" }
```

`outcome` is usually `answered`. It is `proposal_created` when the turn raised something for a person to approve (a key can raise an approval but never grant one), and `budget_blocked` when the workspace is out of credits. When the turn made files, a `files` list carries each one's `filename` and `url`.

Each key talks in its own conversation by default. Pass `"session": "<key>"` to continue a specific session, or `"session": "new"` to start fresh; the response returns the session key for reuse.

```bash
curl -X POST https://app.meet-cedric.com/api/v1/chat \
  -H "Authorization: Bearer $CEDRIC_KEY" \
  -H "Content-Type: application/json" \
  -d '{"message": "Now post it in #team", "session": "abc123"}'
```

## Files: videos, images and documents

A tool call is JSON and has no room for a video, so a file on your machine comes in through `POST /api/v1/files`, with the same key or sign-in token, as multipart form-data: field `files`, up to 5 files per request, 100 MB each. The answer lists each file's `id`. Add `?share=1` to also get a public link.

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

With `?share=1`, each stored file also carries a `shareUrl`, and its `expiresInDays` becomes 365. A file that could not be stored is listed in `refused` with the reason, and the others still go through.

Optional form fields: `keep=1` keeps the file for good (`expiresInDays` is then `null`), `path=brand/videos` puts it in a folder.

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

- **Standard** (the default, and always the mode for browser sign-ins). Most tools run as soon as you call them. Two kinds don't:
  - **Direct key only:** `gmail_send`, `send_dm`, `calendar_create_event`, `calendar_update_event`, `calendar_delete_event`, `integration_request`, `integration_bulk`, `integration_upload`, `run_recipe`, `run_code` and `schedule_automation`. The call does nothing and returns `"status": "requires_direct_key"`. Use a direct key, or hand the task to `ask_cedric` (see [work you hand to Cedric](#work-you-hand-to-cedric)).
  - **Needs approval:** `send_channel_message`, `move_event_hook` and `start_build`. The call returns `"status": "pending_approval"` with a `proposalId`, and a person decides in chat or the dashboard. Check it with the `proposal_status` tool.
- **Direct:** every one of these runs immediately. Creating a direct key is the standing approval (you are automating yourself), and revoking it ends everything.

### Work you hand to Cedric

An `ask_cedric` call or a `/api/v1/chat` turn under a standard key or a sign-in runs Cedric's reads straight away. Every send and every write to a connected app (email, DMs, calendar changes, app calls, recipes, code, automations, and also file deletes and workspace profile edits) goes on a card in the key owner's **Action Centre** instead of running. The card shows the exact call, and it runs once, when the owner presses **Send**. Cedric's reply says what is waiting there; resending the request does not push it through. With a direct key, the same work runs immediately.

### Never over the API

Whatever the mode, five tools never run over the API, and `tools/list` leaves them out: `dashboard_link`, `connect_telegram`, `connect_discord`, `connect_whatsapp` and `create_event_hook`. Each would create access wider than the key, so they work only from chat or the dashboard. Connecting a tool server for the whole team stays an admin's job in chat or the dashboard: through the API, `connect_mcp` connects one for you only.

## Limits

- MCP and file uploads: 60 requests per minute per key, shared between the two.
- Chat: 30 requests per minute per key.
- A chat message can be up to 8,000 characters; an MCP request body up to 200,000. Long work belongs in sessions.
- Suspended or out-of-credit workspaces refuse API turns with the same message chat gives.
- Turns are metered as normal usage; direct tool calls count per call.

Questions or a missing endpoint? Write to sales@meet-cedric.com.
