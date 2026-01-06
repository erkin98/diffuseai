"""Unit tests for crypto service."""

import pytest
from imggen.domain.crypto import CryptoService
from imggen.domain.exceptions import EncryptionError


def test_generate_salt():
    """Test salt generation."""
    crypto = CryptoService()
    salt1 = crypto.generate_salt()
    salt2 = crypto.generate_salt()
    
    assert len(salt1) == 32
    assert len(salt2) == 32
    assert salt1 != salt2  # Should be random


def test_derive_keys():
    """Test key derivation."""
    crypto = CryptoService()
    password = "test_password_123"
    auth_salt = crypto.generate_salt()
    key_salt = crypto.generate_salt()
    
    auth_hash, master_key = crypto.derive_keys(password, auth_salt, key_salt)
    
    assert len(auth_hash) == 32
    assert len(master_key) == 32
    assert auth_hash != master_key  # Should be different


def test_verify_auth_hash():
    """Test password verification."""
    crypto = CryptoService()
    password = "test_password_123"
    auth_salt = crypto.generate_salt()
    key_salt = crypto.generate_salt()
    
    auth_hash, _ = crypto.derive_keys(password, auth_salt, key_salt)
    
    # Correct password should verify
    assert crypto.verify_auth_hash(auth_hash, password, auth_salt)
    
    # Wrong password should not verify
    assert not crypto.verify_auth_hash(auth_hash, "wrong_password", auth_salt)


def test_encrypt_decrypt():
    """Test encryption and decryption."""
    crypto = CryptoService()
    master_key = crypto.generate_salt()  # Use random key for testing
    plaintext = b"Hello, World! This is secret data."
    
    # Encrypt
    blob = crypto.encrypt(plaintext, master_key)
    
    assert blob.data != plaintext
    assert len(blob.salt) == 32
    assert blob.algorithm == "AES-256-GCM"
    
    # Decrypt
    decrypted = crypto.decrypt(blob, master_key)
    
    assert decrypted == plaintext


def test_encrypt_decrypt_metadata():
    """Test metadata encryption."""
    crypto = CryptoService()
    master_key = crypto.generate_salt()
    metadata = {
        "prompt": "a beautiful sunset",
        "width": 1024,
        "height": 1024,
        "seed": 42,
    }
    
    # Encrypt
    blob = crypto.encrypt_metadata(metadata, master_key)
    
    # Decrypt
    decrypted = crypto.decrypt_metadata(blob, master_key)
    
    assert decrypted == metadata


def test_decrypt_with_wrong_key():
    """Test decryption with wrong key fails."""
    crypto = CryptoService()
    master_key = crypto.generate_salt()
    wrong_key = crypto.generate_salt()
    plaintext = b"Secret data"
    
    blob = crypto.encrypt(plaintext, master_key)
    
    with pytest.raises(EncryptionError):
        crypto.decrypt(blob, wrong_key)


def test_deterministic_key_derivation():
    """Test that key derivation is deterministic."""
    crypto = CryptoService()
    password = "test_password"
    auth_salt = crypto.generate_salt()
    key_salt = crypto.generate_salt()
    
    auth_hash1, master_key1 = crypto.derive_keys(password, auth_salt, key_salt)
    auth_hash2, master_key2 = crypto.derive_keys(password, auth_salt, key_salt)
    
    assert auth_hash1 == auth_hash2
    assert master_key1 == master_key2

