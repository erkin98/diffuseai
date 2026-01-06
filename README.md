# imggen - Secure AI Image Generation Platform

A **world-class** AI image generation platform with end-to-end encryption, built with clean architecture principles.

## Features

- 🔒 **Zero-Knowledge Encryption**: All images, prompts, and metadata encrypted client-side with AES-256-GCM
- 🎨 **SDXL Generation**: High-quality image generation via ComfyUI
- 🏗️ **Clean Architecture**: Domain-driven design with pluggable infrastructure
- 🖥️ **Beautiful CLI**: Rich terminal interface with Typer
- 🔐 **Secure Sessions**: Argon2id password hashing, secure session management
- 📦 **Encrypted Vault**: All generated images stored encrypted locally

## Quick Start

### Prerequisites

- Python 3.11+
- ComfyUI running locally (default: `http://127.0.0.1:8188`)
- SDXL Base model installed in ComfyUI

**Don't have ComfyUI?** Run our automated setup:
```bash
./setup_comfyui.sh
```
Or see the [ComfyUI Setup Guide](docs/COMFYUI_SETUP.md) for manual installation.

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd diffuseai

# Run the dev script (auto-installs uv and dependencies)
./dev.sh --help

# Or use just recipes for easier commands
just setup
```

**Two ways to run commands:**
- **`dev.sh`** - Full-featured bash script (works everywhere)
- **`just`** - Recipe-based commands (requires `just` installed)

Install just: `cargo install just` or see [justfile guide](docs/JUSTFILE_GUIDE.md)

### Basic Usage

**With dev.sh:**
```bash
./dev.sh user register
./dev.sh user login
./dev.sh generate generate "a beautiful sunset"
./dev.sh gallery list
./dev.sh gallery export 1 output.png
```

**With just (easier!):**
```bash
just register
just login
just gen "a beautiful sunset"
just gallery
just export 1 output.png
```

See all recipes: `just --list` | [Justfile Guide](docs/JUSTFILE_GUIDE.md)

## Architecture

This platform follows **Clean Architecture** principles:

```
┌─────────────────────────────────────────┐
│         Interface Layer (CLI)           │
├─────────────────────────────────────────┤
│      Application Layer (Use Cases)      │
├─────────────────────────────────────────┤
│    Domain Layer (Business Logic)        │
├─────────────────────────────────────────┤
│   Infrastructure (DB, GPU, Storage)     │
└─────────────────────────────────────────┘
```

### Layers

1. **Domain Layer** (`src/imggen/domain/`)
   - Pure business logic with zero dependencies
   - Entities: User, Image, Vault
   - Crypto service with zero-knowledge encryption
   - Domain exceptions

2. **Application Layer** (`src/imggen/application/`)
   - Use cases: Register, Login, Generate, Gallery operations
   - Orchestrates domain objects and infrastructure
   - Interface-agnostic (works for CLI, API, SDK)

3. **Infrastructure Layer** (`src/imggen/infrastructure/`)
   - Database: SQLite (with Postgres support planned)
   - GPU Providers: ComfyUI (with cloud provider support planned)
   - Storage: Local filesystem (with S3/R2 support planned)
   - Session management

4. **Interface Layer** (`src/imggen/interfaces/`)
   - CLI: Typer-based terminal interface
   - Future: REST API, Web UI

## Security Architecture

### Zero-Knowledge Encryption

```
Password → Argon2id KDF → 
    ├─ Auth Hash (stored server-side)
    └─ Master Key (client-side only, never stored)

Master Key → HKDF → File Keys → AES-256-GCM → Encrypted Files
```

**Key Security Features:**

- **Two-step key derivation**: Separate auth hash and master key
- **Client-side encryption**: Master key never leaves your machine
- **Per-file keys**: Each file encrypted with unique derived key
- **Authenticated encryption**: AES-256-GCM with integrity verification
- **Memory-hard KDF**: Argon2id (t=3, m=64MB, p=4)
- **Secure sessions**: Auto-expiring with encrypted master key storage
- **Secure deletion**: File overwriting before removal

## CLI Commands

### User Management

```bash
./dev.sh user register          # Interactive registration
./dev.sh user login             # Login and unlock vault
./dev.sh user logout            # Lock vault
./dev.sh user whoami            # Show current user
```

### Image Generation

```bash
./dev.sh generate "prompt"                      # Basic generation
./dev.sh generate "prompt" -n "negative"        # With negative prompt
./dev.sh generate "prompt" --steps 30           # Custom steps
./dev.sh generate "prompt" --size 1024x1024     # Custom size
./dev.sh generate "prompt" --seed 42            # Reproducible
./dev.sh generate "prompt" --cfg 7.5            # Custom CFG scale
```

### Gallery Management

```bash
./dev.sh gallery list                    # List all images
./dev.sh gallery list --limit 10         # Paginated
./dev.sh gallery info <id>               # Show metadata
./dev.sh gallery export <id> out.png     # Decrypt and export
./dev.sh gallery delete <id>             # Secure delete
./dev.sh gallery search "keyword"        # Search by prompt
```

### Configuration

```bash
./dev.sh config show                     # Show current config
```

Use environment variables to configure:

```bash
export IMGGEN_COMFYUI_URL=http://localhost:8188
export IMGGEN_DEFAULT_STEPS=30
export IMGGEN_SESSION_TIMEOUT=7200
```

## Project Structure

```
diffuseai/
├── pyproject.toml              # Project config
├── dev.sh                      # Development script
├── README.md                   # This file
├── build.md                    # Architecture documentation
│
├── src/imggen/
│   ├── config.py               # Settings
│   ├── domain/                 # Core business logic
│   │   ├── entities.py
│   │   ├── value_objects.py
│   │   ├── crypto.py
│   │   └── exceptions.py
│   ├── application/            # Use cases
│   │   ├── auth.py
│   │   ├── generation.py
│   │   └── gallery.py
│   ├── infrastructure/         # External adapters
│   │   ├── database/
│   │   ├── gpu/
│   │   ├── storage/
│   │   └── session.py
│   └── interfaces/
│       └── cli/                # CLI interface
│
├── workflows/
│   └── sdxl_base.json          # SDXL workflow
│
└── data/                       # Runtime data (gitignored)
    ├── imggen.db
    ├── sessions/
    └── vaults/
```

## Development

### Running Tests

```bash
# Install dev dependencies
uv sync --all-extras

# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=imggen --cov-report=html
```

### Code Quality

```bash
# Format with ruff
uv run ruff format .

# Lint with ruff
uv run ruff check .

# Type check with mypy
uv run mypy src/imggen
```

## Configuration

All settings can be configured via environment variables with the `IMGGEN_` prefix:

| Variable | Default | Description |
|----------|---------|-------------|
| `IMGGEN_DATA_DIR` | `data` | Data directory |
| `IMGGEN_COMFYUI_URL` | `http://127.0.0.1:8188` | ComfyUI API URL |
| `IMGGEN_COMFYUI_TIMEOUT` | `300` | Request timeout (seconds) |
| `IMGGEN_SESSION_TIMEOUT` | `3600` | Session timeout (seconds) |
| `IMGGEN_DEFAULT_WIDTH` | `1024` | Default image width |
| `IMGGEN_DEFAULT_HEIGHT` | `1024` | Default image height |
| `IMGGEN_DEFAULT_STEPS` | `25` | Default sampling steps |
| `IMGGEN_DEFAULT_CFG` | `7.0` | Default CFG scale |

## Future Plans

### Online Mode (Architecture Ready)

- **Self-Hosted**: Docker Compose deployment with Postgres, Redis
- **SaaS**: Multi-tenant with zero-knowledge architecture
- **Hybrid GPU**: Local priority with cloud fallback (RunPod, Modal)
- **REST API**: FastAPI backend
- **Web UI**: React frontend
- **Billing**: Usage metering and payment integration

### Provider Support

- ✅ ComfyUI Local
- 🔄 RunPod (planned)
- 🔄 Modal (planned)
- 🔄 Replicate (planned)

### Storage Backends

- ✅ Local Filesystem
- 🔄 S3/R2 (planned)

## Security Checklist

- ✅ Argon2id for password hashing (memory-hard)
- ✅ AES-256-GCM for encryption (authenticated)
- ✅ Per-file random IVs/nonces
- ✅ Zero-knowledge architecture
- ✅ Secure memory handling
- ✅ No secrets in logs
- ✅ Session timeout
- ✅ Secure file deletion
- ⏳ Rate limiting (online mode)

## License

See [LICENSE](LICENSE) file.

## Contributing

This project follows clean architecture principles. When contributing:

1. Keep domain layer pure (no external dependencies)
2. Use dependency injection
3. Write tests for use cases
4. Follow the existing code structure

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

---

**Built with:** Python, Typer, Rich, Pydantic, SQLAlchemy, Cryptography, ComfyUI
