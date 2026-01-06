"""Cloud GPU provider (future implementation)."""

from typing import Optional
from .base import GPUProvider
from imggen.domain.exceptions import GenerationError


class CloudGPUProvider(GPUProvider):
    """
    Cloud GPU provider for fallback (RunPod, Modal, Replicate).
    
    This is a placeholder for future implementation.
    """
    
    def __init__(self, api_key: str, provider: str = "runpod"):
        self.api_key = api_key
        self.provider = provider
    
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
        """Generate image using cloud GPU."""
        raise NotImplementedError("Cloud GPU provider not yet implemented")
    
    async def health_check(self) -> bool:
        """Check if cloud provider is available."""
        return False

