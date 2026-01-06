#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"
COMFYUI_DIR="$PARENT_DIR/ComfyUI"
MODEL_PATH="$COMFYUI_DIR/models/checkpoints"
MODEL_FILE="sd_xl_base_1.0.safetensors"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[✓]${NC} $1"; }
error() { echo -e "${RED}[✗]${NC} $1"; exit 1; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }

echo -e "\n${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                          ║${NC}"
echo -e "${BLUE}║           ComfyUI Setup for imggen                       ║${NC}"
echo -e "${BLUE}║                                                          ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}\n"

# Check Python
info "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    error "Python 3 is not installed. Please install Python 3.10 or 3.11"
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
info "Found Python $PYTHON_VERSION"
success "Python check passed"

# Check GPU
info "Checking for NVIDIA GPU..."
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader | while read line; do
        info "Found GPU: $line"
    done
    success "NVIDIA GPU detected"
else
    warn "nvidia-smi not found. GPU may not be available."
    warn "ComfyUI will run on CPU (very slow)"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check/Install ComfyUI
if [ -d "$COMFYUI_DIR" ]; then
    info "ComfyUI directory already exists at: $COMFYUI_DIR"
    read -p "Update existing installation? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        info "Updating ComfyUI..."
        cd "$COMFYUI_DIR"
        git pull
        success "ComfyUI updated"
    fi
else
    info "Cloning ComfyUI..."
    cd "$PARENT_DIR"
    git clone https://github.com/comfyanonymous/ComfyUI.git
    success "ComfyUI cloned to $COMFYUI_DIR"
fi

cd "$COMFYUI_DIR"

# Install dependencies
info "Installing ComfyUI dependencies..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    info "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

info "Installing PyTorch with CUDA support..."
pip install --upgrade pip
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu121

info "Installing ComfyUI requirements..."
pip install -r requirements.txt

success "Dependencies installed"

# Check for models
mkdir -p "$MODEL_PATH"

echo ""
info "imggen supports 3 model sizes:"
echo "  • SMALL (SD 1.5): 2GB VRAM, 512x512, fast (~4GB download)"
echo "  • MEDIUM (SD 2.1): 4GB VRAM, 768x768, balanced (~5GB download)"
echo "  • LARGE (SDXL): 8GB VRAM, 1024x1024, best quality (~7GB download)"
echo ""

if [ -f "$MODEL_PATH/$MODEL_FILE" ]; then
    success "SDXL (large) model already exists"
else
    info "SDXL Base 1.0 (large model) not found"
    echo ""
    echo "Which model(s) do you want to download?"
    echo ""
    echo "  1) LARGE only (SDXL - best quality, 6.9GB)"
    echo "  2) ALL models (SD 1.5 + SD 2.1 + SDXL, ~16GB)"
    echo "  3) Manual download instructions"
    echo "  4) Skip model download"
    echo ""
    read -p "Choose option (1-4): " -n 1 -r
    echo
    
    case $REPLY in
        1)
            info "Installing huggingface_hub..."
            pip install huggingface_hub
            
            info "Downloading SDXL Base 1.0 (~6.9GB)..."
            info "This may take 10-30 minutes depending on your connection..."
            
            python3 << EOF
from huggingface_hub import hf_hub_download
import os

try:
    print("Starting download...")
    hf_hub_download(
        repo_id='stabilityai/stable-diffusion-xl-base-1.0',
        filename='sd_xl_base_1.0.safetensors',
        local_dir='$MODEL_PATH',
        local_dir_use_symlinks=False
    )
    print("Download complete!")
except Exception as e:
    print(f"Error: {e}")
    print("\nYou can manually download from:")
    print("https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0")
    exit(1)
EOF
            
            if [ -f "$MODEL_PATH/$MODEL_FILE" ]; then
                success "SDXL (large) model downloaded successfully"
            else
                error "Model download failed"
            fi
            ;;
        2)
            info "Installing huggingface_hub..."
            pip install huggingface_hub
            
            info "Downloading all 3 models (~16GB total)..."
            info "This may take 30-60 minutes depending on your connection..."
            
            python3 << EOF
from huggingface_hub import hf_hub_download
import os

models = [
    ("runwayml/stable-diffusion-v1-5", "v1-5-pruned-emaonly.safetensors", "SD 1.5 (small)"),
    ("stabilityai/stable-diffusion-2-1", "v2-1_768-ema-pruned.safetensors", "SD 2.1 (medium)"),
    ("stabilityai/stable-diffusion-xl-base-1.0", "sd_xl_base_1.0.safetensors", "SDXL (large)"),
]

for repo_id, filename, name in models:
    try:
        print(f"\n Downloading {name}...")
        hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            local_dir='$MODEL_PATH',
            local_dir_use_symlinks=False
        )
        print(f"✓ {name} complete!")
    except Exception as e:
        print(f"✗ {name} failed: {e}")

print("\nAll downloads complete!")
EOF
            
            success "Models downloaded"
            ;;
        3)
            echo ""
            echo "Manual download instructions:"
            echo ""
            echo "SMALL (SD 1.5):"
            echo "  https://huggingface.co/runwayml/stable-diffusion-v1-5"
            echo "  File: v1-5-pruned-emaonly.safetensors (4GB)"
            echo ""
            echo "MEDIUM (SD 2.1):"
            echo "  https://huggingface.co/stabilityai/stable-diffusion-2-1"
            echo "  File: v2-1_768-ema-pruned.safetensors (5GB)"
            echo ""
            echo "LARGE (SDXL):"
            echo "  https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0"
            echo "  File: sd_xl_base_1.0.safetensors (6.9GB)"
            echo ""
            echo "Place all files in: $MODEL_PATH/"
            echo ""
            read -p "Press Enter when download is complete..."
            
            if [ -f "$MODEL_PATH/$MODEL_FILE" ]; then
                success "SDXL model found"
            else
                warn "Models not found. Download before generating images."
            fi
            ;;
        4)
            warn "Skipping model download"
            warn "Download models manually before generating images"
            ;;
        *)
            warn "Invalid option. Skipping model download."
            ;;
    esac
fi

# Create startup script
info "Creating startup script..."
cat > "$COMFYUI_DIR/start_comfyui.sh" << 'STARTSCRIPT'
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment
source venv/bin/activate

# Check GPU memory
if command -v nvidia-smi &> /dev/null; then
    VRAM=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -n1)
    
    if [ "$VRAM" -lt 8000 ]; then
        echo "Low VRAM detected ($VRAM MB). Starting with --lowvram flag..."
        python main.py --lowvram "$@"
    else
        echo "Starting ComfyUI..."
        python main.py "$@"
    fi
else
    echo "No GPU detected. Starting in CPU mode (slow)..."
    python main.py --cpu "$@"
fi
STARTSCRIPT

chmod +x "$COMFYUI_DIR/start_comfyui.sh"
success "Startup script created: $COMFYUI_DIR/start_comfyui.sh"

# Test startup
echo ""
info "Testing ComfyUI startup..."
read -p "Start ComfyUI now for testing? (Y/n) " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    info "Starting ComfyUI (press Ctrl+C to stop)..."
    info "Once ComfyUI starts, open: http://127.0.0.1:8188"
    echo ""
    
    "$COMFYUI_DIR/start_comfyui.sh"
else
    info "Skipping test startup"
fi

# Summary
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                          ║${NC}"
echo -e "${GREEN}║              Setup Complete! 🎉                          ║${NC}"
echo -e "${GREEN}║                                                          ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "ComfyUI Location: $COMFYUI_DIR"
echo ""
echo "To start ComfyUI:"
echo "  cd $COMFYUI_DIR"
echo "  ./start_comfyui.sh"
echo ""
echo "Or manually:"
echo "  cd $COMFYUI_DIR"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
echo "Then test with imggen:"
echo "  cd $SCRIPT_DIR"
echo ""
echo "  # List available models"
echo "  ./dev.sh generate models"
echo ""
echo "  # Generate with different sizes"
echo "  ./dev.sh generate generate \"sunset\" --model small   # Fast, 512px"
echo "  ./dev.sh generate generate \"sunset\" --model medium  # Balanced, 768px"
echo "  ./dev.sh generate generate \"sunset\" --model large   # Best, 1024px"
echo ""
echo "ComfyUI Web UI: http://127.0.0.1:8188"
echo ""
echo "Documentation:"
echo "  • ComfyUI Setup: docs/COMFYUI_SETUP.md"
echo "  • Model Guide: docs/MODELS.md"
echo ""

