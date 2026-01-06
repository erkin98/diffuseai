"""Session management for authenticated users."""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

from imggen.domain.value_objects import SessionInfo
from imggen.domain.exceptions import SessionExpiredError, SessionNotFoundError


class SessionManager:
    """
    Manage user sessions with encrypted master keys.
    
    Sessions are stored in local files during CLI usage.
    In online mode, this would be replaced with server-side session storage.
    """
    
    def __init__(self, session_dir: Path, timeout: int = 3600):
        self.session_dir = session_dir
        self.timeout = timeout
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.session_file = self.session_dir / ".session"
    
    def create_session(self, session: SessionInfo) -> None:
        """Create a new session."""
        data = {
            "user_id": session.user_id,
            "username": session.username,
            "master_key": session.master_key.hex(),
            "created_at": session.created_at.isoformat(),
            "expires_at": session.expires_at.isoformat(),
        }
        
        with open(self.session_file, "w") as f:
            json.dump(data, f)
        
        # Set restrictive permissions (Unix only)
        try:
            self.session_file.chmod(0o600)
        except Exception:
            pass
    
    def get_session(self) -> Optional[SessionInfo]:
        """Get current session if valid."""
        if not self.session_file.exists():
            return None
        
        try:
            with open(self.session_file, "r") as f:
                data = json.load(f)
            
            expires_at = datetime.fromisoformat(data["expires_at"])
            
            # Check if expired
            if datetime.utcnow() > expires_at:
                self.clear_session()
                raise SessionExpiredError("Session has expired. Please login again.")
            
            return SessionInfo(
                user_id=data["user_id"],
                username=data["username"],
                master_key=bytes.fromhex(data["master_key"]),
                created_at=datetime.fromisoformat(data["created_at"]),
                expires_at=expires_at,
            )
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Invalid session file
            self.clear_session()
            return None
    
    def clear_session(self) -> None:
        """Clear current session."""
        if self.session_file.exists():
            # Overwrite with zeros before deletion
            with open(self.session_file, "wb") as f:
                f.write(b"\x00" * 1024)
            
            self.session_file.unlink()
    
    def require_session(self) -> SessionInfo:
        """Get session or raise error."""
        session = self.get_session()
        if not session:
            raise SessionNotFoundError("No active session. Please login first.")
        return session
    
    def is_logged_in(self) -> bool:
        """Check if user is logged in."""
        try:
            session = self.get_session()
            return session is not None
        except SessionExpiredError:
            return False

