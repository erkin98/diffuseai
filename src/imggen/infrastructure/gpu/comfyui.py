"""ComfyUI local GPU provider."""

import asyncio
import json
import random
import uuid
from pathlib import Path
from typing import Optional, Dict, Any
import httpx
import websockets

from imggen.domain.exceptions import GenerationError
from imggen.domain.models import get_model_by_name, ModelSize, MODELS
from .base import GPUProvider


class ComfyUIProvider(GPUProvider):
    """
    ComfyUI local provider for multiple model sizes.
    
    Supports small (SD 1.5), medium (SD 2.1), and large (SDXL) models.
    """
    
    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8188",
        timeout: int = 300,
        workflow_path: Optional[Path] = None,
        model_size: str = "large",
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.workflow_path = workflow_path
        self.model_size = model_size
        self.client_id = str(uuid.uuid4())
    
    def _load_workflow(self) -> Dict[str, Any]:
        """Load workflow template."""
        if self.workflow_path and self.workflow_path.exists():
            with open(self.workflow_path, "r") as f:
                return json.load(f)
        
        # Return default workflow based on model size
        return self._get_default_workflow()
    
    def _get_default_workflow(self) -> Dict[str, Any]:
        """Get default workflow based on model size."""
        model_config = get_model_by_name(self.model_size)
        
        return {
            "1": {
                "inputs": {
                    "ckpt_name": model_config.checkpoint
                },
                "class_type": "CheckpointLoaderSimple"
            },
            "2": {
                "inputs": {
                    "text": "PROMPT_PLACEHOLDER",
                    "clip": ["1", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "3": {
                "inputs": {
                    "text": "NEGATIVE_PROMPT_PLACEHOLDER",
                    "clip": ["1", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "4": {
                "inputs": {
                    "width": 1024,
                    "height": 1024,
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage"
            },
            "5": {
                "inputs": {
                    "seed": 42,
                    "steps": 25,
                    "cfg": 7.0,
                    "sampler_name": "dpmpp_2m",
                    "scheduler": "karras",
                    "denoise": 1.0,
                    "model": ["1", 0],
                    "positive": ["2", 0],
                    "negative": ["3", 0],
                    "latent_image": ["4", 0]
                },
                "class_type": "KSampler"
            },
            "6": {
                "inputs": {
                    "samples": ["5", 0],
                    "vae": ["1", 2]
                },
                "class_type": "VAEDecode"
            },
            "7": {
                "inputs": {
                    "filename_prefix": "imggen",
                    "images": ["6", 0]
                },
                "class_type": "SaveImage"
            }
        }
    
    def _prepare_workflow(
        self,
        prompt: str,
        negative_prompt: str,
        width: int,
        height: int,
        steps: int,
        cfg_scale: float,
        seed: Optional[int],
    ) -> Dict[str, Any]:
        """Prepare workflow with parameters."""
        workflow = self._load_workflow()
        
        # Set seed
        if seed is None:
            seed = random.randint(0, 2**32 - 1)
        
        # Update workflow parameters
        workflow["2"]["inputs"]["text"] = prompt
        workflow["3"]["inputs"]["text"] = negative_prompt
        workflow["4"]["inputs"]["width"] = width
        workflow["4"]["inputs"]["height"] = height
        workflow["5"]["inputs"]["seed"] = seed
        workflow["5"]["inputs"]["steps"] = steps
        workflow["5"]["inputs"]["cfg"] = cfg_scale
        
        return workflow
    
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
        """Generate image using ComfyUI."""
        try:
            # Prepare workflow
            workflow = self._prepare_workflow(
                prompt, negative_prompt, width, height, steps, cfg_scale, seed
            )
            
            # Queue prompt
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/prompt",
                    json={
                        "prompt": workflow,
                        "client_id": self.client_id,
                    },
                )
                response.raise_for_status()
                result = response.json()
                prompt_id = result["prompt_id"]
            
            # Wait for completion via WebSocket
            ws_url = self.base_url.replace("http://", "ws://").replace("https://", "wss://")
            async with websockets.connect(f"{ws_url}/ws?clientId={self.client_id}") as ws:
                while True:
                    message = await ws.recv()
                    data = json.loads(message)
                    
                    if data.get("type") == "executing":
                        executing_data = data.get("data", {})
                        if executing_data.get("prompt_id") == prompt_id and executing_data.get("node") is None:
                            # Execution finished
                            break
            
            # Get history to find output images
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/history/{prompt_id}")
                response.raise_for_status()
                history = response.json()
            
            # Extract output image
            outputs = history[prompt_id]["outputs"]
            for node_id, node_output in outputs.items():
                if "images" in node_output:
                    image_info = node_output["images"][0]
                    filename = image_info["filename"]
                    subfolder = image_info.get("subfolder", "")
                    folder_type = image_info.get("type", "output")
                    
                    # Download image
                    async with httpx.AsyncClient(timeout=self.timeout) as client:
                        params = {
                            "filename": filename,
                            "subfolder": subfolder,
                            "type": folder_type,
                        }
                        response = await client.get(
                            f"{self.base_url}/view",
                            params=params,
                        )
                        response.raise_for_status()
                        return response.content
            
            raise GenerationError("No output image found in ComfyUI response")
            
        except Exception as e:
            raise GenerationError(f"ComfyUI generation failed: {e}")
    
    async def health_check(self) -> bool:
        """Check if ComfyUI is available."""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.base_url}/system_stats")
                return response.status_code == 200
        except Exception:
            return False

