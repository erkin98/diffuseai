"""Abstract GPU provider interface."""

from abc import ABC, abstractmethod
from typing import Optional


class GPUProvider(ABC):
    """Abstract GPU provider for image generation."""
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 1024,
        steps: int = 25,
        cfg_scale: float = 7.0,
        seed: Optional[int] = None,
    ) -> bytes:
        """
        Generate an image and return PNG bytes.
        
        Args:
            prompt: Generation prompt
            negative_prompt: Negative prompt
            width: Image width
            height: Image height
            steps: Sampling steps
            cfg_scale: CFG scale
            seed: Random seed (None for random)
        
        Returns:
            PNG image bytes
        
        Raises:
            GenerationError: If generation fails
        """
        pass
    
    async def img2img(
        self,
        input_image: bytes,
        prompt: str,
        strength: float = 0.75,
        negative_prompt: str = "",
        steps: int = 25,
        cfg_scale: float = 7.0,
        seed: Optional[int] = None,
    ) -> bytes:
        """
        Transform an image using img2img (optional - not all providers support this).
        
        Args:
            input_image: Input image as bytes
            prompt: Transformation/style prompt
            strength: How much to change (0.0-1.0, higher = more change)
            negative_prompt: Negative prompt
            steps: Sampling steps
            cfg_scale: CFG scale
            seed: Random seed
        
        Returns:
            Transformed PNG image bytes
        
        Raises:
            NotImplementedError: If provider doesn't support img2img
        """
        raise NotImplementedError("This provider does not support img2img")
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if provider is available and healthy.
        
        Returns:
            True if provider is available
        """
        pass

