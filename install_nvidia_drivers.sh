#!/usr/bin/env bash
# Generic NVIDIA Driver Installation Script
# Supports any NVIDIA GPU with automatic detection
# Run with: sudo ./install_nvidia_drivers.sh

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[✓]${NC} $1"; }
error() { echo -e "${RED}[✗]${NC} $1"; exit 1; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                          ║${NC}"
echo -e "${BLUE}║        NVIDIA Driver Installation (Generic)              ║${NC}"
echo -e "${BLUE}║                                                          ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    error "Please run as root: sudo ./install_nvidia_drivers.sh"
fi

# Detect NVIDIA GPU
info "Detecting NVIDIA GPU..."
if ! lspci | grep -i nvidia > /dev/null; then
    error "No NVIDIA GPU detected!"
fi

GPU_INFO=$(lspci | grep -i 'vga.*nvidia' | head -1)
GPU_NAME=$(echo "$GPU_INFO" | cut -d: -f3 | xargs)

success "Detected GPU: $GPU_NAME"
echo ""

# Get recommended drivers
info "Checking available NVIDIA drivers..."
AVAILABLE_DRIVERS=$(ubuntu-drivers list 2>/dev/null | grep nvidia-driver || echo "")

if [ -z "$AVAILABLE_DRIVERS" ]; then
    warn "Could not auto-detect drivers. Showing common options."
    AVAILABLE_DRIVERS="nvidia-driver-535
nvidia-driver-550
nvidia-driver-565
nvidia-driver-570
nvidia-driver-580"
fi

echo ""
echo -e "${BLUE}Available NVIDIA drivers:${NC}"
echo "$AVAILABLE_DRIVERS" | nl
echo ""

# Get recommended driver
RECOMMENDED=$(ubuntu-drivers devices 2>/dev/null | grep recommended | awk '{print $3}' || echo "nvidia-driver-580")

echo -e "${GREEN}Recommended:${NC} $RECOMMENDED"
echo ""
echo "Driver versions explained:"
echo "  • 535 - LTS (Long Term Support) - Most stable"
echo "  • 550 - Production Branch - Stable"
echo "  • 565+ - New Feature Branch - Latest features"
echo "  • 570+ - Beta Branch - Cutting edge"
echo "  • 580+ - Latest - Newest (recommended for RTX 30/40 series)"
echo ""

# Prompt for driver choice
echo "Choose driver to install:"
echo "  1) $RECOMMENDED (recommended)"
echo "  2) nvidia-driver-535 (LTS, most stable)"
echo "  3) nvidia-driver-580 (latest)"
echo "  4) Custom version"
echo "  5) Auto-install (let Ubuntu choose)"
echo ""
read -p "Enter choice (1-5): " choice

case $choice in
    1)
        DRIVER="$RECOMMENDED"
        ;;
    2)
        DRIVER="nvidia-driver-535"
        ;;
    3)
        DRIVER="nvidia-driver-580"
        ;;
    4)
        read -p "Enter driver version (e.g., 580): " version
        DRIVER="nvidia-driver-$version"
        ;;
    5)
        info "Using ubuntu-drivers autoinstall..."
        apt update
        ubuntu-drivers autoinstall -y
        AUTO_INSTALL=true
        ;;
    *)
        error "Invalid choice"
        ;;
esac

if [ "${AUTO_INSTALL:-false}" = "false" ]; then
    info "Updating package list..."
    apt update

    echo ""
    info "Installing $DRIVER..."
    echo ""
    apt install -y "$DRIVER"
fi

# Detect VRAM (approximate based on GPU name)
detect_vram() {
    local gpu_lower=$(echo "$GPU_NAME" | tr '[:upper:]' '[:lower:]')
    
    if echo "$gpu_lower" | grep -qE "rtx 40[89]0|a100|h100"; then
        echo "24"
    elif echo "$gpu_lower" | grep -qE "rtx 4070|rtx 3090|a40"; then
        echo "12"
    elif echo "$gpu_lower" | grep -qE "rtx 4060|rtx 3080|rtx 3070|a10"; then
        echo "8"
    elif echo "$gpu_lower" | grep -qE "rtx 3060|rtx 4050|rtx 3050"; then
        echo "4"
    elif echo "$gpu_lower" | grep -qE "gtx 1660|gtx 1650|rtx 2060"; then
        echo "6"
    else
        echo "unknown"
    fi
}

VRAM=$(detect_vram)

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                          ║${NC}"
echo -e "${GREEN}║              ✅ Installation Complete!                   ║${NC}"
echo -e "${GREEN}║                                                          ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}GPU:${NC} $GPU_NAME"
[ "$VRAM" != "unknown" ] && echo -e "${BLUE}VRAM:${NC} ~${VRAM}GB"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo ""
echo "  1. Reboot your system:"
echo "     ${GREEN}sudo reboot${NC}"
echo ""
echo "  2. After reboot, verify the driver:"
echo "     ${GREEN}nvidia-smi${NC}"
echo ""
echo "  3. Run ComfyUI setup:"
echo "     ${GREEN}./setup_comfyui.sh${NC}"
echo ""
echo "  4. Generate images:"
echo "     ${GREEN}just gen \"your prompt\"${NC}"
echo ""

# VRAM-based recommendations
if [ "$VRAM" != "unknown" ]; then
    echo -e "${BLUE}💡 Recommended models for ~${VRAM}GB VRAM:${NC}"
    if [ "$VRAM" -ge 24 ]; then
        echo "   ✅✅✅ LARGE (SDXL): Best quality, very fast"
        echo "   ✅✅✅ MEDIUM: Very fast"
        echo "   ✅✅✅ SMALL: Lightning fast"
    elif [ "$VRAM" -ge 12 ]; then
        echo "   ✅✅✅ LARGE (SDXL): Best quality, fast"
        echo "   ✅✅✅ MEDIUM: Very fast"
        echo "   ✅✅✅ SMALL: Lightning fast"
    elif [ "$VRAM" -ge 8 ]; then
        echo "   ✅✅ LARGE (SDXL): Best quality (may need --lowvram)"
        echo "   ✅✅✅ MEDIUM: Fast, great balance ⭐ Recommended"
        echo "   ✅✅✅ SMALL: Very fast"
    elif [ "$VRAM" -ge 4 ]; then
        echo "   ✅ LARGE (SDXL): Possible with --lowvram (slower)"
        echo "   ✅✅✅ MEDIUM: Balanced, good quality ⭐ Recommended"
        echo "   ✅✅✅ SMALL: Very fast"
    else
        echo "   ⚠️  LARGE (SDXL): Not recommended"
        echo "   ✅✅ MEDIUM: Use with --lowvram"
        echo "   ✅✅✅ SMALL: Best choice ⭐ Recommended"
    fi
    echo ""
    echo "   Usage:"
    echo "     just gen-small \"prompt\"   # Fast (512x512)"
    echo "     just gen-medium \"prompt\"  # Balanced (768x768)"
    echo "     just gen-large \"prompt\"   # Best (1024x1024)"
fi

echo ""
echo -e "${YELLOW}Press Enter to reboot now, or Ctrl+C to reboot later...${NC}"
read -r

echo "Rebooting in 5 seconds... (Ctrl+C to cancel)"
sleep 5
reboot

