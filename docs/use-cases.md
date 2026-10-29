# What to build with Cedric

Worked examples of an agent (or a script) using Cedric's tools. Each one names the calls it makes; parameters are in [tools.md](tools.md).

Each example also says what it needs. **Sign-in** means it works with a browser sign-in or any API key. Some tools only run with a direct key; none of these examples need one, and `ask_cedric` covers that work under a sign-in by asking a person first. See [approvals](api.md#approvals).

## Check what the team decided before writing code

Your coding agent is about to change the pricing logic. Before it guesses, it asks the team's memory, then saves the new decision once it is made.

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

A deploy fails at 2 a.m. The CI job makes one chat call; Cedric reads the context, drafts the message and the issue, and a teammate approves them with one tap in the morning.

```bash
curl -X POST https://app.meet-cedric.com/api/v1/chat \
  -H "Authorization: Bearer $CEDRIC_KEY" -H "Content-Type: application/json" \
  -d '{"message": "The prod deploy failed at the migrate step (log below). Tell #eng what broke and open a Linear issue for it.\n\n..."}'
```

The reply comes back with `"outcome": "proposal_created"` when Cedric raised something for approval.

Needs: an API key (chat takes keys).

## Meeting prep without leaving the terminal

Turn on the pre-meeting brief, send Cedric into the call, and share the notes after.

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

Schedule a standing job and Cedric runs it every week in the workspace, long after your agent's session has ended.

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

## Hand over the whole thing

When the work is open-ended, don't script it. One call, and Cedric plans and uses his own tools.

```json
{ "name": "ask_cedric", "arguments": {
    "message": "Find every customer who emailed about the outage this week, draft a personal reply to each, and hold them for my approval." } }
```

Needs: sign-in. Anything that would send waits for approval.
