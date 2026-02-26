
import os
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from supabase import create_client, Client

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.url: str = os.environ.get("SUPABASE_URL", "")
        self.key: str = os.environ.get("SUPABASE_KEY", "")
        self.client: Optional[Client] = None
        
        if self.url and self.key:
            try:
                self.client = create_client(self.url, self.key)
                logger.info("[DB] Supabase client initialized")
            except Exception as e:
                logger.error(f"[DB] Failed to initialize Supabase: {e}")
        else:
            logger.warning("[DB] SUPABASE_URL or SUPABASE_KEY missing. Persistence disabled.")

    def create_session(self, video_url: str) -> Optional[str]:
        """Create a new session record and return its ID."""
        if not self.client:
            return None
            
        try:
            data = {
                "video_url": video_url,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "status": "active"
            }
            response = self.client.table("sessions").insert(data).execute()
            if response.data:
                return response.data[0]['id']
        except Exception as e:
            logger.error(f"[DB] Failed to create session: {e}")
            return None

    def log_event(self, session_id: str, event_type: str, content: Dict[str, Any]):
        """Log a transcript or analysis event."""
        if not self.client or not session_id:
            return
            
        try:
            data = {
                "session_id": session_id,
                "type": event_type,  # 'transcript' or 'analysis'
                "content": content,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            self.client.table("events").insert(data).execute()
        except Exception as e:
            logger.error(f"[DB] Failed to log event: {e}")

    def get_recent_events(self, session_id: str, limit: int = 50):
        """Fetch recent events to restore state."""
        if not self.client or not session_id:
            return []
            
        try:
            response = self.client.table("events")\
                .select("*")\
                .eq("session_id", session_id)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            return response.data
        except Exception as e:
            logger.error(f"[DB] Failed to fetch events: {e}")
            return []

    def list_sessions(self, limit: int = 20):
        """List all sessions ordered by creation date."""
        if not self.client:
            return []
            
        try:
            response = self.client.table("sessions")\
                .select("*")\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            return response.data
        except Exception as e:
            logger.error(f"[DB] Failed to list sessions: {e}")
            return []

    def get_session_details(self, session_id: str):
        """Get session with all its events."""
        if not self.client or not session_id:
            return None
            
        try:
            # Get session
            session_response = self.client.table("sessions")\
                .select("*")\
                .eq("id", session_id)\
                .execute()
            
            if not session_response.data:
                return None
                
            session = session_response.data[0]
            
            # Get all events for this session
            events_response = self.client.table("events")\
                .select("*")\
                .eq("session_id", session_id)\
                .order("created_at", desc=False)\
                .execute()
            
            session['events'] = events_response.data
            return session
        except Exception as e:
            logger.error(f"[DB] Failed to get session details: {e}")
            return None
