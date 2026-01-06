"""Gallery management commands."""

from pathlib import Path
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from imggen.config import settings
from imggen.domain.crypto import CryptoService
from imggen.domain.exceptions import SessionNotFoundError, ImageNotFoundError
from imggen.infrastructure.database.sqlite import SQLiteImageRepository
from imggen.infrastructure.storage.local import LocalVaultStorage
from imggen.infrastructure.session import SessionManager
from imggen.application.gallery import (
    ListImagesUseCase,
    GetImageMetadataUseCase,
    ExportImageUseCase,
    DeleteImageUseCase,
    SearchImagesUseCase,
)

gallery_app = typer.Typer()
console = Console()


def get_dependencies():
    """Get shared dependencies."""
    settings.ensure_dirs()
    image_repo = SQLiteImageRepository(settings.db_path)
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
    return image_repo, vault_storage, crypto_service, session_manager


@gallery_app.command("list")
def list_images(
    limit: int = typer.Option(100, "--limit", "-l", help="Maximum number of images"),
    offset: int = typer.Option(0, "--offset", "-o", help="Offset for pagination"),
):
    """List all images in gallery."""
    try:
        image_repo, _, crypto_service, session_manager = get_dependencies()
        use_case = ListImagesUseCase(image_repo, session_manager)
        
        images = use_case.execute(limit=limit, offset=offset)
        
        if not images:
            console.print("\n[yellow]No images found[/yellow]\n")
            console.print("[dim]Generate your first image with:[/dim] imggen generate \"your prompt\"\n")
            return
        
        # Get metadata use case for decryption
        metadata_use_case = GetImageMetadataUseCase(image_repo, crypto_service, session_manager)
        
        table = Table(title=f"Image Gallery ({len(images)} images)", show_header=True)
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Prompt", style="white")
        table.add_column("Size", style="green", no_wrap=True)
        table.add_column("Created", style="dim", no_wrap=True)
        
        for image in images:
            try:
                metadata = metadata_use_case.execute(image.id)  # type: ignore
                prompt_preview = metadata.prompt[:50] + "..." if len(metadata.prompt) > 50 else metadata.prompt
                size_str = f"{metadata.width}x{metadata.height}"
                created_str = metadata.created_at.strftime("%Y-%m-%d %H:%M")
                
                table.add_row(
                    str(image.id),
                    prompt_preview,
                    size_str,
                    created_str,
                )
            except Exception:
                # Skip images with decryption errors
                table.add_row(str(image.id), "[red]Decryption error[/red]", "-", "-")
        
        console.print()
        console.print(table)
        console.print()
        
    except SessionNotFoundError as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}", style="red")
        console.print("[dim]Please login first: imggen user login[/dim]\n")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}", style="red")
        raise typer.Exit(1)


@gallery_app.command("info")
def show_info(image_id: int = typer.Argument(..., help="Image ID")):
    """Show detailed image information."""
    try:
        image_repo, _, crypto_service, session_manager = get_dependencies()
        use_case = GetImageMetadataUseCase(image_repo, crypto_service, session_manager)
        
        metadata = use_case.execute(image_id)
        
        # Create info panel
        info_text = f"""[bold]Prompt:[/bold] {metadata.prompt}

[bold]Negative Prompt:[/bold] {metadata.negative_prompt or '(none)'}

[bold]Size:[/bold] {metadata.width}x{metadata.height}
[bold]Steps:[/bold] {metadata.steps}
[bold]CFG Scale:[/bold] {metadata.cfg_scale}
[bold]Seed:[/bold] {metadata.seed}
[bold]Sampler:[/bold] {metadata.sampler}
[bold]Model:[/bold] {metadata.model}
[bold]Provider:[/bold] {metadata.provider}

[bold]Created:[/bold] {metadata.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}
"""
        
        panel = Panel(
            info_text,
            title=f"[bold cyan]Image #{image_id}[/bold cyan]",
            border_style="cyan",
        )
        
        console.print()
        console.print(panel)
        console.print()
        
    except SessionNotFoundError as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}", style="red")
        console.print("[dim]Please login first: imggen user login[/dim]\n")
        raise typer.Exit(1)
    except ImageNotFoundError as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}", style="red")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}", style="red")
        raise typer.Exit(1)


@gallery_app.command("export")
def export_image(
    image_id: int = typer.Argument(..., help="Image ID"),
    output: str = typer.Argument(..., help="Output file path"),
):
    """Decrypt and export image to file."""
    try:
        image_repo, vault_storage, crypto_service, session_manager = get_dependencies()
        use_case = ExportImageUseCase(image_repo, vault_storage, crypto_service, session_manager)
        
        output_path = Path(output)
        
        with console.status(f"[bold green]Exporting image {image_id}..."):
            result_path = use_case.execute(image_id, output_path)
        
        console.print(f"\n[bold green]✓[/bold green] Image exported to: {result_path}\n")
        
    except SessionNotFoundError as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}", style="red")
        console.print("[dim]Please login first: imggen user login[/dim]\n")
        raise typer.Exit(1)
    except ImageNotFoundError as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}", style="red")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}", style="red")
        raise typer.Exit(1)


@gallery_app.command("delete")
def delete_image(
    image_id: int = typer.Argument(..., help="Image ID"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
):
    """Delete an image."""
    try:
        if not yes:
            confirm = typer.confirm(f"Delete image {image_id}?")
            if not confirm:
                console.print("\n[yellow]Cancelled[/yellow]\n")
                return
        
        image_repo, vault_storage, _, session_manager = get_dependencies()
        use_case = DeleteImageUseCase(image_repo, vault_storage, session_manager)
        
        with console.status(f"[bold green]Deleting image {image_id}..."):
            deleted = use_case.execute(image_id)
        
        if deleted:
            console.print(f"\n[bold green]✓[/bold green] Image {image_id} deleted\n")
        else:
            console.print(f"\n[yellow]Image {image_id} not found[/yellow]\n")
        
    except SessionNotFoundError as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}", style="red")
        console.print("[dim]Please login first: imggen user login[/dim]\n")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}", style="red")
        raise typer.Exit(1)


@gallery_app.command("search")
def search_images(
    keyword: str = typer.Argument(..., help="Search keyword"),
    limit: int = typer.Option(100, "--limit", "-l", help="Maximum results"),
):
    """Search images by prompt keyword."""
    try:
        image_repo, _, crypto_service, session_manager = get_dependencies()
        use_case = SearchImagesUseCase(image_repo, crypto_service, session_manager)
        
        with console.status(f"[bold green]Searching for '{keyword}'..."):
            results = use_case.execute(keyword, limit=limit)
        
        if not results:
            console.print(f"\n[yellow]No images found matching '{keyword}'[/yellow]\n")
            return
        
        table = Table(title=f"Search Results ({len(results)} images)", show_header=True)
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Prompt", style="white")
        table.add_column("Size", style="green", no_wrap=True)
        table.add_column("Created", style="dim", no_wrap=True)
        
        for image, metadata in results:
            prompt_preview = metadata.prompt[:50] + "..." if len(metadata.prompt) > 50 else metadata.prompt
            size_str = f"{metadata.width}x{metadata.height}"
            created_str = metadata.created_at.strftime("%Y-%m-%d %H:%M")
            
            table.add_row(
                str(image.id),
                prompt_preview,
                size_str,
                created_str,
            )
        
        console.print()
        console.print(table)
        console.print()
        
    except SessionNotFoundError as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}", style="red")
        console.print("[dim]Please login first: imggen user login[/dim]\n")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}", style="red")
        raise typer.Exit(1)

