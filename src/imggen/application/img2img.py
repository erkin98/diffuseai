"""Image-to-image transformation use cases."""

from pathlib import Path
from typing import Optional
from PIL import Image as PILImage
import io

from imggen.domain.entities import Image
from imggen.domain.crypto import CryptoService
from imggen.domain.value_objects import ImageMetadata
from imggen.domain.exceptions import ImageNotFoundError, GenerationError
from imggen.infrastructure.database.base import ImageRepository
from imggen.infrastructure.gpu.base import GPUProvider
from imggen.infrastructure.storage.base import VaultStorage
from imggen.infrastructure.session import SessionManager


class Img2ImgUseCase:
    """Image-to-image transformation with style transfer."""

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
        input_image_path: Path,
        prompt: str,
        strength: float = 0.75,
        negative_prompt: str = "",
        steps: int = 25,
        cfg_scale: float = 7.0,
        seed: Optional[int] = None,
    ) -> Image:
        """
        Transform an image using img2img.

        Args:
            input_image_path: Path to input image
            prompt: Style/transformation prompt
            strength: How much to change (0.0-1.0, higher = more change)
            negative_prompt: Negative prompt
            steps: Sampling steps
            cfg_scale: CFG scale
            seed: Random seed

        Returns:
            Created Image entity with transformed image

        Raises:
            SessionNotFoundError: If not logged in
            GenerationError: If transformation fails
        """
        # Require session
        session = self.session_manager.require_session()

        # Load input image
        if not input_image_path.exists():
            raise GenerationError(f"Input image not found: {input_image_path}")

        with open(input_image_path, "rb") as f:
            input_image_bytes = f.read()

        # Check GPU provider health
        if not await self.gpu_provider.health_check():
            raise GenerationError("GPU provider is not available")

        # Check if provider supports img2img
        if not hasattr(self.gpu_provider, "img2img"):
            raise GenerationError("GPU provider does not support img2img")

        # Transform image
        output_image_bytes = await self.gpu_provider.img2img(
            input_image=input_image_bytes,
            prompt=prompt,
            strength=strength,
            negative_prompt=negative_prompt,
            steps=steps,
            cfg_scale=cfg_scale,
            seed=seed,
        )

        # Get image dimensions
        img = PILImage.open(io.BytesIO(output_image_bytes))
        width, height = img.size

        # Encrypt image
        encrypted_image = self.crypto.encrypt(output_image_bytes, session.master_key)

        # Store in vault
        vault_path = self.vault_storage.store(
            user_id=session.user_id,
            blob=encrypted_image,
            filename=f"img2img_{seed or 0}.png",
        )

        # Create metadata
        from datetime import datetime
        import random

        if seed is None:
            seed = random.randint(0, 2**32 - 1)

        metadata = ImageMetadata(
            prompt=f"[img2img] {prompt}",
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
        encrypted_metadata = self.crypto.encrypt_metadata(
            metadata_dict, session.master_key
        )

        # Create image record
        image = Image(
            user_id=session.user_id,
            vault_path=vault_path,
            metadata_blob=encrypted_metadata,
        )

        # Persist
        return self.image_repo.create(image)


class RestyleImageUseCase:
    """Restyle an existing image in the gallery."""

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
        image_id: int,
        style_prompt: str,
        strength: float = 0.75,
        negative_prompt: str = "",
    ) -> Image:
        """
        Restyle an existing gallery image.

        Args:
            image_id: ID of image to restyle
            style_prompt: Style description (e.g., "Studio Ghibli style")
            strength: How much to change (0.0-1.0)
            negative_prompt: Negative prompt

        Returns:
            New Image entity with restyled version
        """
        session = self.session_manager.require_session()

        # Get original image
        original = self.image_repo.get_by_id(image_id, session.user_id)
        if not original:
            raise ImageNotFoundError(f"Image {image_id} not found")

        # Retrieve and decrypt original
        encrypted_blob = self.vault_storage.retrieve(original.vault_path)
        if not encrypted_blob:
            raise GenerationError("Failed to retrieve original image")

        decrypted_bytes = self.crypto.decrypt(encrypted_blob, session.master_key)

        # Get original metadata for seed
        metadata_dict = self.crypto.decrypt_metadata(
            original.metadata_blob, session.master_key
        )
        original_metadata = ImageMetadata(**metadata_dict)

        # Check provider support
        if not hasattr(self.gpu_provider, "img2img"):
            raise GenerationError("GPU provider does not support img2img")

        # Transform
        output_bytes = await self.gpu_provider.img2img(
            input_image=decrypted_bytes,
            prompt=style_prompt,
            strength=strength,
            negative_prompt=negative_prompt,
            steps=original_metadata.steps,
            cfg_scale=original_metadata.cfg_scale,
            seed=original_metadata.seed,
        )

        # Get dimensions
        img = PILImage.open(io.BytesIO(output_bytes))
        width, height = img.size

        # Encrypt and store
        encrypted_image = self.crypto.encrypt(output_bytes, session.master_key)
        vault_path = self.vault_storage.store(
            user_id=session.user_id,
            blob=encrypted_image,
            filename=f"restyle_{image_id}_{original_metadata.seed}.png",
        )

        # Create metadata
        from datetime import datetime

        new_metadata = ImageMetadata(
            prompt=f"[Restyled from #{image_id}] {style_prompt}",
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            steps=original_metadata.steps,
            cfg_scale=original_metadata.cfg_scale,
            seed=original_metadata.seed,
            provider=self.gpu_provider.__class__.__name__,
            created_at=datetime.utcnow(),
        )

        # Encrypt metadata
        metadata_dict = new_metadata.model_dump()
        metadata_dict["created_at"] = new_metadata.created_at.isoformat()
        encrypted_metadata = self.crypto.encrypt_metadata(
            metadata_dict, session.master_key
        )

        # Create record
        new_image = Image(
            user_id=session.user_id,
            vault_path=vault_path,
            metadata_blob=encrypted_metadata,
        )

        return self.image_repo.create(new_image)
