"""Cryptographic primitives for zero-knowledge encryption."""

import os
import secrets
from typing import Tuple
from argon2 import PasswordHasher
from argon2.low_level import hash_secret_raw, Type
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

from .exceptions import EncryptionError
from .value_objects import EncryptedBlob


class CryptoService:
    """
    Zero-knowledge encryption service.
    
    Key Principles:
    - Password derives TWO separate keys: auth_hash and master_key
    - Server stores auth_hash for authentication (never sees master_key)
    - All encryption/decryption happens client-side with master_key
    """
    
    def __init__(
        self,
        time_cost: int = 3,
        memory_cost: int = 65536,  # 64 MB
        parallelism: int = 4,
    ):
        self.time_cost = time_cost
        self.memory_cost = memory_cost
        self.parallelism = parallelism
        self.ph = PasswordHasher(
            time_cost=time_cost,
            memory_cost=memory_cost,
            parallelism=parallelism,
        )
    
    def generate_salt(self) -> bytes:
        """Generate a random 32-byte salt."""
        return secrets.token_bytes(32)
    
    def derive_keys(
        self,
        password: str,
        auth_salt: bytes,
        key_salt: bytes,
    ) -> Tuple[bytes, bytes]:
        """
        Derive both auth_hash and master_key from password.
        
        Args:
            password: User password
            auth_salt: Salt for authentication hash
            key_salt: Salt for master encryption key
        
        Returns:
            Tuple of (auth_hash, master_key)
        """
        # Derive auth hash (stored server-side for authentication)
        auth_hash = hash_secret_raw(
            secret=password.encode("utf-8"),
            salt=auth_salt,
            time_cost=self.time_cost,
            memory_cost=self.memory_cost,
            parallelism=self.parallelism,
            hash_len=32,
            type=Type.ID,
        )
        
        # Derive master key (used for encryption, never stored)
        master_key = hash_secret_raw(
            secret=password.encode("utf-8"),
            salt=key_salt,
            time_cost=self.time_cost,
            memory_cost=self.memory_cost,
            parallelism=self.parallelism,
            hash_len=32,
            type=Type.ID,
        )
        
        return auth_hash, master_key
    
    def verify_auth_hash(self, stored_hash: bytes, password: str, auth_salt: bytes) -> bool:
        """
        Verify password against stored auth hash.
        
        Args:
            stored_hash: Stored authentication hash
            password: Password to verify
            auth_salt: Salt used for auth hash
        
        Returns:
            True if password matches
        """
        computed_hash = hash_secret_raw(
            secret=password.encode("utf-8"),
            salt=auth_salt,
            time_cost=self.time_cost,
            memory_cost=self.memory_cost,
            parallelism=self.parallelism,
            hash_len=32,
            type=Type.ID,
        )
        return secrets.compare_digest(stored_hash, computed_hash)
    
    def derive_file_key(self, master_key: bytes, salt: bytes, info: bytes = b"file") -> bytes:
        """
        Derive a file-specific encryption key from master key.
        
        Args:
            master_key: Master encryption key
            salt: Random salt for this file
            info: Context info for key derivation
        
        Returns:
            32-byte file encryption key
        """
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            info=info,
        )
        return hkdf.derive(master_key)
    
    def encrypt(self, plaintext: bytes, master_key: bytes) -> EncryptedBlob:
        """
        Encrypt data with AES-256-GCM.
        
        Args:
            plaintext: Data to encrypt
            master_key: Master encryption key
        
        Returns:
            EncryptedBlob with encrypted data
        
        Raises:
            EncryptionError: If encryption fails
        """
        try:
            # Generate random salt for file key derivation
            salt = self.generate_salt()
            
            # Derive file-specific key
            file_key = self.derive_file_key(master_key, salt)
            
            # Generate random nonce (12 bytes for GCM)
            nonce = os.urandom(12)
            
            # Encrypt with AES-256-GCM
            aesgcm = AESGCM(file_key)
            ciphertext = aesgcm.encrypt(nonce, plaintext, None)
            
            # Package: nonce + ciphertext + tag (tag is included in ciphertext)
            encrypted_data = nonce + ciphertext
            
            return EncryptedBlob(
                data=encrypted_data,
                salt=salt,
                algorithm="AES-256-GCM",
            )
        except Exception as e:
            raise EncryptionError(f"Encryption failed: {e}")
    
    def decrypt(self, blob: EncryptedBlob, master_key: bytes) -> bytes:
        """
        Decrypt data with AES-256-GCM.
        
        Args:
            blob: EncryptedBlob to decrypt
            master_key: Master encryption key
        
        Returns:
            Decrypted plaintext
        
        Raises:
            EncryptionError: If decryption fails
        """
        try:
            # Derive file-specific key
            file_key = self.derive_file_key(master_key, blob.salt)
            
            # Extract nonce and ciphertext
            nonce = blob.data[:12]
            ciphertext = blob.data[12:]
            
            # Decrypt with AES-256-GCM
            aesgcm = AESGCM(file_key)
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
            
            return plaintext
        except Exception as e:
            raise EncryptionError(f"Decryption failed: {e}")
    
    def encrypt_metadata(self, metadata: dict, master_key: bytes) -> EncryptedBlob:
        """
        Encrypt metadata as JSON.
        
        Args:
            metadata: Metadata dictionary
            master_key: Master encryption key
        
        Returns:
            EncryptedBlob with encrypted metadata
        """
        import json
        plaintext = json.dumps(metadata).encode("utf-8")
        return self.encrypt(plaintext, master_key)
    
    def decrypt_metadata(self, blob: EncryptedBlob, master_key: bytes) -> dict:
        """
        Decrypt metadata from JSON.
        
        Args:
            blob: EncryptedBlob to decrypt
            master_key: Master encryption key
        
        Returns:
            Metadata dictionary
        """
        import json
        plaintext = self.decrypt(blob, master_key)
        return json.loads(plaintext.decode("utf-8"))

