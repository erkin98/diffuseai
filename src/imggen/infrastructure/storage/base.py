"""Abstract vault storage interface."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from imggen.domain.value_objects import EncryptedBlob


class VaultStorage(ABC):
    """Abstract vault storage for encrypted files."""
    
    @abstractmethod
    def store(self, user_id: int, blob: EncryptedBlob, filename: str) -> str:
        """
        Store encrypted blob.
        
        Args:
            user_id: User ID
            blob: Encrypted data
            filename: Desired filename
        
        Returns:
            Vault path (relative)
        """
        pass
    
    @abstractmethod
    def retrieve(self, vault_path: str) -> Optional[EncryptedBlob]:
        """
        Retrieve encrypted blob.
        
        Args:
            vault_path: Vault path (relative)
        
        Returns:
            EncryptedBlob or None if not found
        """
        pass
    
    @abstractmethod
    def delete(self, vault_path: str) -> bool:
        """
        Securely delete encrypted file.
        
        Args:
            vault_path: Vault path (relative)
        
        Returns:
            True if deleted successfully
        """
        pass
    
    @abstractmethod
    def exists(self, vault_path: str) -> bool:
        """
        Check if file exists.
        
        Args:
            vault_path: Vault path (relative)
        
        Returns:
            True if exists
        """
        pass

