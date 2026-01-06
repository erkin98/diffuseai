"""SQLite database implementation."""

import sqlite3
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from imggen.domain.entities import User, Image
from imggen.domain.value_objects import EncryptedBlob
from .base import UserRepository, ImageRepository


def init_db(db_path: Path) -> None:
    """Initialize database schema."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            auth_salt BLOB NOT NULL,
            key_salt BLOB NOT NULL,
            auth_hash BLOB NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    
    # Images table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            vault_path TEXT NOT NULL,
            metadata_data BLOB NOT NULL,
            metadata_salt BLOB NOT NULL,
            metadata_algorithm TEXT NOT NULL,
            thumbnail_data BLOB,
            thumbnail_salt BLOB,
            thumbnail_algorithm TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    # Indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_images_user_id ON images(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_images_created_at ON images(created_at)")
    
    conn.commit()
    conn.close()


class SQLiteUserRepository(UserRepository):
    """SQLite implementation of user repository."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        init_db(db_path)
    
    def _get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)
    
    def create(self, user: User) -> User:
        """Create a new user."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            INSERT INTO users (username, auth_salt, key_salt, auth_hash, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                user.username,
                user.auth_salt,
                user.key_salt,
                user.auth_hash,
                user.created_at.isoformat(),
            ),
        )
        
        user.id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return user
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, username, auth_salt, key_salt, auth_hash, created_at FROM users WHERE id = ?",
            (user_id,),
        )
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return User(
            id=row[0],
            username=row[1],
            auth_salt=row[2],
            key_salt=row[3],
            auth_hash=row[4],
            created_at=datetime.fromisoformat(row[5]),
        )
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, username, auth_salt, key_salt, auth_hash, created_at FROM users WHERE username = ?",
            (username,),
        )
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return User(
            id=row[0],
            username=row[1],
            auth_salt=row[2],
            key_salt=row[3],
            auth_hash=row[4],
            created_at=datetime.fromisoformat(row[5]),
        )
    
    def exists(self, username: str) -> bool:
        """Check if user exists."""
        return self.get_by_username(username) is not None


class SQLiteImageRepository(ImageRepository):
    """SQLite implementation of image repository."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        init_db(db_path)
    
    def _get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)
    
    def create(self, image: Image) -> Image:
        """Create a new image record."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        thumbnail_data = image.thumbnail_blob.data if image.thumbnail_blob else None
        thumbnail_salt = image.thumbnail_blob.salt if image.thumbnail_blob else None
        thumbnail_algorithm = image.thumbnail_blob.algorithm if image.thumbnail_blob else None
        
        cursor.execute(
            """
            INSERT INTO images (
                user_id, vault_path, 
                metadata_data, metadata_salt, metadata_algorithm,
                thumbnail_data, thumbnail_salt, thumbnail_algorithm,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                image.user_id,
                image.vault_path,
                image.metadata_blob.data,
                image.metadata_blob.salt,
                image.metadata_blob.algorithm,
                thumbnail_data,
                thumbnail_salt,
                thumbnail_algorithm,
                image.created_at.isoformat(),
            ),
        )
        
        image.id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return image
    
    def get_by_id(self, image_id: int, user_id: int) -> Optional[Image]:
        """Get image by ID (filtered by user_id)."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT id, user_id, vault_path,
                   metadata_data, metadata_salt, metadata_algorithm,
                   thumbnail_data, thumbnail_salt, thumbnail_algorithm,
                   created_at
            FROM images
            WHERE id = ? AND user_id = ?
            """,
            (image_id, user_id),
        )
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        metadata_blob = EncryptedBlob(
            data=row[3],
            salt=row[4],
            algorithm=row[5],
        )
        
        thumbnail_blob = None
        if row[6]:
            thumbnail_blob = EncryptedBlob(
                data=row[6],
                salt=row[7],
                algorithm=row[8],
            )
        
        return Image(
            id=row[0],
            user_id=row[1],
            vault_path=row[2],
            metadata_blob=metadata_blob,
            thumbnail_blob=thumbnail_blob,
            created_at=datetime.fromisoformat(row[9]),
        )
    
    def list_by_user(self, user_id: int, limit: int = 100, offset: int = 0) -> List[Image]:
        """List images for a user."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT id, user_id, vault_path,
                   metadata_data, metadata_salt, metadata_algorithm,
                   thumbnail_data, thumbnail_salt, thumbnail_algorithm,
                   created_at
            FROM images
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """,
            (user_id, limit, offset),
        )
        
        rows = cursor.fetchall()
        conn.close()
        
        images = []
        for row in rows:
            metadata_blob = EncryptedBlob(
                data=row[3],
                salt=row[4],
                algorithm=row[5],
            )
            
            thumbnail_blob = None
            if row[6]:
                thumbnail_blob = EncryptedBlob(
                    data=row[6],
                    salt=row[7],
                    algorithm=row[8],
                )
            
            images.append(
                Image(
                    id=row[0],
                    user_id=row[1],
                    vault_path=row[2],
                    metadata_blob=metadata_blob,
                    thumbnail_blob=thumbnail_blob,
                    created_at=datetime.fromisoformat(row[9]),
                )
            )
        
        return images
    
    def delete(self, image_id: int, user_id: int) -> bool:
        """Delete an image."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "DELETE FROM images WHERE id = ? AND user_id = ?",
            (image_id, user_id),
        )
        
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return deleted
    
    def search_by_prompt(self, user_id: int, keyword: str, limit: int = 100) -> List[Image]:
        """
        Search images by prompt keyword.
        Note: This is a stub - actual search requires decrypting metadata.
        """
        # For now, just return all user images
        # Proper implementation would need to decrypt and search in application layer
        return self.list_by_user(user_id, limit=limit)

