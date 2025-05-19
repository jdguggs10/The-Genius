"""
Authentication module for ESPN Fantasy Baseball MCP Server
Handles session management and credential storage
"""

import sys
from typing import Dict, Optional
from utils import log_error

class AuthService:
    """Manages authentication credentials for ESPN access"""
    
    def __init__(self):
        self.credentials: Dict[str, Dict[str, str]] = {}
    
    def store_credentials(self, session_id: str, espn_s2: str, swid: str) -> Dict[str, str]:
        """Store ESPN authentication credentials for a session"""
        try:
            self.credentials[session_id] = {
                'espn_s2': espn_s2,
                'swid': swid
            }
            log_error(f"Stored credentials for session {session_id}")
            return {"status": "success", "message": "Authentication successful. Credentials stored for this session."}
        except Exception as e:
            log_error(f"Authentication error: {str(e)}")
            return {"status": "error", "message": f"Authentication error: {str(e)}"}
    
    def get_credentials(self, session_id: str) -> Optional[Dict[str, str]]:
        """Retrieve stored credentials for a session"""
        return self.credentials.get(session_id)
    
    def clear_credentials(self, session_id: str) -> Dict[str, str]:
        """Clear stored credentials for a session"""
        try:
            if session_id in self.credentials:
                del self.credentials[session_id]
                log_error(f"Cleared credentials for session {session_id}")
            return {"status": "success", "message": "Authentication credentials have been cleared."}
        except Exception as e:
            log_error(f"Error clearing credentials: {str(e)}")
            return {"status": "error", "message": f"Error clearing credentials: {str(e)}"}

# Global auth service instance
auth_service = AuthService()

def authenticate(espn_s2: str, swid: str, session_id: str = "default_session") -> Dict[str, str]:
    """
    Store ESPN authentication credentials for this session.
    
    Args:
        espn_s2: The ESPN_S2 cookie value from your ESPN account
        swid: The SWID cookie value from your ESPN account
        session_id: Session identifier (defaults to default_session)
    
    Returns:
        Dictionary with status and message
    """
    return auth_service.store_credentials(session_id, espn_s2, swid)

def logout(session_id: str = "default_session") -> Dict[str, str]:
    """
    Clear stored authentication credentials for this session.
    
    Args:
        session_id: Session identifier (defaults to default_session)
    
    Returns:
        Dictionary with status and message
    """
    return auth_service.clear_credentials(session_id)