"""Main CLI application."""

import typer
from rich.console import Console

from .user import user_app
from .generate import generate_app
from .gallery import gallery_app
from .config import config_app
from .img2img import img2img_app

app = typer.Typer(
    name="imggen",
    help="Secure AI Image Generation with E2E Encryption",
    no_args_is_help=True,
)

console = Console()

# Add subcommands
app.add_typer(user_app, name="user", help="User management")
app.add_typer(generate_app, name="generate", help="Generate images")
app.add_typer(gallery_app, name="gallery", help="Manage image gallery")
app.add_typer(img2img_app, name="img2img", help="Image-to-image transformation")
app.add_typer(config_app, name="config", help="Configuration")


@app.callback()
def callback():
    """Secure AI Image Generation Platform."""
    pass


def main():
    """Entry point for CLI."""
    app()


if __name__ == "__main__":
    main()

