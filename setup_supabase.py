#!/usr/bin/env python3
"""
Setup script to create Supabase tables for AI Live Listener
Run this once to initialize your database schema.
"""

import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
    exit(1)

print(f"🔗 Connecting to Supabase: {SUPABASE_URL}")

try:
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Connected to Supabase successfully!")
    
    # Read the SQL schema
    with open("supabase_schema.sql", "r") as f:
        schema_sql = f.read()
    
    print("\n📋 Executing schema SQL...")
    print("=" * 60)
    
    # Execute the schema
    # Note: Supabase Python client doesn't directly support raw SQL execution
    # You need to use the SQL Editor in Supabase Dashboard or use psql
    
    print("\n⚠️  IMPORTANT: The Supabase Python client doesn't support raw SQL execution.")
    print("\nPlease follow these steps:")
    print("\n1. Go to: https://app.supabase.com")
    print("2. Select your project")
    print("3. Click 'SQL Editor' in the left sidebar")
    print("4. Click 'New Query'")
    print("5. Copy and paste the contents of 'supabase_schema.sql'")
    print("6. Click 'Run' (or press Cmd/Ctrl + Enter)")
    print("\n" + "=" * 60)
    
    # Try to check if tables exist by querying them
    print("\n🔍 Checking if tables already exist...")
    
    try:
        sessions = client.table("sessions").select("id").limit(1).execute()
        print("✅ 'sessions' table exists!")
    except Exception as e:
        print(f"❌ 'sessions' table not found: {str(e)}")
        print("   → You need to create it using the SQL Editor")
    
    try:
        events = client.table("events").select("id").limit(1).execute()
        print("✅ 'events' table exists!")
    except Exception as e:
        print(f"❌ 'events' table not found: {str(e)}")
        print("   → You need to create it using the SQL Editor")
    
    print("\n" + "=" * 60)
    print("\n📖 For detailed setup instructions, see: SUPABASE_SETUP.md")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nPlease check:")
    print("1. Your SUPABASE_URL is correct")
    print("2. Your SUPABASE_KEY is the 'anon' or 'service_role' key from:")
    print("   Supabase Dashboard > Settings > API")
    exit(1)
