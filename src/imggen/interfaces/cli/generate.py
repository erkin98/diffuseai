"""Image generation commands."""

import asyncio
from typing import Optional
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from imggen.config import settings
from imggen.domain.crypto import CryptoService
from imggen.domain.exceptions import SessionNotFoundError, GenerationError
from imggen.domain.models import MODELS, ModelSize, get_model_by_name
from imggen.infrastructure.database.sqlite import SQLiteImageRepository
from imggen.infrastructure.gpu.comfyui import ComfyUIProvider
from imggen.infrastructure.storage.local import LocalVaultStorage
from imggen.infrastructure.session import SessionManager
from imggen.application.generation import GenerateImageUseCase

generate_app = typer.Typer()
console = Console()


@generate_app.command("models")
def list_models():
    """List available model sizes."""
    from rich.table import Table
    
    table = Table(title="Available Models", show_header=True)
    table.add_column("Size", style="cyan", no_wrap=True)
    table.add_column("Model", style="white")
    table.add_column("Native Size", style="green")
    table.add_column("Steps", style="yellow")
    table.add_column("Min VRAM", style="magenta")
    table.add_column("Description", style="dim")
    
    for size, config in MODELS.items():
        table.add_row(
            size.value,
            config.name,
            f"{config.native_width}x{config.native_height}",
            str(config.recommended_steps),
            f"{config.min_vram_gb}GB",
            config.description,
        )
    
    console.print()
    console.print(table)
    console.print()
    console.print("[dim]Usage:[/dim] ./dev.sh generate generate \"prompt\" --model [cyan]small[/cyan]|[cyan]medium[/cyan]|[cyan]large[/cyan]")
    console.print()


def get_dependencies(model_size: str = "large"):
    """Get shared dependencies."""
    settings.ensure_dirs()
    image_repo = SQLiteImageRepository(settings.db_path)
    gpu_provider = ComfyUIProvider(
        base_url=settings.comfyui_url,
        timeout=settings.comfyui_timeout,
        workflow_path=None,
        model_size=model_size,
    )
    vault_storage = LocalVaultStorage(settings.vault_dir)
    crypto_service = CryptoService(
        time_cost=settings.argon2_time_cost,
        memory_cost=settings.argon2_memory_cost,
        parallelism=settings.argon2_parallelism,
    )
    session_manager = SessionManager(
        settings.session_dir,
        timeout=settings.session_timeout,
    )
    return image_repo, gpu_provider, vault_storage, crypto_service, session_manager


@generate_app.command()
def generate(
    prompt: str = typer.Argument(..., help="Generation prompt"),
    negative_prompt: str = typer.Option("", "-n", "--negative", help="Negative prompt"),
    width: int = typer.Option(None, "--width", help="Image width"),
    height: int = typer.Option(None, "--height", help="Image height"),
    steps: int = typer.Option(None, "--steps", help="Sampling steps"),
    cfg_scale: float = typer.Option(None, "--cfg", help="CFG scale"),
    seed: Optional[int] = typer.Option(None, "--seed", help="Random seed"),
    size: Optional[str] = typer.Option(None, "--size", help="Size as WIDTHxHEIGHT (e.g., 1024x1024)"),
    model: str = typer.Option("large", "-m", "--model", help="Model size (small/medium/large)"),
):
    """Generate an AI image with E2E encryption."""
    
    # Validate and get model config
    try:
        model_config = get_model_by_name(model)
    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {e}", style="red")
        console.print("\n[dim]Available models:[/dim]")
        for size, config in MODELS.items():
            console.print(f"  [cyan]{size.value}[/cyan]: {config.name}")
            console.print(f"    {config.description}")
            console.print(f"    Native: {config.native_width}x{config.native_height}, "
                        f"Steps: {config.recommended_steps}, "
                        f"Min VRAM: {config.min_vram_gb}GB\n")
        raise typer.Exit(1)
    
    # Parse size if provided
    if size:
        try:
            w, h = size.lower().split("x")
            width = int(w)
            height = int(h)
        except ValueError:
            console.print("[bold red]Error:[/bold red] Invalid size format. Use WIDTHxHEIGHT (e.g., 1024x1024)", style="red")
            raise typer.Exit(1)
    
    # Use defaults based on model or config
    if not width or not height:
        if not size:
            width = model_config.native_width
            height = model_config.native_height
    
    width = width or settings.default_width
    height = height or settings.default_height
    steps = steps or model_config.recommended_steps
    cfg_scale = cfg_scale or settings.default_cfg
    
    try:
        image_repo, gpu_provider, vault_storage, crypto_service, session_manager = get_dependencies(model)
        use_case = GenerateImageUseCase(
            image_repo, gpu_provider, vault_storage, crypto_service, session_manager
        )
        
        console.print(f"\n[bold cyan]Generating Image[/bold cyan]\n")
        console.print(f"[dim]Model:[/dim] {model_config.name} ({model.upper()})")
        console.print(f"[dim]Prompt:[/dim] {prompt}")
        if negative_prompt:
            console.print(f"[dim]Negative:[/dim] {negative_prompt}")
        console.print(f"[dim]Size:[/dim] {width}x{height}")
        console.print(f"[dim]Steps:[/dim] {steps}")
        console.print(f"[dim]CFG:[/dim] {cfg_scale}")
        if seed is not None:
            console.print(f"[dim]Seed:[/dim] {seed}")
        console.print()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task(description="Generating image...", total=None)
            
            image = asyncio.run(
                use_case.execute(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    width=width,
                    height=height,
                    steps=steps,
                    cfg_scale=cfg_scale,
                    seed=seed,
                )
            )
        
        console.print(f"\n[bold green]✓[/bold green] Image generated successfully!")
        console.print(f"[dim]Image ID:[/dim] {image.id}")
        console.print(f"\n[dim]View with:[/dim] imggen gallery info {image.id}")
        console.print(f"[dim]Export with:[/dim] imggen gallery export {image.id} output.png\n")
        
    except SessionNotFoundError as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}", style="red")
        console.print("[dim]Please login first: imggen user login[/dim]\n")
        raise typer.Exit(1)
    except GenerationError as e:
        console.print(f"\n[bold red]Generation Error:[/bold red] {e}", style="red")
        console.print("\n[dim]Make sure ComfyUI is running at:[/dim]")
        console.print(f"  {settings.comfyui_url}\n")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}", style="red")
        raise typer.Exit(1)

