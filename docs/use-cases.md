# What to build with Cedric

Worked examples of an agent (or a script) using Cedric's tools. Each one names the calls it makes; parameters are in [tools.md](tools.md).

Each example also says what it needs. **Sign-in** means it works with a browser sign-in or any API key. Some tools only run with a direct key; only one example below needs one, and `ask_cedric` covers that work under a sign-in: each send waits in your Action Centre until you press Send. See [approvals](api.md#approvals) and [how approvals work](https://meet-cedric.com/docs/how-approvals-work).

## Check what the team decided before writing code

Your coding agent is about to change the pricing logic. Before it guesses, it asks the team's memory, then saves the new decision once it is made. How Cedric keeps it: [the company brain](https://meet-cedric.com/docs/the-company-brain).

```json
{ "name": "recall_memories", "arguments": { "query": "annual plan discount decision" } }
{ "name": "search_workspace", "arguments": { "query": "pricing page copy" } }
{ "name": "remember", "arguments": {
    "title": "Annual plan discount",
    "content": "Annual plans get two months free, decided in the 2026-10 pricing review." } }
```

Needs: sign-in.

## Ship and tell

A PR merges. The agent writes the summary itself and posts it where the team reads. The post waits for one tap of approval from a teammate.

```json
{ "name": "send_channel_message", "arguments": {
    "to": "#eng",
    "message": "Shipped: CSV export on the reports page. Try it under Reports, then Export." } }
```

The call returns `pending_approval` with a `proposalId`. Your agent can check it with `proposal_status` and move on once it is `executed`.

Needs: sign-in.

## A demo video from your laptop to Slack

A tool call is JSON, so the file goes up first, then the message carries its id.

```bash
curl -X POST https://app.meet-cedric.com/api/v1/files \
  -H "Authorization: Bearer $CEDRIC_KEY" -F "files=@./demo.mp4"
# { "files": [{ "id": "f_...", ... }], "refused": [] }
```

```json
{ "name": "send_channel_message", "arguments": {
    "to": "#launch", "message": "Here is the cut for Thursday.", "file_ids": ["f_..."] } }
```

Needs: sign-in.

## Settle it with a vote

Three names for the feature, nobody agrees. The agent puts it to the channel and reads the result back.

```json
{ "name": "post_vote", "arguments": {
    "question": "Which name do we ship?", "options": ["Pulse", "Signal", "Beacon"], "to": "#product" } }
{ "name": "vote_results", "arguments": {} }
```

Needs: sign-in. Votes post in Slack.

## CI that speaks up

A deploy fails at 2 a.m. The CI job makes one chat call; Cedric reads the context and drafts the message and the issue. Nothing goes out at night: the post waits for a teammate's approval in chat, and the Linear issue waits on a card in the key owner's Action Centre until they press Send.

```bash
curl -X POST https://app.meet-cedric.com/api/v1/chat \
  -H "Authorization: Bearer $CEDRIC_KEY" -H "Content-Type: application/json" \
  -d '{"message": "The prod deploy failed at the migrate step (log below). Tell #eng what broke and open a Linear issue for it.\n\n..."}'
```

The reply comes back with `"outcome": "proposal_created"` when Cedric raised a post for approval, and its text says what waits in the Action Centre. With a direct key, both go out at once.

Needs: an API key (chat takes keys).

## Meeting prep without leaving the terminal

Turn on the pre-meeting brief, send Cedric into the call, and share the notes after. What he does in a call: [Cedric in meetings](https://meet-cedric.com/docs/cedric-in-meetings).

```json
{ "name": "meeting_brief", "arguments": { "on": true } }
{ "name": "join_call", "arguments": {
    "meeting_url": "https://meet.google.com/abc-defg-hij",
    "purpose": "Weekly pipeline review: track decisions and owners" } }
{ "name": "share_meeting_notes", "arguments": { "meeting": "Weekly pipeline review" } }
```

Needs: sign-in.

## Watch a competitor

Point Cedric at a pricing page once; ask what changed whenever you like.

```json
{ "name": "watch_source", "arguments": {
    "url": "https://example.com/pricing", "kind": "page", "label": "Competitor pricing", "interval_hours": 24 } }
{ "name": "pull_updates", "arguments": { "hours": 168 } }
```

Needs: sign-in.

## Monday metrics, set up once

Schedule a standing job and Cedric runs it every week in the workspace, long after your agent's session has ended. More in [recurring work and automations](https://meet-cedric.com/docs/recurring-work-and-automations).

```json
{ "name": "schedule_task", "arguments": {
    "prompt": "Pull last week's MRR and new customers from Stripe and post a short summary in #team.",
    "cron": "0 9 * * 1", "tz": "Europe/Zurich" } }
```

Needs: sign-in.

## User research by voice

Make a short spoken interview, share the link, and read the transcripts when people have answered.

```json
{ "name": "create_voice_interview", "arguments": {
    "title": "Why did you pick us?",
    "context": "Customers who signed up in the last 30 days. We want to know what made them choose us and what almost stopped them.",
    "max_minutes": 5 } }
{ "name": "get_voice_interview_results", "arguments": { "interview_id": "..." } }
```

Needs: sign-in.

## Find a slot and book it

Your agent finds when everyone is free, then books the meeting with a video link and sends the invites.

```json
{ "name": "calendar_free_busy", "arguments": {
    "time_min": "2026-11-03T08:00:00+01:00", "time_max": "2026-11-05T18:00:00+01:00",
    "emails": ["ana@example.com", "tom@example.com"] } }
{ "name": "calendar_create_event", "arguments": {
    "title": "Q4 roadmap review",
    "start": "2026-11-04T14:00:00+01:00", "end": "2026-11-04T14:45:00+01:00",
    "attendees": ["ana@example.com", "tom@example.com"], "video": true, "confirmed": true } }
```

Times need a UTC offset. Busy blocks come back without titles.

Needs: a direct key for the booking. Under a sign-in, ask `ask_cedric` to book it instead, and the invite waits in your Action Centre until you press Send.

## Collect answers with a form

The agent needs everyone's input before the offsite. One call makes a form with a personal link for each person; the answers come back to the agent.

```json
{ "name": "create_form", "arguments": {
    "title": "Offsite: what should we cover?",
    "fields": [
      { "key": "topic", "label": "The one topic we must cover", "type": "text", "required": true },
      { "key": "format", "label": "Preferred format", "type": "select", "options": ["Talks", "Workshops", "Mixed"] },
      { "key": "notes", "label": "Anything else", "type": "textarea" } ],
    "recipients": [ { "key": "ana", "name": "Ana" }, { "key": "tom", "name": "Tom" } ],
    "closes_at": "2026-11-07T18:00:00+01:00" } }
{ "name": "list_form_submissions", "arguments": { "form_id": "..." } }
```

Share the links in a channel or a DM. Each answer also fires a workflow event, so a form paired with `start_workflow` (pass the run in `run_id`) wakes that workflow as answers arrive.

Needs: sign-in.

## A launch board the team can move

Your agent turns a launch plan into a board anyone with the link can open, move cards on and add to. Later it reads the board back to see what moved.

```json
{ "name": "board", "arguments": {
    "action": "create", "title": "November launch",
    "columns": ["Todo", "Doing", "Done"],
    "cards": [
      { "title": "Final pricing page copy", "column": "Doing", "assignee": "Ana", "due": "2026-11-10" },
      { "title": "Launch email", "column": "Todo", "assignee": "Tom", "due": "2026-11-12" },
      { "title": "Demo video", "column": "Todo" } ] } }
{ "name": "board", "arguments": { "action": "read", "board_id": "..." } }
```

`query_records` filters and groups the cards ("everything due this week, by assignee"), for a status line in your agent's own report.

Needs: sign-in.

## Turn numbers into a deck

Your agent has the quarter's figures. One call turns them into a real PowerPoint file, ready to share.

```json
{ "name": "create_presentation", "arguments": {
    "title": "Q3 in review",
    "slides": [
      { "title": "Q3 in review", "body": "Sales and product, July to September" },
      { "title": "Revenue", "bullets": ["MRR up 18% to $84k", "Net revenue retention 112%", "Three new enterprise accounts"] },
      { "title": "Next quarter", "bullets": ["Self-serve annual plans", "EU data residency", "Hire two account executives"] } ] } }
```

A first slide without bullets becomes the cover. `create_spreadsheet`, `create_document` (PDF) and `create_chart_page` (a web page of charts and headline figures) work the same way. Every file comes back with an id you can post with `send_channel_message`.

Needs: sign-in.

## Bring your own tools

Connect another MCP server to Cedric once, and its tools sit next to his for every later call, from your agent and from chat.

```json
{ "name": "connect_mcp", "arguments": {
    "url": "https://mcp.example.com/mcp", "token": "...", "name": "Example CRM" } }
```

Cedric checks the server before saving it. Its tools then show up in `tools/list` as `mcp__<key>__<tool>`, with the labels that server gives them. Over the API a server is connected for you only; connecting one for the whole team is an admin's job in chat or the dashboard. See [bring your own tools](https://meet-cedric.com/docs/bring-your-own-tools).

Needs: sign-in.

## Hand over the whole thing

When the work is open-ended, don't script it. One call, and Cedric plans and uses his own tools.

```json
{ "name": "ask_cedric", "arguments": {
    "message": "Find every customer who emailed about the outage this week, draft a personal reply to each, and hold them for my approval." } }
```

Needs: sign-in. Each reply waits in your Action Centre until you press Send.

## More

The same work from chat instead of code: [use cases](https://meet-cedric.com/use-cases), [ready-made agents](https://meet-cedric.com/agent-gallery) and the [apps Cedric connects to](https://meet-cedric.com/integrations).
