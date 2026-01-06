"""User management commands."""

import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table

from imggen.config import settings
from imggen.domain.crypto import CryptoService
from imggen.domain.exceptions import (
    UserAlreadyExistsError,
    AuthenticationError,
    UserNotFoundError,
    SessionExpiredError,
)
from imggen.infrastructure.database.sqlite import SQLiteUserRepository
from imggen.infrastructure.session import SessionManager
from imggen.application.auth import (
    RegisterUseCase,
    LoginUseCase,
    LogoutUseCase,
    WhoAmIUseCase,
)

user_app = typer.Typer()
console = Console()


def get_dependencies():
    """Get shared dependencies."""
    settings.ensure_dirs()
    user_repo = SQLiteUserRepository(settings.db_path)
    crypto_service = CryptoService(
        time_cost=settings.argon2_time_cost,
        memory_cost=settings.argon2_memory_cost,
        parallelism=settings.argon2_parallelism,
    )
    session_manager = SessionManager(
        settings.session_dir,
        timeout=settings.session_timeout,
    )
    return user_repo, crypto_service, session_manager


@user_app.command("register")
def register():
    """Register a new user."""
    console.print("\n[bold cyan]Register New User[/bold cyan]\n")
    
    username = Prompt.ask("[bold]Username[/bold]")
    password = Prompt.ask("[bold]Password[/bold]", password=True)
    password_confirm = Prompt.ask("[bold]Confirm Password[/bold]", password=True)
    
    if password != password_confirm:
        console.print("[bold red]Error:[/bold red] Passwords do not match", style="red")
        raise typer.Exit(1)
    
    if len(password) < 8:
        console.print("[bold red]Error:[/bold red] Password must be at least 8 characters", style="red")
        raise typer.Exit(1)
    
    try:
        user_repo, crypto_service, _ = get_dependencies()
        use_case = RegisterUseCase(user_repo, crypto_service)
        
        with console.status("[bold green]Creating user..."):
            user = use_case.execute(username, password)
        
        console.print(f"\n[bold green]✓[/bold green] User '{user.username}' registered successfully!")
        console.print("\n[dim]You can now login with:[/dim]")
        console.print(f"  [bold]imggen user login[/bold]\n")
        
    except UserAlreadyExistsError as e:
        console.print(f"[bold red]Error:[/bold red] {e}", style="red")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}", style="red")
        raise typer.Exit(1)


@user_app.command("login")
def login():
    """Login and unlock vault."""
    console.print("\n[bold cyan]Login[/bold cyan]\n")
    
    username = Prompt.ask("[bold]Username[/bold]")
    password = Prompt.ask("[bold]Password[/bold]", password=True)
    
    try:
        user_repo, crypto_service, session_manager = get_dependencies()
        use_case = LoginUseCase(user_repo, crypto_service, session_manager)
        
        with console.status("[bold green]Authenticating..."):
            session = use_case.execute(username, password)
        
        console.print(f"\n[bold green]✓[/bold green] Logged in as '{session.username}'")
        console.print(f"[dim]Session expires: {session.expires_at.strftime('%Y-%m-%d %H:%M:%S')} UTC[/dim]\n")
        
    except (UserNotFoundError, AuthenticationError) as e:
        console.print(f"[bold red]Error:[/bold red] {e}", style="red")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}", style="red")
        raise typer.Exit(1)


@user_app.command("logout")
def logout():
    """Logout and lock vault."""
    try:
        _, _, session_manager = get_dependencies()
        use_case = LogoutUseCase(session_manager)
        use_case.execute()
        
        console.print("\n[bold green]✓[/bold green] Logged out successfully\n")
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}", style="red")
        raise typer.Exit(1)


@user_app.command("whoami")
def whoami():
    """Show current user."""
    try:
        _, _, session_manager = get_dependencies()
        use_case = WhoAmIUseCase(session_manager)
        session = use_case.execute()
        
        if not session:
            console.print("\n[yellow]Not logged in[/yellow]\n")
            console.print("[dim]Use 'imggen user login' to login[/dim]\n")
            raise typer.Exit(0)
        
        table = Table(title="Current Session", show_header=False, box=None)
        table.add_column("Field", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")
        
        table.add_row("Username", session.username)
        table.add_row("User ID", str(session.user_id))
        table.add_row("Logged in", session.created_at.strftime("%Y-%m-%d %H:%M:%S UTC"))
        table.add_row("Expires", session.expires_at.strftime("%Y-%m-%d %H:%M:%S UTC"))
        
        console.print()
        console.print(table)
        console.print()
        
    except SessionExpiredError as e:
        console.print(f"\n[yellow]{e}[/yellow]\n")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}", style="red")
        raise typer.Exit(1)

