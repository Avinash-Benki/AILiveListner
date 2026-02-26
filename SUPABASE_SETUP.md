# Supabase Database Setup

## Quick Setup Instructions

### Option 1: Using Supabase Dashboard (Recommended)

1. **Go to your Supabase project**: https://app.supabase.com
2. **Navigate to SQL Editor** (left sidebar)
3. **Create a new query**
4. **Copy and paste** the contents of `supabase_schema.sql`
5. **Run the query** (click "Run" or press Cmd/Ctrl + Enter)

### Option 2: Using Supabase CLI

If you have the Supabase CLI installed:

```bash
# Make sure you're logged in
supabase login

# Link to your project
supabase link --project-ref YOUR_PROJECT_REF

# Run the migration
supabase db push
```

### Option 3: Using psql (Direct Connection)

```bash
# Get your connection string from Supabase Dashboard > Settings > Database
psql "postgresql://postgres:[YOUR-PASSWORD]@[YOUR-PROJECT-REF].supabase.co:5432/postgres" < supabase_schema.sql
```

## Verify Tables Were Created

After running the schema, verify in Supabase Dashboard:

1. Go to **Table Editor** (left sidebar)
2. You should see two tables:
   - `sessions` - Stores each analysis session
   - `events` - Stores transcripts and analysis results

## Environment Variables

Make sure your `.env` file has:

```env
SUPABASE_URL=https://[YOUR-PROJECT-REF].supabase.co
SUPABASE_KEY=[YOUR-ANON-KEY]
```

You can find these in: **Supabase Dashboard > Settings > API**

## Testing the Database

After setup, start your backend:

```bash
./venv/bin/python3 -m uvicorn src.api:app --host 0.0.0.0 --port 8000
```

Then start a new analysis session. You should see in the logs:
```
[DB] Session created: [UUID]
```

Check your Supabase Dashboard > Table Editor > sessions to see the new row!

## Schema Overview

### `sessions` table
- `id` (UUID) - Primary key
- `video_url` (TEXT) - YouTube URL being analyzed
- `created_at` (TIMESTAMPTZ) - When session started
- `status` (TEXT) - 'active' or 'completed'
- `updated_at` (TIMESTAMPTZ) - Last update time

### `events` table
- `id` (UUID) - Primary key
- `session_id` (UUID) - Foreign key to sessions
- `type` (TEXT) - 'transcript' or 'analysis'
- `content` (JSONB) - The actual data
- `created_at` (TIMESTAMPTZ) - When event occurred

## Troubleshooting

**Error: "relation already exists"**
- Tables are already created, you're good to go!

**Error: "permission denied"**
- Make sure RLS policies are set correctly
- Check that your SUPABASE_KEY has the right permissions

**No data appearing in tables**
- Check that SUPABASE_URL and SUPABASE_KEY are set in `.env`
- Look for `[DB]` logs in your backend console
- Verify the backend is actually calling `db.create_session()`
