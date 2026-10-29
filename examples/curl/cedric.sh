#!/usr/bin/env bash
# The Cedric API from the shell.
#
#   export CEDRIC_KEY=cedric_sk_...
#   ./cedric.sh tools                 # list the MCP tools
#   ./cedric.sh call recall_memories '{"query":"pricing decisions"}'
#   ./cedric.sh chat "Summarize this week for the team"
#   ./cedric.sh upload ./teaser.mp4
set -euo pipefail

BASE="https://app.meet-cedric.com"
AUTH="Authorization: Bearer ${CEDRIC_KEY:?set CEDRIC_KEY}"

mcp() {
  curl -sS -X POST "$BASE/api/v1/mcp" -H "$AUTH" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json, text/event-stream" \
    -d "$1"
}

case "${1:-}" in
  tools)
    mcp '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' ;;
  call)
    args="${3:-}"; [ -n "$args" ] || args='{}'
    mcp "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/call\",\"params\":{\"name\":\"$2\",\"arguments\":$args}}" ;;
  chat)
    curl -sS -X POST "$BASE/api/v1/chat" -H "$AUTH" -H "Content-Type: application/json" \
      -d "$(printf '{"message": %s}' "$(printf '%s' "$2" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')")" ;;
  upload)
    curl -sS -X POST "$BASE/api/v1/files" -H "$AUTH" -F "files=@$2" ;;
  *)
    sed -n '2,9p' "$0"; exit 1 ;;
esac
