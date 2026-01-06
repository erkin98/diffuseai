"""Abstract repository interfaces."""

from abc import ABC, abstractmethod
from typing import Optional, List

from imggen.domain.entities import User, Image


class UserRepository(ABC):
    """Abstract user repository."""
    
    @abstractmethod
    def create(self, user: User) -> User:
        """Create a new user."""
        pass
    
    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        pass
    
    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        pass
    
    @abstractmethod
    def exists(self, username: str) -> bool:
        """Check if user exists."""
        pass


class ImageRepository(ABC):
    """Abstract image repository."""
    
    @abstractmethod
    def create(self, image: Image) -> Image:
        """Create a new image record."""
        pass
    
    @abstractmethod
    def get_by_id(self, image_id: int, user_id: int) -> Optional[Image]:
        """Get image by ID (filtered by user_id)."""
        pass
    
    @abstractmethod
    def list_by_user(self, user_id: int, limit: int = 100, offset: int = 0) -> List[Image]:
        """List images for a user."""
        pass
    
    @abstractmethod
    def delete(self, image_id: int, user_id: int) -> bool:
        """Delete an image."""
        pass
    
    @abstractmethod
    def search_by_prompt(self, user_id: int, keyword: str, limit: int = 100) -> List[Image]:
        """Search images by prompt keyword (requires decryption)."""
        pass

