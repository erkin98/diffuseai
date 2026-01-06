"""Local filesystem vault storage."""

import os
import json
from pathlib import Path
from typing import Optional
from datetime import datetime

from imggen.domain.value_objects import EncryptedBlob
from imggen.domain.exceptions import VaultAccessError
from .base import VaultStorage


class LocalVaultStorage(VaultStorage):
    """Local filesystem implementation of vault storage."""
    
    def __init__(self, vault_dir: Path):
        self.vault_dir = vault_dir
        self.vault_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_user_dir(self, user_id: int) -> Path:
        """Get user-specific vault directory."""
        user_dir = self.vault_dir / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir
    
    def _resolve_path(self, vault_path: str) -> Path:
        """Resolve vault path to absolute path."""
        full_path = self.vault_dir / vault_path
        
        # Security: ensure path is within vault directory
        try:
            full_path.resolve().relative_to(self.vault_dir.resolve())
        except ValueError:
            raise VaultAccessError("Invalid vault path (directory traversal attempt)")
        
        return full_path
    
    def store(self, user_id: int, blob: EncryptedBlob, filename: str) -> str:
        """Store encrypted blob."""
        try:
            user_dir = self._get_user_dir(user_id)
            
            # Generate unique filename with timestamp
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            name_parts = filename.rsplit(".", 1)
            if len(name_parts) == 2:
                unique_filename = f"{name_parts[0]}_{timestamp}.{name_parts[1]}"
            else:
                unique_filename = f"{filename}_{timestamp}"
            
            file_path = user_dir / unique_filename
            
            # Store as JSON with encrypted data and metadata
            data = {
                "data": blob.data.hex(),  # Store as hex string
                "salt": blob.salt.hex(),
                "algorithm": blob.algorithm,
                "stored_at": datetime.utcnow().isoformat(),
            }
            
            with open(file_path, "w") as f:
                json.dump(data, f)
            
            # Return relative path
            return str(file_path.relative_to(self.vault_dir))
            
        except Exception as e:
            raise VaultAccessError(f"Failed to store file: {e}")
    
    def retrieve(self, vault_path: str) -> Optional[EncryptedBlob]:
        """Retrieve encrypted blob."""
        try:
            file_path = self._resolve_path(vault_path)
            
            if not file_path.exists():
                return None
            
            with open(file_path, "r") as f:
                data = json.load(f)
            
            return EncryptedBlob(
                data=bytes.fromhex(data["data"]),
                salt=bytes.fromhex(data["salt"]),
                algorithm=data["algorithm"],
            )
            
        except Exception as e:
            raise VaultAccessError(f"Failed to retrieve file: {e}")
    
    def delete(self, vault_path: str) -> bool:
        """Securely delete encrypted file."""
        try:
            file_path = self._resolve_path(vault_path)
            
            if not file_path.exists():
                return False
            
            # Overwrite with random data before deletion (simple secure delete)
            file_size = file_path.stat().st_size
            with open(file_path, "wb") as f:
                f.write(os.urandom(file_size))
            
            # Delete file
            file_path.unlink()
            
            return True
            
        except Exception as e:
            raise VaultAccessError(f"Failed to delete file: {e}")
    
    def exists(self, vault_path: str) -> bool:
        """Check if file exists."""
        try:
            file_path = self._resolve_path(vault_path)
            return file_path.exists()
        except Exception:
            return False

