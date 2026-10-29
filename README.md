<p align="center">
  <a href="https://meet-cedric.com"><img src="assets/cedric-logo.png" width="96" height="96" alt="Cedric"></a>
</p>

<h1 align="center">Cedric MCP server</h1>

<p align="center">
  The AI employee that lives where your team talks, as a remote MCP server.<br>
  <a href="https://meet-cedric.com">Website</a> ·
  <a href="docs/clients.md">Connect a client</a> ·
  <a href="docs/tools.md">Tools</a> ·
  <a href="docs/use-cases.md">Use cases</a> ·
  <a href="docs/api.md">API</a> ·
  <a href="https://app.meet-cedric.com">Start free</a>
</p>

[Cedric](https://meet-cedric.com) is an AI employee for Slack, Telegram and Discord. He joins your meetings, works in the tools you connect (HubSpot, Notion, Gmail, Google Calendar, Linear, GitHub, Stripe and 3,000+ more) and asks before anything is sent or changed.

This repo is how you reach him from code. Cedric is a remote MCP server, so Claude Code, Cursor, VS Code, Claude, ChatGPT, Codex CLI, Gemini CLI, Windsurf or your own agent can use his 129 tools: team memory, channels, connected apps, meetings, files, workflows and scheduling. Your agent is the brain; Cedric is the hands.

| | |
| --- | --- |
| **Endpoint** | `https://app.meet-cedric.com/api/v1/mcp` |
| **Transport** | Streamable HTTP |
| **Auth** | Either way works: sign in once in the browser (OAuth 2.1 with PKCE, nothing to paste), or send an API key `cedric_sk_...` |
| **Account** | Free to start, no card: [app.meet-cedric.com](https://app.meet-cedric.com) |

## Quick start

Claude Code:

```bash
claude mcp add --transport http cedric https://app.meet-cedric.com/api/v1/mcp
# then run /mcp, pick cedric, and choose Authenticate
```

Cursor (`~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "cedric": { "url": "https://app.meet-cedric.com/api/v1/mcp" }
  }
}
```

VS Code:

```bash
code --add-mcp '{"name":"cedric","type":"http","url":"https://app.meet-cedric.com/api/v1/mcp"}'
```

Claude, ChatGPT, Codex CLI, Gemini CLI, Windsurf and API keys: see **[docs/clients.md](docs/clients.md)**.

Once connected, call the `getting_started` tool. It returns the full guide, including when to act directly and when to hand a whole task to Cedric with `ask_cedric`.

## What your agent can do with Cedric

A few of the [129 tools](docs/tools.md):

| Area | Tools |
| --- | --- |
| Hand over a whole task | `ask_cedric` |
| Team memory | `remember`, `recall_memories`, `search_workspace` |
| Chat | `read_channel`, `send_channel_message`, `send_dm`, `post_vote` |
| Connected apps | `list_connectors`, `integration_request`, `run_recipe` |
| Email and calendar | `gmail_search`, `gmail_send`, `calendar_free_busy`, `calendar_create_event` |
| Meetings | `join_call`, `share_meeting_notes`, `meeting_brief` |
| Schedules and workflows | `schedule_task`, `start_workflow`, `watch_app`, `watch_source` |
| Files and documents | `upload_file`, `read_file`, `create_document`, `create_presentation`, `create_spreadsheet` |

Most tools run as soon as you call them. Under a browser sign-in or a standard key, two kinds don't:

- **Direct key only:** sending mail or DMs, changing the calendar, calling a connected app's API (`integration_request`, `run_recipe`), running code and compiled automations (`schedule_automation`) are refused with `requires_direct_key`. Use a direct key, or hand the task to `ask_cedric`, which asks a person before anything goes out.
- **Needs approval:** posting in a channel, moving an event hook and starting a build return `pending_approval` until a person approves.

See [approvals](docs/api.md#approvals).

## What people build with it

- **"What did we decide?" from the editor.** Before touching the pricing code, your coding agent asks `recall_memories` and gets the team's actual decision, not a guess.
- **Ship and tell.** When a PR merges, the agent writes the summary, `send_channel_message` posts it in #eng once a teammate approves, and `remember` keeps the decision for next time.
- **CI that speaks up.** A failed deploy calls `/api/v1/chat`: "Tell #eng what broke and open a Linear issue." Cedric drafts both and a teammate approves with one tap.
- **Settle it with a vote.** `post_vote` asks the channel which name to ship, and `vote_results` brings the tally back to your agent.

More, with the calls spelled out: **[docs/use-cases.md](docs/use-cases.md)**.

## Use it from code

The official MCP SDKs connect with an API key from Cedric's **Settings → MCP**.

TypeScript ([examples/node/mcp-client.mjs](examples/node/mcp-client.mjs)):

```js
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";

const transport = new StreamableHTTPClientTransport(
  new URL("https://app.meet-cedric.com/api/v1/mcp"),
  { requestInit: { headers: { Authorization: `Bearer ${process.env.CEDRIC_KEY}` } } },
);
const client = new Client({ name: "my-agent", version: "1.0.0" });
await client.connect(transport);

const { tools } = await client.listTools();
const result = await client.callTool({
  name: "recall_memories",
  arguments: { query: "pricing decisions" },
});
```

Python ([examples/python/mcp_client.py](examples/python/mcp_client.py)):

```python
from mcp import ClientSession
from mcp.client.streamable_http import create_mcp_http_client, streamable_http_client

http = create_mcp_http_client(headers={"Authorization": f"Bearer {key}"})
async with http, streamable_http_client(URL, http_client=http) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        result = await session.call_tool("recall_memories", {"query": "pricing decisions"})
```

No agent of your own? One HTTP call with an API key runs a whole Cedric turn ([examples/node/chat.mjs](examples/node/chat.mjs), [examples/python/chat.py](examples/python/chat.py)):

```bash
curl -X POST https://app.meet-cedric.com/api/v1/chat \
  -H "Authorization: Bearer $CEDRIC_KEY" \
  -H "Content-Type: application/json" \
  -d '{"message": "Summarize this week for the team"}'

# { "reply": "...", "session": "abc123", "outcome": "answered" }
```

Chat sessions, file uploads, approvals and limits: **[docs/api.md](docs/api.md)**.

## In this repo

```
docs/clients.md          setup for every MCP client, API keys, how the sign-in works
docs/tools.md            every tool, grouped, with its parameters
docs/use-cases.md        worked examples of what to build with Cedric
docs/api.md              MCP, chat and files endpoints, approvals, limits
examples/node/           MCP SDK client and chat call (TypeScript SDK)
examples/python/         MCP SDK client and chat call (Python SDK)
examples/curl/cedric.sh  the whole API from the shell
server.json              the MCP Registry entry
```

## Links

- Website: [meet-cedric.com](https://meet-cedric.com)
- Docs: [meet-cedric.com/docs](https://meet-cedric.com/docs)
- Connect other MCP servers to Cedric: [bring your own tools](https://meet-cedric.com/docs/bring-your-own-tools)
- Pricing: [meet-cedric.com/pricing](https://meet-cedric.com/pricing)
- Security: [meet-cedric.com/security](https://meet-cedric.com/security)
- Contact: sales@meet-cedric.com

Cedric is built in Zurich, Switzerland, by SFF Studio. The examples and docs in this repo are MIT licensed; the Cedric service itself is not open source.
