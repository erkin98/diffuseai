"""Model configuration and metadata."""

from enum import Enum
from typing import Dict
from pydantic import BaseModel


class ModelSize(str, Enum):
    """Supported model sizes."""
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class ModelConfig(BaseModel):
    """Configuration for a specific model."""
    name: str
    checkpoint: str
    native_width: int
    native_height: int
    recommended_steps: int
    min_vram_gb: float
    description: str


# Model configurations
MODELS: Dict[ModelSize, ModelConfig] = {
    ModelSize.SMALL: ModelConfig(
        name="Stable Diffusion 1.5",
        checkpoint="v1-5-pruned-emaonly.safetensors",
        native_width=512,
        native_height=512,
        recommended_steps=20,
        min_vram_gb=2.0,
        description="Fast generation, lower quality. Good for quick iterations.",
    ),
    ModelSize.MEDIUM: ModelConfig(
        name="Stable Diffusion 2.1",
        checkpoint="v2-1_768-ema-pruned.safetensors",
        native_width=768,
        native_height=768,
        recommended_steps=25,
        min_vram_gb=4.0,
        description="Balanced speed and quality. Works on most GPUs.",
    ),
    ModelSize.LARGE: ModelConfig(
        name="SDXL Base 1.0",
        checkpoint="sd_xl_base_1.0.safetensors",
        native_width=1024,
        native_height=1024,
        recommended_steps=25,
        min_vram_gb=8.0,
        description="Best quality, slower generation. Requires powerful GPU.",
    ),
}


def get_model_config(size: ModelSize) -> ModelConfig:
    """Get configuration for a model size."""
    return MODELS[size]


def get_model_by_name(name: str) -> ModelConfig:
    """Get model configuration by size name."""
    try:
        size = ModelSize(name.lower())
        return MODELS[size]
    except (ValueError, KeyError):
        raise ValueError(f"Invalid model size: {name}. Choose from: small, medium, large")

