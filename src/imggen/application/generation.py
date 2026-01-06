"""Image generation use cases."""

import random
from datetime import datetime
from typing import Optional

from imggen.domain.entities import Image
from imggen.domain.crypto import CryptoService
from imggen.domain.value_objects import ImageMetadata, EncryptedBlob
from imggen.domain.exceptions import GenerationError
from imggen.infrastructure.database.base import ImageRepository
from imggen.infrastructure.gpu.base import GPUProvider
from imggen.infrastructure.storage.base import VaultStorage
from imggen.infrastructure.session import SessionManager


class GenerateImageUseCase:
    """Generate an AI image with E2E encryption."""
    
    def __init__(
        self,
        image_repo: ImageRepository,
        gpu_provider: GPUProvider,
        vault_storage: VaultStorage,
        crypto_service: CryptoService,
        session_manager: SessionManager,
    ):
        self.image_repo = image_repo
        self.gpu_provider = gpu_provider
        self.vault_storage = vault_storage
        self.crypto = crypto_service
        self.session_manager = session_manager
    
    async def execute(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 1024,
        steps: int = 25,
        cfg_scale: float = 7.0,
        seed: Optional[int] = None,
    ) -> Image:
        """
        Generate encrypted image.
        
        Args:
            prompt: Generation prompt
            negative_prompt: Negative prompt
            width: Image width
            height: Image height
            steps: Sampling steps
            cfg_scale: CFG scale
            seed: Random seed (None for random)
        
        Returns:
            Created Image entity
        
        Raises:
            SessionNotFoundError: If not logged in
            GenerationError: If generation fails
        """
        # Require session
        session = self.session_manager.require_session()
        
        # Generate seed if not provided
        if seed is None:
            seed = random.randint(0, 2**32 - 1)
        
        # Check GPU provider health
        if not await self.gpu_provider.health_check():
            raise GenerationError("GPU provider is not available")
        
        # Generate image
        image_bytes = await self.gpu_provider.generate(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            steps=steps,
            cfg_scale=cfg_scale,
            seed=seed,
        )
        
        # Encrypt image
        encrypted_image = self.crypto.encrypt(image_bytes, session.master_key)
        
        # Store encrypted image in vault
        vault_path = self.vault_storage.store(
            user_id=session.user_id,
            blob=encrypted_image,
            filename=f"image_{seed}.png",
        )
        
        # Create metadata
        metadata = ImageMetadata(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            steps=steps,
            cfg_scale=cfg_scale,
            seed=seed,
            provider=self.gpu_provider.__class__.__name__,
            created_at=datetime.utcnow(),
        )
        
        # Encrypt metadata
        metadata_dict = metadata.model_dump()
        metadata_dict["created_at"] = metadata.created_at.isoformat()
        encrypted_metadata = self.crypto.encrypt_metadata(metadata_dict, session.master_key)
        
        # Create image record
        image = Image(
            user_id=session.user_id,
            vault_path=vault_path,
            metadata_blob=encrypted_metadata,
        )
        
        # Persist
        return self.image_repo.create(image)

