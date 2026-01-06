"""Authentication use cases."""

from datetime import datetime, timedelta
from typing import Optional

from imggen.domain.entities import User
from imggen.domain.crypto import CryptoService
from imggen.domain.value_objects import SessionInfo
from imggen.domain.exceptions import (
    AuthenticationError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from imggen.infrastructure.database.base import UserRepository
from imggen.infrastructure.session import SessionManager


class RegisterUseCase:
    """Register a new user."""
    
    def __init__(
        self,
        user_repo: UserRepository,
        crypto_service: CryptoService,
    ):
        self.user_repo = user_repo
        self.crypto = crypto_service
    
    def execute(self, username: str, password: str) -> User:
        """
        Register a new user with zero-knowledge encryption.
        
        Args:
            username: Username
            password: Password
        
        Returns:
            Created user
        
        Raises:
            UserAlreadyExistsError: If username already exists
        """
        # Check if user exists
        if self.user_repo.exists(username):
            raise UserAlreadyExistsError(f"User '{username}' already exists")
        
        # Generate salts
        auth_salt = self.crypto.generate_salt()
        key_salt = self.crypto.generate_salt()
        
        # Derive keys
        auth_hash, _ = self.crypto.derive_keys(password, auth_salt, key_salt)
        
        # Create user
        user = User(
            username=username,
            auth_salt=auth_salt,
            key_salt=key_salt,
            auth_hash=auth_hash,
        )
        
        # Persist
        return self.user_repo.create(user)


class LoginUseCase:
    """Login user and create session."""
    
    def __init__(
        self,
        user_repo: UserRepository,
        crypto_service: CryptoService,
        session_manager: SessionManager,
    ):
        self.user_repo = user_repo
        self.crypto = crypto_service
        self.session_manager = session_manager
    
    def execute(self, username: str, password: str) -> SessionInfo:
        """
        Authenticate user and create session.
        
        Args:
            username: Username
            password: Password
        
        Returns:
            Session info with master key
        
        Raises:
            UserNotFoundError: If user doesn't exist
            AuthenticationError: If password is incorrect
        """
        # Get user
        user = self.user_repo.get_by_username(username)
        if not user:
            raise UserNotFoundError(f"User '{username}' not found")
        
        # Verify password
        if not self.crypto.verify_auth_hash(user.auth_hash, password, user.auth_salt):
            raise AuthenticationError("Invalid password")
        
        # Derive master key (never stored on server)
        _, master_key = self.crypto.derive_keys(password, user.auth_salt, user.key_salt)
        
        # Create session
        now = datetime.utcnow()
        session = SessionInfo(
            user_id=user.id,  # type: ignore
            username=user.username,
            master_key=master_key,
            created_at=now,
            expires_at=now + timedelta(seconds=self.session_manager.timeout),
        )
        
        self.session_manager.create_session(session)
        
        return session


class LogoutUseCase:
    """Logout user and clear session."""
    
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager
    
    def execute(self) -> None:
        """Clear current session."""
        self.session_manager.clear_session()


class WhoAmIUseCase:
    """Get current user info."""
    
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager
    
    def execute(self) -> Optional[SessionInfo]:
        """
        Get current session info.
        
        Returns:
            SessionInfo if logged in, None otherwise
        """
        return self.session_manager.get_session()

