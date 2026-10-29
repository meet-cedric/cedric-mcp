"""Rebuild docs/tools.md from the live server's tools/list.

    CEDRIC_KEY=cedric_sk_... python scripts/build-tools-doc.py

Tools from external MCP servers a workspace connected (names starting
with "mcp__") are left out: they belong to that workspace, not to Cedric.
"""

import json
import os
import re
import sys
import urllib.request

URL = "https://app.meet-cedric.com/api/v1/mcp"
OUT = os.path.join(os.path.dirname(__file__), "..", "docs", "tools.md")

GROUPS = [
    ("Start here", ["getting_started", "ask_cedric", "about_cedric", "explore_capabilities"]),
    ("Connected apps", ["list_connectors", "get_connect_link", "ask_to_connect", "integration_request",
                        "integration_upload", "integration_bulk", "run_recipe"]),
    ("Email and calendar", ["gmail_search", "gmail_get_thread", "gmail_send", "calendar_list_events",
                            "calendar_free_busy", "calendar_create_event", "calendar_update_event",
                            "calendar_delete_event"]),
    ("Memory and knowledge", ["remember", "recall_memories", "list_memories", "delete_memory",
                              "set_memory_audience", "search_workspace", "read_knowledge_source",
                              "update_person_profile", "update_workspace_profile", "record_learning",
                              "retire_learning", "set_preference"]),
    ("Chat and channels", ["list_channels", "channel_members", "read_channel", "send_channel_message",
                           "send_dm", "edit_message", "delete_message", "set_channel_privacy",
                           "ask_with_options", "post_vote", "vote_results", "connect_telegram",
                           "connect_discord", "connect_whatsapp"]),
    ("Meetings", ["join_call", "set_meeting_screen", "share_meeting_notes", "meeting_brief",
                  "list_precall_asks", "answer_precall_ask", "meeting_open_asks", "answer_meeting_question",
                  "approve_card", "dismiss_card", "stop_nudges", "nudge_later", "mark_item_done",
                  "stop_chasing", "chase_later"]),
    ("Schedules, workflows and automations", ["schedule_task", "list_scheduled_tasks", "cancel_scheduled_task",
                                              "schedule_automation", "start_workflow", "workflow_checkpoint",
                                              "finish_workflow", "list_workflows", "cancel_workflow",
                                              "send_workflow_event", "watch_app", "list_watches", "stop_watch",
                                              "create_event_hook", "list_event_hooks", "update_event_hook",
                                              "delete_event_hook", "move_event_hook", "proposal_status"]),
    ("Web sources", ["watch_source", "list_watched_sources", "unwatch_source", "pull_updates", "pull_metrics"]),
    ("Files", ["list_files", "get_file", "find_shared_files", "upload_file", "read_file", "convert_file",
               "manage_file", "publish_attachment"]),
    ("Documents, pages and media", ["create_document", "create_presentation", "create_spreadsheet",
                                    "create_text_file", "create_html_page", "update_html_page", "create_page",
                                    "update_page", "create_chart_page", "board", "query_records", "create_form",
                                    "list_forms", "list_form_submissions", "create_social_preview",
                                    "create_post_image", "create_ad_recommendations", "create_video",
                                    "update_video", "create_voice_interview", "list_voice_interviews",
                                    "get_voice_interview_results", "close_voice_interview"]),
    ("Code and builds", ["run_code", "pair_builder", "start_build", "steer_build", "stop_build",
                         "answer_build_ask", "builds_status", "build_changes"]),
    ("Skills and other MCP servers", ["list_skills", "get_skill", "save_skill", "connect_mcp",
                                      "list_mcp_servers", "disconnect_mcp"]),
    ("Workspace", ["dashboard_link", "referral_link", "update_task_doc", "archive_task_doc", "send_feedback"]),
]

# Wording fixes for the public page (Cedric is "he").
FIXES = {"what it learns": "what he learns"}


def fetch_tools():
    key = os.environ.get("CEDRIC_KEY")
    if not key:
        sys.exit("Set CEDRIC_KEY to a cedric_sk_... key.")
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list"}).encode()
    req = urllib.request.Request(URL, data=body, method="POST", headers={
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    })
    with urllib.request.urlopen(req) as res:
        text = res.read().decode()
    if not text.lstrip().startswith("{"):
        text = [line[5:] for line in text.splitlines() if line.startswith("data:")][-1]
    return json.loads(text)["result"]["tools"]


def summary(desc):
    text = " ".join(desc.split())
    # First sentence, not fooled by "e.g." or "i.e.".
    masked = re.sub(r"\b(e\.g|i\.e|etc|vs)\.", lambda m: m.group(0).replace(".", "\0"), text)
    first = re.split(r"(?<=[.!?])\s", masked, maxsplit=1)[0].replace("\0", ".")
    for old, new in FIXES.items():
        first = first.replace(old, new)
    return first.replace("|", "\\|")


def params(schema):
    props = (schema or {}).get("properties", {})
    required = set((schema or {}).get("required", []))
    names = [f"`{p}`" if p in required else f"`{p}`?" for p in props]
    return ", ".join(names) if names else "none"


def main():
    tools = {t["name"]: t for t in fetch_tools() if not t["name"].startswith("mcp__")}
    grouped = {n for _, names in GROUPS for n in names}
    missing = sorted(set(tools) - grouped)
    groups = GROUPS + ([("Other", missing)] if missing else [])

    lines = [
        "# Cedric MCP tools",
        "",
        f"The {len(tools)} tools the Cedric server exposes at `{URL}`, grouped by what they do. "
        "Every call acts as the signed-in person, inside their workspace.",
        "",
        "Parameters marked `?` are optional. Call `getting_started` first: it returns the full usage "
        "guide over the wire, and `tools/list` returns each tool's complete input schema.",
        "",
        "Risky tools (sending messages or mail, running code, creating automations) return "
        "`pending_approval` under a standard key or browser sign-in, until a person approves. "
        "See [approvals](api.md#approvals).",
        "",
        "Generated by `scripts/build-tools-doc.py` from the live `tools/list`.",
        "",
    ]
    for title, names in groups:
        present = [n for n in names if n in tools]
        if not present:
            continue
        lines += [f"## {title}", "", "| Tool | What it does | Parameters |", "| --- | --- | --- |"]
        for n in present:
            t = tools[n]
            lines.append(f"| `{n}` | {summary(t.get('description', ''))} | {params(t.get('inputSchema'))} |")
        lines.append("")
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))
    print(f"{len(tools)} tools written to docs/tools.md" + (f"; ungrouped: {missing}" if missing else ""))


if __name__ == "__main__":
    main()
