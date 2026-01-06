"""Application configuration with environment support."""

from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_prefix="IMGGEN_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # Paths
    data_dir: Path = Field(default=Path("data"), description="Data directory")
    db_path: Path = Field(default=Path("data/imggen.db"), description="Database path")
    vault_dir: Path = Field(default=Path("data/vaults"), description="Vault storage directory")
    session_dir: Path = Field(default=Path("data/sessions"), description="Session directory")
    workflow_dir: Path = Field(default=Path("workflows"), description="Workflow templates directory")
    
    # ComfyUI
    comfyui_url: str = Field(default="http://127.0.0.1:8188", description="ComfyUI API URL")
    comfyui_timeout: int = Field(default=300, description="ComfyUI request timeout (seconds)")
    
    # Security
    session_timeout: int = Field(default=3600, description="Session timeout in seconds")
    argon2_time_cost: int = Field(default=3, description="Argon2 time cost")
    argon2_memory_cost: int = Field(default=65536, description="Argon2 memory cost (KB)")
    argon2_parallelism: int = Field(default=4, description="Argon2 parallelism")
    
    # Generation defaults
    default_width: int = Field(default=1024, description="Default image width")
    default_height: int = Field(default=1024, description="Default image height")
    default_steps: int = Field(default=25, description="Default sampling steps")
    default_cfg: float = Field(default=7.0, description="Default CFG scale")
    default_model: str = Field(default="large", description="Default model size (small/medium/large)")
    
    def ensure_dirs(self) -> None:
        """Create necessary directories if they don't exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self.session_dir.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()

