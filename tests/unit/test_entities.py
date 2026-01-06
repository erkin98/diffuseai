"""Unit tests for domain entities."""

from datetime import datetime
from imggen.domain.entities import User, Image
from imggen.domain.value_objects import EncryptedBlob, ImageMetadata


def test_user_creation():
    """Test user entity creation."""
    user = User(
        username="testuser",
        auth_salt=b"auth_salt_32_bytes_____________",
        key_salt=b"key_salt_32_bytes______________",
        auth_hash=b"auth_hash_32_bytes_____________",
    )
    
    assert user.username == "testuser"
    assert user.id is None  # Not yet persisted
    assert isinstance(user.created_at, datetime)


def test_image_creation():
    """Test image entity creation."""
    metadata_blob = EncryptedBlob(
        data=b"encrypted_metadata",
        salt=b"salt_32_bytes_____________________",
        algorithm="AES-256-GCM",
    )
    
    image = Image(
        user_id=1,
        vault_path="1/image_123.png",
        metadata_blob=metadata_blob,
    )
    
    assert image.user_id == 1
    assert image.vault_path == "1/image_123.png"
    assert image.id is None  # Not yet persisted
    assert isinstance(image.created_at, datetime)


def test_image_metadata():
    """Test image metadata value object."""
    metadata = ImageMetadata(
        prompt="a beautiful sunset",
        negative_prompt="blurry, bad quality",
        width=1024,
        height=1024,
        steps=25,
        cfg_scale=7.0,
        seed=42,
        provider="ComfyUIProvider",
    )
    
    assert metadata.prompt == "a beautiful sunset"
    assert metadata.width == 1024
    assert metadata.seed == 42
    assert isinstance(metadata.created_at, datetime)


def test_encrypted_blob():
    """Test encrypted blob value object."""
    blob = EncryptedBlob(
        data=b"encrypted_data_here",
        salt=b"random_salt_32_bytes_____________",
        algorithm="AES-256-GCM",
    )
    
    assert blob.data == b"encrypted_data_here"
    assert len(blob.salt) == 33
    assert blob.algorithm == "AES-256-GCM"

