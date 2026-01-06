"""Domain entities - core business objects."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from .value_objects import ImageMetadata, EncryptedBlob


class User(BaseModel):
    """User entity."""
    
    id: Optional[int] = Field(default=None, description="User ID (None until persisted)")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    auth_salt: bytes = Field(..., description="Salt for authentication")
    key_salt: bytes = Field(..., description="Salt for master key derivation")
    auth_hash: bytes = Field(..., description="Authentication hash")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    
    model_config = {"frozen": False}


class Image(BaseModel):
    """Image entity with encrypted data."""
    
    id: Optional[int] = Field(default=None, description="Image ID (None until persisted)")
    user_id: int = Field(..., description="Owner user ID")
    vault_path: str = Field(..., description="Path to encrypted image file")
    metadata_blob: EncryptedBlob = Field(..., description="Encrypted metadata")
    thumbnail_blob: Optional[EncryptedBlob] = Field(default=None, description="Encrypted thumbnail")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    
    model_config = {"frozen": False}


class Vault(BaseModel):
    """Vault entry for encrypted file storage."""
    
    id: Optional[int] = Field(default=None, description="Vault ID")
    user_id: int = Field(..., description="Owner user ID")
    file_path: str = Field(..., description="Relative path in vault")
    encrypted_data: EncryptedBlob = Field(..., description="Encrypted file data")
    file_type: str = Field(..., description="File type (image, metadata, etc)")
    size_bytes: int = Field(..., description="Encrypted size in bytes")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    
    model_config = {"frozen": False}

