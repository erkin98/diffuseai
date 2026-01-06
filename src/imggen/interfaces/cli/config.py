"""Configuration commands."""

import typer
from rich.console import Console
from rich.table import Table

from imggen.config import settings

config_app = typer.Typer()
console = Console()


@config_app.command("show")
def show_config():
    """Show current configuration."""
    table = Table(title="Configuration", show_header=True)
    table.add_column("Setting", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")
    
    table.add_row("Data Directory", str(settings.data_dir))
    table.add_row("Database Path", str(settings.db_path))
    table.add_row("Vault Directory", str(settings.vault_dir))
    table.add_row("Session Directory", str(settings.session_dir))
    table.add_row("Workflow Directory", str(settings.workflow_dir))
    table.add_row("", "")
    table.add_row("ComfyUI URL", settings.comfyui_url)
    table.add_row("ComfyUI Timeout", f"{settings.comfyui_timeout}s")
    table.add_row("", "")
    table.add_row("Session Timeout", f"{settings.session_timeout}s")
    table.add_row("", "")
    table.add_row("Default Width", str(settings.default_width))
    table.add_row("Default Height", str(settings.default_height))
    table.add_row("Default Steps", str(settings.default_steps))
    table.add_row("Default CFG", str(settings.default_cfg))
    
    console.print()
    console.print(table)
    console.print()
    console.print("[dim]Configuration can be changed via environment variables:[/dim]")
    console.print("[dim]  IMGGEN_COMFYUI_URL, IMGGEN_DEFAULT_STEPS, etc.[/dim]\n")


@config_app.command("set")
def set_config(
    key: str = typer.Argument(..., help="Configuration key (e.g., comfyui.url)"),
    value: str = typer.Argument(..., help="Configuration value"),
):
    """Set configuration value (placeholder - use env vars for now)."""
    console.print("\n[yellow]Configuration changes via CLI are not yet implemented.[/yellow]")
    console.print("\n[dim]Use environment variables instead:[/dim]")
    console.print(f"  export IMGGEN_{key.upper().replace('.', '_')}={value}\n")

