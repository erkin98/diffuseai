#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# Install uv if missing
if ! command -v uv &> /dev/null; then
    info "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
    success "uv installed"
fi

# Sync dependencies
info "Syncing dependencies..."
uv sync
success "Dependencies synced"

# Initialize data directories
mkdir -p data/vaults data/sessions
success "Data directories ready"

# Initialize database if needed
if [[ ! -f data/imggen.db ]]; then
    info "Initializing database..."
    uv run python -c "from imggen.infrastructure.database.sqlite import init_db; from pathlib import Path; init_db(Path('data/imggen.db'))"
    success "Database initialized"
fi

# Run CLI
if [[ $# -eq 0 ]]; then
    info "Usage: ./dev.sh <command>"
    info "Run './dev.sh --help' for available commands"
    uv run imggen --help
else
    uv run imggen "$@"
fi

