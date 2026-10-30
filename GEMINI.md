# Cedric

Cedric is the AI employee that lives in a team's chat (Slack, Telegram, Discord). Through the `cedric` MCP server you work in the user's Cedric workspace as them: the same memory, connected apps and approvals as chat.

- The first time Cedric's tools are used, the browser opens to sign in. Run `/mcp auth cedric` if it doesn't.
- Call `getting_started` first. It explains when to act with a single tool and when to hand a whole task to `ask_cedric`.
- A sign-in runs in standard mode. `gmail_send`, `send_dm`, the calendar write tools, `integration_request`, `integration_bulk`, `integration_upload`, `run_recipe`, `run_code` and `schedule_automation` return `requires_direct_key`. Hand that work to `ask_cedric` instead.
- Work handed to `ask_cedric` never sends on its own: each email, DM, calendar change or app write waits on a card in the user's Action Centre until they press Send. Tell the user, and don't resend the request.
- `send_channel_message`, `move_event_hook` and `start_build` return `pending_approval`. Check `proposal_status` until a person decides.

Website: https://meet-cedric.com
Docs: https://github.com/meet-cedric/cedric-mcp and https://meet-cedric.com/docs
