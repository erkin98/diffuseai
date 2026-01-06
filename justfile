# imggen - Secure AI Image Generation Platform
# Run 'just' or 'just --list' to see all available recipes

# Default recipe (show help)
default:
    @just --list

# ============================================================================
# Setup & Installation
# ============================================================================

# Setup imggen (install dependencies, init database)
setup:
    @echo "🔧 Setting up imggen..."
    uv sync
    mkdir -p data/vaults data/sessions
    @if [ ! -f data/imggen.db ]; then \
        echo "📦 Initializing database..."; \
        uv run python -c "from imggen.infrastructure.database.sqlite import init_db; from pathlib import Path; init_db(Path('data/imggen.db'))"; \
    fi
    @echo "✅ imggen setup complete!"

# Setup ComfyUI (automated installation)
setup-comfyui:
    @echo "🎨 Setting up ComfyUI..."
    ./setup_comfyui.sh

# Setup everything (imggen + ComfyUI)
setup-all: setup setup-comfyui

# Install development dependencies
setup-dev:
    @echo "🔧 Installing dev dependencies..."
    uv sync --all-extras
    @echo "✅ Dev dependencies installed!"

# ============================================================================
# User Management
# ============================================================================

# Register a new user
register:
    @echo "👤 Register new user"
    uv run imggen user register

# Login to imggen
login:
    @echo "🔐 Login"
    uv run imggen user login

# Logout from imggen
logout:
    @echo "👋 Logout"
    uv run imggen user logout

# Show current user
whoami:
    uv run imggen user whoami

# ============================================================================
# Image Generation
# ============================================================================

# List available models
models:
    uv run imggen generate models

# Check if ComfyUI is running, start if not
_ensure-comfyui:
    #!/usr/bin/env bash
    if ! curl -s http://127.0.0.1:8188/system_stats > /dev/null 2>&1; then
        echo "🎨 ComfyUI not running, starting in background..."
        if [ -d "../ComfyUI" ]; then
            cd ../ComfyUI
            # Use the proper python from venv or system
            if [ -f "venv/bin/python" ]; then
                nohup venv/bin/python main.py --lowvram > comfyui.log 2>&1 &
            elif [ -f "venv/bin/python3" ]; then
                nohup venv/bin/python3 main.py --lowvram > comfyui.log 2>&1 &
            else
                # No venv, use system python
                nohup python3 main.py --lowvram > comfyui.log 2>&1 &
            fi
            echo "⏳ Waiting for ComfyUI to start (10 seconds)..."
            sleep 10
            if curl -s http://127.0.0.1:8188/system_stats > /dev/null 2>&1; then
                echo "✅ ComfyUI started successfully"
            else
                echo "❌ ComfyUI failed to start. Check ../ComfyUI/comfyui.log"
                echo "💡 You may need to run: ./setup_comfyui.sh first"
                exit 1
            fi
        else
            echo "❌ ComfyUI not found at ../ComfyUI"
            echo "💡 Run: ./setup_comfyui.sh to install ComfyUI"
            exit 1
        fi
    else
        echo "✅ ComfyUI is running"
    fi

# Check if user is logged in
_ensure-login:
    #!/usr/bin/env bash
    if ! uv run imggen user whoami > /dev/null 2>&1; then
        echo "🔐 Not logged in. Please login:"
        uv run imggen user login
    else
        echo "✅ Already logged in"
    fi

# Generate an image (usage: just gen "your prompt")
# Automatically starts ComfyUI and ensures login
gen PROMPT: _ensure-comfyui _ensure-login
    uv run imggen generate generate "{{PROMPT}}"

# Generate with small model (fast)
gen-small PROMPT: _ensure-comfyui _ensure-login
    uv run imggen generate generate "{{PROMPT}}" --model small

# Generate with medium model (balanced)
gen-medium PROMPT: _ensure-comfyui _ensure-login
    uv run imggen generate generate "{{PROMPT}}" --model medium

# Generate with large model (best quality)
gen-large PROMPT: _ensure-comfyui _ensure-login
    uv run imggen generate generate "{{PROMPT}}" --model large

# Generate with custom parameters
gen-custom PROMPT MODEL="large" SIZE="1024x1024" STEPS="25": _ensure-comfyui _ensure-login
    uv run imggen generate generate "{{PROMPT}}" --model {{MODEL}} --size {{SIZE}} --steps {{STEPS}}

# Generate with negative prompt
gen-neg PROMPT NEG_PROMPT: _ensure-comfyui _ensure-login
    uv run imggen generate generate "{{PROMPT}}" --negative "{{NEG_PROMPT}}"

# Generate with seed (reproducible)
gen-seed PROMPT SEED: _ensure-comfyui _ensure-login
    uv run imggen generate generate "{{PROMPT}}" --seed {{SEED}}

# Quick test generation
gen-test:
    uv run imggen generate generate "a red apple on a wooden table, photorealistic" --model small --steps 15

# Transform an image with img2img
img2img INPUT PROMPT STRENGTH="0.75":
    uv run imggen img2img transform "{{INPUT}}" "{{PROMPT}}" --strength {{STRENGTH}}

# Restyle a gallery image
restyle ID STYLE STRENGTH="0.75":
    uv run imggen img2img restyle {{ID}} "{{STYLE}}" --strength {{STRENGTH}}

# Restyle to Studio Ghibli
ghibli ID:
    uv run imggen img2img restyle {{ID}} "Studio Ghibli anime style, soft colors, whimsical, Miyazaki inspired, hand-drawn animation" --strength 0.7

# Restyle to cyberpunk
cyberpunk ID:
    uv run imggen img2img restyle {{ID}} "cyberpunk style, neon lights, futuristic, dark atmosphere, blade runner aesthetic" --strength 0.75

# Restyle to watercolor
watercolor ID:
    uv run imggen img2img restyle {{ID}} "watercolor painting style, soft edges, artistic, painted texture" --strength 0.6

# ============================================================================
# Gallery Management
# ============================================================================

# List all images
gallery:
    uv run imggen gallery list

# List images with limit
gallery-limit LIMIT="10":
    uv run imggen gallery list --limit {{LIMIT}}

# Show image info
info ID:
    uv run imggen gallery info {{ID}}

# Export image to file
export ID OUTPUT:
    uv run imggen gallery export {{ID}} {{OUTPUT}}

# Delete an image
delete ID:
    uv run imggen gallery delete {{ID}}

# Search images by keyword
search KEYWORD:
    uv run imggen gallery search "{{KEYWORD}}"

# ============================================================================
# ComfyUI Management
# ============================================================================

# Start ComfyUI
comfyui:
    @echo "🎨 Starting ComfyUI..."
    @cd ../ComfyUI && python main.py

# Start ComfyUI with low VRAM mode
comfyui-lowvram:
    @echo "🎨 Starting ComfyUI (low VRAM mode)..."
    @cd ../ComfyUI && python main.py --lowvram

# Start ComfyUI in background
comfyui-bg:
    @echo "🎨 Starting ComfyUI in background..."
    @cd ../ComfyUI && nohup python main.py > comfyui.log 2>&1 &
    @echo "✅ ComfyUI started. Check logs: tail -f ../ComfyUI/comfyui.log"

# Check ComfyUI status
comfyui-status:
    @curl -s http://127.0.0.1:8188/system_stats && echo "\n✅ ComfyUI is running" || echo "❌ ComfyUI is not running"

# Stop ComfyUI (if running in background)
comfyui-stop:
    @pkill -f "python main.py" && echo "✅ ComfyUI stopped" || echo "ℹ️  ComfyUI not running"

# ============================================================================
# Configuration
# ============================================================================

# Show current configuration
config:
    uv run imggen config show

# Set ComfyUI URL
config-url URL:
    @echo "Setting IMGGEN_COMFYUI_URL={{URL}}"
    @export IMGGEN_COMFYUI_URL={{URL}}

# ============================================================================
# Testing & Development
# ============================================================================

# Run all tests
test:
    uv run pytest

# Run tests with coverage
test-cov:
    uv run pytest --cov=imggen --cov-report=html
    @echo "📊 Coverage report: htmlcov/index.html"

# Run specific test file
test-file FILE:
    uv run pytest tests/{{FILE}}

# Run unit tests only
test-unit:
    uv run pytest tests/unit/ -v

# Run integration tests only
test-integration:
    uv run pytest tests/integration/ -v

# Format code with ruff
fmt:
    uv run ruff format .

# Lint code with ruff
lint:
    uv run ruff check .

# Type check with mypy
typecheck:
    uv run mypy src/imggen

# Run all checks (format, lint, typecheck, test)
check: fmt lint typecheck test

# ============================================================================
# Documentation
# ============================================================================

# Open README
readme:
    @${EDITOR:-nano} README.md

# Open quickstart guide
quickstart:
    @${EDITOR:-nano} QUICKSTART.md

# Open model guide
models-doc:
    @${EDITOR:-nano} docs/MODELS.md

# Open ComfyUI setup guide
comfyui-doc:
    @${EDITOR:-nano} docs/COMFYUI_SETUP.md

# ============================================================================
# Database & Cleanup
# ============================================================================

# Reset database (WARNING: deletes all data!)
db-reset:
    @echo "⚠️  This will delete all users and images!"
    @read -p "Are you sure? (yes/no): " confirm && [ "$$confirm" = "yes" ] || exit 1
    rm -f data/imggen.db
    @echo "♻️  Database reset. Run 'just setup' to reinitialize."

# Clean build artifacts
clean:
    rm -rf build/ dist/ *.egg-info .pytest_cache .mypy_cache .ruff_cache
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    @echo "✨ Cleaned build artifacts"

# Clean all (including data - WARNING!)
clean-all:
    @echo "⚠️  This will delete ALL data including images and database!"
    @read -p "Are you sure? (yes/no): " confirm && [ "$$confirm" = "yes" ] || exit 1
    rm -rf data/ .pytest_cache .mypy_cache .ruff_cache build/ dist/ *.egg-info
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    @echo "💥 Everything cleaned"

# ============================================================================
# Utilities
# ============================================================================

# Show project statistics
stats:
    @echo "📊 Project Statistics"
    @echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    @echo "Python files: $(find src -name '*.py' | wc -l)"
    @echo "Lines of code: $(find src -name '*.py' -exec wc -l {} + | tail -1 | awk '{print $1}')"
    @echo "Test files: $(find tests -name '*.py' | wc -l)"
    @echo "Documentation files: $(find . -maxdepth 2 -name '*.md' | wc -l)"
    @echo ""
    @echo "Database: $([ -f data/imggen.db ] && echo '✅ exists' || echo '❌ not found')"
    @echo "ComfyUI: $([ -d ../ComfyUI ] && echo '✅ installed' || echo '❌ not installed')"

# Check system requirements
check-system:
    @echo "🔍 System Requirements Check"
    @echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    @python3 --version || echo "❌ Python not found"
    @uv --version || echo "❌ uv not found"
    @command -v nvidia-smi >/dev/null && nvidia-smi --query-gpu=name,memory.total --format=csv,noheader || echo "ℹ️  No NVIDIA GPU detected"
    @echo ""
    @echo "Disk space:"
    @df -h . | tail -1 | awk '{print "  Available: " $4}'

# Create backup of vault and database
backup:
    @echo "💾 Creating backup..."
    @mkdir -p backups
    @tar -czf backups/imggen-backup-$(date +%Y%m%d-%H%M%S).tar.gz data/
    @echo "✅ Backup created in backups/"

# Update dependencies
update:
    @echo "⬆️  Updating dependencies..."
    uv sync --upgrade
    @echo "✅ Dependencies updated"

# ============================================================================
# Workflows (Common Task Combinations)
# ============================================================================

# Complete first-time setup
first-time: setup-all register login
    @echo "🎉 First-time setup complete!"
    @echo "Generate your first image with: just gen 'your prompt'"

# Daily workflow: login and start ComfyUI
start: login
    @echo "🚀 Starting ComfyUI in background..."
    @just comfyui-bg
    @sleep 3
    @just comfyui-status

# End session: stop ComfyUI and logout
stop: comfyui-stop logout

# Development workflow: format, lint, test
dev: fmt lint test

# Generate and export in one command
gen-export PROMPT OUTPUT:
    @echo "🎨 Generating and exporting..."
    @uv run imggen generate generate "{{PROMPT}}"
    @IMAGE_ID=$(uv run imggen gallery list --limit 1 | grep -oP '^\s*\K\d+' | head -1) && \
     uv run imggen gallery export $$IMAGE_ID {{OUTPUT}}
    @echo "✅ Saved to {{OUTPUT}}"

# Batch generate with different models
gen-compare PROMPT:
    @echo "📊 Comparing models for: {{PROMPT}}"
    @just gen-small "{{PROMPT}}"
    @just gen-medium "{{PROMPT}}"
    @just gen-large "{{PROMPT}}"
    @echo "✅ Generated with all 3 models. Check gallery!"

# Quick demo
demo:
    @echo "🎬 Running quick demo..."
    @just comfyui-status || (echo "❌ Start ComfyUI first: just comfyui" && exit 1)
    @just gen-test
    @just gallery

