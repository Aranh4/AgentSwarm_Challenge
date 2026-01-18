"""
Session Manager - In-memory session storage for user context
Provides lightweight caching of user data and message history to reduce latency
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import deque
import threading


class SessionManager:
    """Manages in-memory user sessions with auto-expiration"""
    
    def __init__(self, expiration_minutes: int = 30):
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        self.expiration_minutes = expiration_minutes
    
    def get_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve session data for a user if it exists and hasn't expired
        
        Returns:
            Session data dict or None if expired/not found
        """
        with self._lock:
            if user_id not in self._sessions:
                return None
            
            session = self._sessions[user_id]
            last_accessed = session.get("last_accessed")
            
            # Check expiration
            if last_accessed:
                elapsed = datetime.now() - last_accessed
                if elapsed > timedelta(minutes=self.expiration_minutes):
                    del self._sessions[user_id]
                    return None
            
            # Update access time
            session["last_accessed"] = datetime.now()
            return session.copy()
    
    def update_session(self, user_id: str, data: Dict[str, Any]):
        """
        Update or create session with user data
        
        Args:
            user_id: User identifier
            data: Dict containing user context (name, balance, transactions, etc.)
        """
        with self._lock:
            if user_id not in self._sessions:
                self._sessions[user_id] = {
                    "message_history": deque(maxlen=5),
                    "last_accessed": datetime.now()
                }
            
            session = self._sessions[user_id]
            session.update(data)
            session["last_accessed"] = datetime.now()
    
    def add_message(self, user_id: str, query: str, response: str):
        """
        Add a message exchange to the session history
        
        Args:
            user_id: User identifier
            query: User's query
            response: Agent's response
        """
        with self._lock:
            if user_id not in self._sessions:
                self._sessions[user_id] = {
                    "message_history": deque(maxlen=5),
                    "last_accessed": datetime.now()
                }
            
            session = self._sessions[user_id]
            session["message_history"].append({
                "query": query,
                "response": response,
                "timestamp": datetime.now().isoformat()
            })
            session["last_accessed"] = datetime.now()
    
    def get_message_history(self, user_id: str) -> List[Dict[str, str]]:
        """Get recent message history for context"""
        session = self.get_session(user_id)
        if session and "message_history" in session:
            return list(session["message_history"])
        return []
    
    def clear_session(self, user_id: str):
        """Manually clear a user's session"""
        with self._lock:
            if user_id in self._sessions:
                del self._sessions[user_id]
    
    def cleanup_expired(self):
        """Remove all expired sessions (called periodically)"""
        with self._lock:
            expired_users = []
            now = datetime.now()
            
            for user_id, session in self._sessions.items():
                last_accessed = session.get("last_accessed")
                if last_accessed:
                    elapsed = now - last_accessed
                    if elapsed > timedelta(minutes=self.expiration_minutes):
                        expired_users.append(user_id)
            
            for user_id in expired_users:
                del self._sessions[user_id]
            
            return len(expired_users)


# Global session manager instance
session_manager = SessionManager(expiration_minutes=30)
