#!/usr/bin/env python3
"""Quick script to check what's in the database"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

print("📊 Checking database contents...\n")

# Check sessions
sessions = client.table("sessions").select("*").order("created_at", desc=True).limit(10).execute()
print(f"✅ Found {len(sessions.data)} session(s):")
for s in sessions.data:
    print(f"   - {s['id']}: {s['video_url']} (created: {s['created_at']})")

print()

# Check events
events = client.table("events").select("*").order("created_at", desc=True).limit(10).execute()
print(f"✅ Found {len(events.data)} event(s):")
for e in events.data:
    print(f"   - {e['type']}: session {e['session_id']} (created: {e['created_at']})")

if len(sessions.data) == 0:
    print("\n💡 No sessions found yet. Start a new analysis to create one!")
