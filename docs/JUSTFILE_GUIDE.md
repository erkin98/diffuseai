# Justfile Guide

The `justfile` provides convenient recipes for all common imggen tasks.

## Installation

### Install just

```bash
# Linux/macOS with cargo
cargo install just

# macOS with Homebrew
brew install just

# Or download from: https://github.com/casey/just
```

### Verify Installation

```bash
just --version
```

## Quick Start

```bash
# Show all available recipes
just

# Or
just --list

# Run a recipe
just setup
```

## Recipe Categories

### 🔧 Setup & Installation

```bash
just setup              # Setup imggen (dependencies, database)
just setup-comfyui      # Setup ComfyUI automatically
just setup-all          # Setup everything
just setup-dev          # Install dev dependencies
```

### 👤 User Management

```bash
just register           # Register new user
just login              # Login
just logout             # Logout
just whoami             # Show current user
```

### 🎨 Image Generation

```bash
# List models
just models

# Generate (basic)
just gen "a beautiful sunset"

# Model-specific shortcuts
just gen-small "fast draft"           # SD 1.5 (512px, fast)
just gen-medium "balanced quality"    # SD 2.1 (768px, balanced)
just gen-large "best quality"         # SDXL (1024px, slow)

# Advanced
just gen-custom "prompt" large 1024x1024 30
just gen-neg "cat" "ugly, deformed"
just gen-seed "landscape" 42

# Quick test
just gen-test
```

### 🖼️ Gallery Management

```bash
just gallery            # List all images
just gallery-limit 5    # List 5 images
just info 1             # Show image 1 info
just export 1 out.png   # Export image 1
just delete 1           # Delete image 1
just search "sunset"    # Search by keyword
```

### 🎨 ComfyUI Management

```bash
just comfyui            # Start ComfyUI
just comfyui-lowvram    # Start with low VRAM mode
just comfyui-bg         # Start in background
just comfyui-status     # Check if running
just comfyui-stop       # Stop ComfyUI
```

### ⚙️ Configuration

```bash
just config             # Show config
just config-url http://localhost:8188  # Set custom URL
```

### 🧪 Testing & Development

```bash
just test               # Run all tests
just test-cov           # Run with coverage
just test-unit          # Unit tests only
just test-integration   # Integration tests only

just fmt                # Format code
just lint               # Lint code
just typecheck          # Type check
just check              # All checks (fmt + lint + type + test)
```

### 📚 Documentation

```bash
just readme             # Open README
just quickstart         # Open quickstart guide
just models-doc         # Open models guide
just comfyui-doc        # Open ComfyUI setup guide
```

### 🧹 Database & Cleanup

```bash
just clean              # Clean build artifacts
just clean-all          # Clean everything (WARNING!)
just db-reset           # Reset database (WARNING!)
just backup             # Backup vault and database
```

### 🛠️ Utilities

```bash
just stats              # Show project statistics
just check-system       # Check system requirements
just update             # Update dependencies
```

### 🔄 Workflows (Combined Tasks)

```bash
# Complete first-time setup
just first-time         # setup-all + register + login

# Start your day
just start              # login + start ComfyUI in background

# End your session
just stop               # stop ComfyUI + logout

# Development workflow
just dev                # fmt + lint + test

# Generate and export in one go
just gen-export "prompt" output.png

# Compare all models
just gen-compare "dragon"

# Quick demo
just demo
```

## Common Workflows

### First Time Setup

```bash
# 1. Setup everything
just first-time

# 2. Generate first image
just gen "a beautiful sunset"

# 3. View gallery
just gallery
```

### Daily Usage

```bash
# Morning: Start everything
just start

# Generate images
just gen "your amazing prompt"
just gen-small "quick draft"
just gen-large "final masterpiece"

# View and export
just gallery
just export 1 output.png

# Evening: Stop everything
just stop
```

### Development Workflow

```bash
# Make changes to code

# Run checks
just dev

# Run specific tests
just test-unit

# Check coverage
just test-cov
```

### Model Comparison

```bash
# Generate same prompt with all models
just gen-compare "epic fantasy landscape"

# View results
just gallery

# Export all
just export 1 small.png
just export 2 medium.png
just export 3 large.png
```

## Recipe Arguments

Some recipes accept arguments:

```bash
# Positional arguments
just gen "your prompt here"
just export 1 output.png

# Named arguments (use = sign)
just gen-custom "prompt" MODEL=small SIZE=512x512 STEPS=20
```

## Advanced Usage

### Chaining Recipes

```bash
# Run multiple recipes in sequence
just setup && just login && just gen-test
```

### Custom Configuration

Edit the `justfile` to:
- Add your own recipes
- Modify default values
- Create project-specific workflows

### Environment Variables

Set environment variables before recipes:

```bash
IMGGEN_COMFYUI_URL=http://remote:8188 just gen "test"
```

## Tips & Tricks

### 1. Tab Completion

Enable shell completion for just:

```bash
# bash
source <(just --completions bash)

# zsh
source <(just --completions zsh)

# fish
just --completions fish | source
```

### 2. List Recipes with Descriptions

```bash
just --list
```

### 3. Show Recipe Details

```bash
just --show gen
```

### 4. Dry Run

See what a recipe would do without running:

```bash
just --dry-run gen "test"
```

### 5. Choose Recipe Interactively

```bash
just --choose
```

### 6. Default Recipe

Just run `just` to see all recipes:

```bash
just
```

## Comparison: just vs dev.sh

| Feature | justfile | dev.sh |
|---------|----------|--------|
| Syntax | Clean, declarative | Bash script |
| Discovery | `just --list` | Need to read script |
| Arguments | Built-in support | Manual parsing |
| Documentation | In recipes | Comments |
| Platform | Cross-platform | Bash-specific |
| Use case | Quick commands | Full setup |

**Recommendation:** Use both!
- `just` for daily commands
- `dev.sh` for full setup and complex workflows

## Examples

### Quick Image Generation Loop

```bash
# Generate 5 variations
for i in {1..5}; do
  just gen-seed "fantasy castle" $i
done

just gallery
```

### Development Loop

```bash
# Watch and test
while true; do
  just test-unit
  sleep 2
done
```

### Automated Workflow

```bash
#!/bin/bash
just setup
just login
just gen "landscape 1"
just gen "landscape 2"
just gallery
just export 1 landscape1.png
just export 2 landscape2.png
```

## Troubleshooting

### "command not found: just"

Install just first:
```bash
cargo install just
```

### Recipe Fails

Check individual commands:
```bash
just --dry-run recipe-name
```

### Custom Path

If imggen is not in PATH:
```bash
# Edit justfile, change 'uv run imggen' to full path
```

## Creating Custom Recipes

Add your own recipes to the justfile:

```python
# My custom recipe
my-recipe PARAM:
    @echo "Running my recipe with {{PARAM}}"
    uv run imggen generate generate "{{PARAM}}" --model small
    uv run imggen gallery list
```

## Summary

The justfile provides **80+ recipes** organized into 12 categories for:
- ✅ Quick command execution
- ✅ Easy discovery (`just --list`)
- ✅ Consistent interface
- ✅ Workflow automation
- ✅ Development tasks
- ✅ Daily operations

**Most used recipes:**
1. `just gen "prompt"` - Generate image
2. `just gallery` - View images
3. `just export ID file` - Export image
4. `just start` - Begin session
5. `just stop` - End session

Try it out:
```bash
just models
just gen-test
just gallery
```

Happy generating! 🎨

