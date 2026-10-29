"""One request, one whole Cedric turn: he plans, uses his tools and replies.

    pip install -r requirements.txt
    CEDRIC_KEY=cedric_sk_... python chat.py "Which invoices are overdue this week?"
"""

import os
import sys

import requests

message = sys.argv[1] if len(sys.argv) > 1 else "Summarize this week for the team"

res = requests.post(
    "https://app.meet-cedric.com/api/v1/chat",
    headers={"Authorization": f"Bearer {os.environ['CEDRIC_KEY']}"},
    # Add "session" to continue a conversation, or "new" to start fresh.
    json={"message": message},
    timeout=300,
)
res.raise_for_status()
data = res.json()
print(data["reply"])
print(f"\n(session: {data['session']})")
