"""Image-to-image transformation commands."""

import asyncio
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from imggen.config import settings
from imggen.domain.crypto import CryptoService
from imggen.domain.exceptions import SessionNotFoundError, GenerationError, ImageNotFoundError
from imggen.infrastructure.database.sqlite import SQLiteImageRepository
from imggen.infrastructure.gpu.comfyui import ComfyUIProvider
from imggen.infrastructure.storage.local import LocalVaultStorage
from imggen.infrastructure.session import SessionManager
from imggen.application.img2img import Img2ImgUseCase, RestyleImageUseCase

img2img_app = typer.Typer()
console = Console()


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


@img2img_app.command("transform")
def img2img_transform(
    input_path: str = typer.Argument(..., help="Input image path"),
    prompt: str = typer.Argument(..., help="Style/transformation prompt"),
    output: Optional[str] = typer.Option(None, "-o", "--output", help="Output path (optional)"),
    strength: float = typer.Option(0.75, "-s", "--strength", help="Transformation strength (0.0-1.0)"),
    negative_prompt: str = typer.Option("", "-n", "--negative", help="Negative prompt"),
    steps: int = typer.Option(25, "--steps", help="Sampling steps"),
    cfg_scale: float = typer.Option(7.0, "--cfg", help="CFG scale"),
    seed: Optional[int] = typer.Option(None, "--seed", help="Random seed"),
    model: str = typer.Option("medium", "-m", "--model", help="Model size (small/medium/large)"),
):
    """Transform an image using img2img (e.g., restyle to Ghibli)."""
    
    input_image_path = Path(input_path)
    
    try:
        image_repo, gpu_provider, vault_storage, crypto_service, session_manager = get_dependencies(model)
        use_case = Img2ImgUseCase(
            image_repo, gpu_provider, vault_storage, crypto_service, session_manager
        )
        
        console.print(f"\n[bold cyan]Transforming Image[/bold cyan]\n")
        console.print(f"[dim]Input:[/dim] {input_image_path}")
        console.print(f"[dim]Style:[/dim] {prompt}")
        console.print(f"[dim]Strength:[/dim] {strength} (0.0=keep original, 1.0=full transform)")
        console.print(f"[dim]Model:[/dim] {model}")
        console.print(f"[dim]Steps:[/dim] {steps}")
        console.print()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task(description="Transforming image...", total=None)
            
            image = asyncio.run(
                use_case.execute(
                    input_image_path=input_image_path,
                    prompt=prompt,
                    strength=strength,
                    negative_prompt=negative_prompt,
                    steps=steps,
                    cfg_scale=cfg_scale,
                    seed=seed,
                )
            )
        
        console.print(f"\n[bold green]✓[/bold green] Image transformed successfully!")
        console.print(f"[dim]Image ID:[/dim] {image.id}")
        
        # Export if output path specified
        if output:
            from imggen.application.gallery import ExportImageUseCase
            export_use_case = ExportImageUseCase(
                image_repo, vault_storage, crypto_service, session_manager
            )
            export_use_case.execute(image.id, Path(output))  # type: ignore
            console.print(f"[dim]Exported to:[/dim] {output}")
        else:
            console.print(f"\n[dim]Export with:[/dim] imggen gallery export {image.id} output.png\n")
        
    except SessionNotFoundError as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}", style="red")
        console.print("[dim]Please login first: just login[/dim]\n")
        raise typer.Exit(1)
    except GenerationError as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}", style="red")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}", style="red")
        raise typer.Exit(1)


@img2img_app.command("restyle")
def restyle_image(
    image_id: int = typer.Argument(..., help="Gallery image ID to restyle"),
    style: str = typer.Argument(..., help="Style description (e.g., 'Studio Ghibli')"),
    output: Optional[str] = typer.Option(None, "-o", "--output", help="Output path (optional)"),
    strength: float = typer.Option(0.75, "-s", "--strength", help="Transformation strength (0.0-1.0)"),
    negative_prompt: str = typer.Option("", "-n", "--negative", help="Negative prompt"),
):
    """Restyle an existing gallery image."""
    
    try:
        image_repo, gpu_provider, vault_storage, crypto_service, session_manager = get_dependencies()
        use_case = RestyleImageUseCase(
            image_repo, gpu_provider, vault_storage, crypto_service, session_manager
        )
        
        console.print(f"\n[bold cyan]Restyling Image #{image_id}[/bold cyan]\n")
        console.print(f"[dim]Style:[/dim] {style}")
        console.print(f"[dim]Strength:[/dim] {strength}")
        console.print()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task(description="Restyling image...", total=None)
            
            new_image = asyncio.run(
                use_case.execute(
                    image_id=image_id,
                    style_prompt=style,
                    strength=strength,
                    negative_prompt=negative_prompt,
                )
            )
        
        console.print(f"\n[bold green]✓[/bold green] Image restyled successfully!")
        console.print(f"[dim]New Image ID:[/dim] {new_image.id}")
        
        # Export if output specified
        if output:
            from imggen.application.gallery import ExportImageUseCase
            export_use_case = ExportImageUseCase(
                image_repo, vault_storage, crypto_service, session_manager
            )
            export_use_case.execute(new_image.id, Path(output))  # type: ignore
            console.print(f"[dim]Exported to:[/dim] {output}\n")
        else:
            console.print(f"\n[dim]Export with:[/dim] just export {new_image.id} output.png\n")
        
    except (SessionNotFoundError, ImageNotFoundError, GenerationError) as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}", style="red")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}", style="red")
        raise typer.Exit(1)

