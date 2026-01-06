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
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if provider is available and healthy.
        
        Returns:
            True if provider is available
        """
        pass

