"""Gallery management use cases."""

from typing import List, Optional
from pathlib import Path

from imggen.domain.entities import Image
from imggen.domain.crypto import CryptoService
from imggen.domain.value_objects import ImageMetadata
from imggen.domain.exceptions import ImageNotFoundError, VaultAccessError
from imggen.infrastructure.database.base import ImageRepository
from imggen.infrastructure.storage.base import VaultStorage
from imggen.infrastructure.session import SessionManager


class ListImagesUseCase:
    """List user's images."""
    
    def __init__(
        self,
        image_repo: ImageRepository,
        session_manager: SessionManager,
    ):
        self.image_repo = image_repo
        self.session_manager = session_manager
    
    def execute(self, limit: int = 100, offset: int = 0) -> List[Image]:
        """
        List user's images.
        
        Args:
            limit: Maximum number of images
            offset: Offset for pagination
        
        Returns:
            List of images
        
        Raises:
            SessionNotFoundError: If not logged in
        """
        session = self.session_manager.require_session()
        return self.image_repo.list_by_user(session.user_id, limit=limit, offset=offset)


class GetImageMetadataUseCase:
    """Get decrypted image metadata."""
    
    def __init__(
        self,
        image_repo: ImageRepository,
        crypto_service: CryptoService,
        session_manager: SessionManager,
    ):
        self.image_repo = image_repo
        self.crypto = crypto_service
        self.session_manager = session_manager
    
    def execute(self, image_id: int) -> ImageMetadata:
        """
        Get decrypted metadata for an image.
        
        Args:
            image_id: Image ID
        
        Returns:
            Decrypted metadata
        
        Raises:
            SessionNotFoundError: If not logged in
            ImageNotFoundError: If image doesn't exist
        """
        session = self.session_manager.require_session()
        
        # Get image
        image = self.image_repo.get_by_id(image_id, session.user_id)
        if not image:
            raise ImageNotFoundError(f"Image {image_id} not found")
        
        # Decrypt metadata
        metadata_dict = self.crypto.decrypt_metadata(image.metadata_blob, session.master_key)
        
        # Parse as ImageMetadata
        return ImageMetadata(**metadata_dict)


class ExportImageUseCase:
    """Export decrypted image to file."""
    
    def __init__(
        self,
        image_repo: ImageRepository,
        vault_storage: VaultStorage,
        crypto_service: CryptoService,
        session_manager: SessionManager,
    ):
        self.image_repo = image_repo
        self.vault_storage = vault_storage
        self.crypto = crypto_service
        self.session_manager = session_manager
    
    def execute(self, image_id: int, output_path: Path) -> Path:
        """
        Decrypt and export image.
        
        Args:
            image_id: Image ID
            output_path: Output file path
        
        Returns:
            Output path
        
        Raises:
            SessionNotFoundError: If not logged in
            ImageNotFoundError: If image doesn't exist
            VaultAccessError: If vault access fails
        """
        session = self.session_manager.require_session()
        
        # Get image
        image = self.image_repo.get_by_id(image_id, session.user_id)
        if not image:
            raise ImageNotFoundError(f"Image {image_id} not found")
        
        # Retrieve encrypted data
        encrypted_blob = self.vault_storage.retrieve(image.vault_path)
        if not encrypted_blob:
            raise VaultAccessError(f"Failed to retrieve image from vault")
        
        # Decrypt
        decrypted_bytes = self.crypto.decrypt(encrypted_blob, session.master_key)
        
        # Write to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(decrypted_bytes)
        
        return output_path


class DeleteImageUseCase:
    """Delete image and its encrypted data."""
    
    def __init__(
        self,
        image_repo: ImageRepository,
        vault_storage: VaultStorage,
        session_manager: SessionManager,
    ):
        self.image_repo = image_repo
        self.vault_storage = vault_storage
        self.session_manager = session_manager
    
    def execute(self, image_id: int) -> bool:
        """
        Delete image and vault data.
        
        Args:
            image_id: Image ID
        
        Returns:
            True if deleted
        
        Raises:
            SessionNotFoundError: If not logged in
        """
        session = self.session_manager.require_session()
        
        # Get image (to get vault path)
        image = self.image_repo.get_by_id(image_id, session.user_id)
        if not image:
            return False
        
        # Delete vault file
        self.vault_storage.delete(image.vault_path)
        
        # Delete database record
        return self.image_repo.delete(image_id, session.user_id)


class SearchImagesUseCase:
    """Search images by prompt."""
    
    def __init__(
        self,
        image_repo: ImageRepository,
        crypto_service: CryptoService,
        session_manager: SessionManager,
    ):
        self.image_repo = image_repo
        self.crypto = crypto_service
        self.session_manager = session_manager
    
    def execute(self, keyword: str, limit: int = 100) -> List[tuple[Image, ImageMetadata]]:
        """
        Search images by prompt keyword.
        
        Note: This requires decrypting all metadata to search.
        
        Args:
            keyword: Search keyword
            limit: Maximum results
        
        Returns:
            List of (Image, ImageMetadata) tuples
        
        Raises:
            SessionNotFoundError: If not logged in
        """
        session = self.session_manager.require_session()
        
        # Get all user images
        images = self.image_repo.list_by_user(session.user_id, limit=limit)
        
        # Search by decrypting metadata
        results = []
        keyword_lower = keyword.lower()
        
        for image in images:
            try:
                metadata_dict = self.crypto.decrypt_metadata(
                    image.metadata_blob,
                    session.master_key,
                )
                metadata = ImageMetadata(**metadata_dict)
                
                # Check if keyword in prompt
                if keyword_lower in metadata.prompt.lower():
                    results.append((image, metadata))
                    
            except Exception:
                # Skip images with decryption errors
                continue
        
        return results

