"""Domain value objects - immutable data structures."""

from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class EncryptedBlob(BaseModel):
    """Encrypted data blob with metadata."""
    
    data: bytes = Field(..., description="Encrypted data (nonce + ciphertext + tag)")
    salt: bytes = Field(..., description="Salt used for key derivation")
    algorithm: str = Field(default="AES-256-GCM", description="Encryption algorithm")
    
    model_config = {"frozen": True}


class ImageMetadata(BaseModel):
    """Image generation metadata."""
    
    prompt: str = Field(..., description="Generation prompt")
    negative_prompt: str = Field(default="", description="Negative prompt")
    width: int = Field(..., description="Image width")
    height: int = Field(..., description="Image height")
    steps: int = Field(..., description="Sampling steps")
    cfg_scale: float = Field(..., description="CFG scale")
    seed: int = Field(..., description="Random seed")
    sampler: str = Field(default="DPM++ 2M Karras", description="Sampler name")
    model: str = Field(default="SDXL Base", description="Model name")
    provider: str = Field(..., description="GPU provider used")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation time")
    
    model_config = {"frozen": True}


class UserCredentials(BaseModel):
    """User authentication credentials."""
    
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    auth_salt: bytes = Field(..., description="Salt for auth hash")
    key_salt: bytes = Field(..., description="Salt for master key")
    auth_hash: bytes = Field(..., description="Hashed password for authentication")
    
    model_config = {"frozen": True}


class SessionInfo(BaseModel):
    """Session information."""
    
    user_id: int = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    master_key: bytes = Field(..., description="Master encryption key")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Session start time")
    expires_at: datetime = Field(..., description="Session expiration time")
    
    model_config = {"frozen": True}

