// Connect to Cedric with the official MCP TypeScript SDK, list his tools,
// and call one.
//
//   npm install
//   CEDRIC_KEY=cedric_sk_... node mcp-client.mjs

import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";

const transport = new StreamableHTTPClientTransport(
  new URL("https://app.meet-cedric.com/api/v1/mcp"),
  { requestInit: { headers: { Authorization: `Bearer ${process.env.CEDRIC_KEY}` } } },
);

const client = new Client({ name: "my-agent", version: "1.0.0" });
await client.connect(transport);

const { tools } = await client.listTools();
console.log(`${tools.length} tools, for example:`, tools.slice(0, 5).map((t) => t.name));

// Search the team's memory.
const result = await client.callTool({
  name: "recall_memories",
  arguments: { query: "pricing decisions" },
});
console.log(result.content.map((c) => c.text).join("\n"));

await client.close();
