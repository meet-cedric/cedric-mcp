// One request, one whole Cedric turn: he plans, uses his tools and replies.
//
//   CEDRIC_KEY=cedric_sk_... node chat.mjs "Draft the Monday report for #team"

const message = process.argv[2] ?? "Summarize this week for the team";

const res = await fetch("https://app.meet-cedric.com/api/v1/chat", {
  method: "POST",
  headers: {
    Authorization: `Bearer ${process.env.CEDRIC_KEY}`,
    "Content-Type": "application/json",
  },
  // Add `session` to continue a conversation, or "new" to start fresh.
  body: JSON.stringify({ message }),
});

if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
const { reply, session } = await res.json();
console.log(reply);
console.log(`\n(session: ${session})`);
