# ComfyUI Setup Guide

Complete guide to setting up ComfyUI for use with imggen.

## Quick Setup (Automated)

We provide an automated setup script that handles everything:

```bash
./setup_comfyui.sh
```

This will:
- Install ComfyUI in `../ComfyUI/` directory
- Download SDXL Base 1.0 model
- Configure and start ComfyUI
- Verify the setup

## Manual Setup

If you prefer to set up manually, follow these steps:

### 1. System Requirements

**Required:**
- Python 3.10 or 3.11
- NVIDIA GPU with 8GB+ VRAM (for SDXL)
- CUDA 11.8 or 12.1
- ~20GB free disk space

**Recommended:**
- 16GB+ system RAM
- Fast SSD storage

### 2. Install ComfyUI

#### Option A: Git Clone (Recommended)

```bash
# Clone ComfyUI
cd ..  # Go to parent directory
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI

# Install dependencies
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt
```

#### Option B: Portable Installation

Download the portable version from:
https://github.com/comfyanonymous/ComfyUI/releases

### 3. Download SDXL Model

The SDXL Base 1.0 model is required (~6.9GB).

#### Option A: Automatic Download

```bash
cd ComfyUI
python -c "
from huggingface_hub import hf_hub_download
import os

model_path = os.path.join('models', 'checkpoints')
os.makedirs(model_path, exist_ok=True)

print('Downloading SDXL Base 1.0...')
hf_hub_download(
    repo_id='stabilityai/stable-diffusion-xl-base-1.0',
    filename='sd_xl_base_1.0.safetensors',
    local_dir=model_path,
    local_dir_use_symlinks=False
)
print('Download complete!')
"
```

#### Option B: Manual Download

1. Visit: https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0
2. Download `sd_xl_base_1.0.safetensors` (6.9GB)
3. Place in: `ComfyUI/models/checkpoints/`

#### Option C: Use CivitAI

Download from CivitAI:
- https://civitai.com/models/101055/sd-xl

### 4. Start ComfyUI

```bash
cd ComfyUI
python main.py
```

**Or with custom settings:**

```bash
# With GPU memory optimization
python main.py --lowvram

# Specific port
python main.py --port 8188

# Listen on all interfaces
python main.py --listen 0.0.0.0
```

### 5. Verify Installation

Once ComfyUI is running:

1. **Open browser:** http://127.0.0.1:8188
2. **Check UI loads** - you should see the workflow editor
3. **Verify model:** Check that `sd_xl_base_1.0.safetensors` appears in the checkpoint dropdown

### 6. Test with imggen

```bash
cd ../diffuseai

# Check connection
curl http://127.0.0.1:8188/system_stats

# Generate test image
./dev.sh generate generate "a red apple on a table"
```

## Configuration

### Change ComfyUI URL

If running ComfyUI on a different port or host:

```bash
export IMGGEN_COMFYUI_URL=http://localhost:8188
./dev.sh config show
```

### ComfyUI Command Line Options

```bash
python main.py --help
```

Common options:
- `--port 8188` - Change port (default: 8188)
- `--listen 0.0.0.0` - Listen on all interfaces
- `--lowvram` - Enable for GPUs with <8GB VRAM
- `--normalvram` - Disable aggressive memory management
- `--cpu` - Run on CPU (very slow)
- `--disable-auto-launch` - Don't open browser automatically

### Performance Optimization

#### For 8GB VRAM GPUs:
```bash
python main.py --lowvram
```

#### For 6GB VRAM GPUs:
```bash
python main.py --lowvram --preview-method none
```

#### For 4GB VRAM GPUs (very slow):
```bash
python main.py --novram --cpu-vae
```

## Troubleshooting

### ComfyUI Won't Start

**Problem:** Import errors or missing dependencies

**Solution:**
```bash
cd ComfyUI
pip install -r requirements.txt --upgrade
```

### "CUDA out of memory"

**Problem:** Not enough GPU VRAM

**Solutions:**
1. Use `--lowvram` flag
2. Reduce image size to 768x768 or 512x512
3. Close other GPU applications
4. Use CPU mode (slow): `--cpu`

### Model Not Found

**Problem:** SDXL model not detected

**Solution:**
1. Verify file location: `ComfyUI/models/checkpoints/sd_xl_base_1.0.safetensors`
2. Check filename matches exactly
3. Restart ComfyUI

### Connection Refused

**Problem:** imggen can't connect to ComfyUI

**Solutions:**
1. Verify ComfyUI is running: `curl http://127.0.0.1:8188/system_stats`
2. Check port: `netstat -tuln | grep 8188`
3. Check firewall settings
4. Try: `export IMGGEN_COMFYUI_URL=http://127.0.0.1:8188`

### Slow Generation

**Problem:** Takes too long to generate images

**Solutions:**
1. Reduce steps: `./dev.sh generate generate "prompt" --steps 20`
2. Reduce size: `--size 768x768`
3. Enable GPU optimizations in ComfyUI
4. Check GPU drivers are updated

## Advanced Setup

### Run ComfyUI as a Service (Linux)

Create `/etc/systemd/system/comfyui.service`:

```ini
[Unit]
Description=ComfyUI Service
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/ComfyUI
ExecStart=/usr/bin/python3 main.py --listen 0.0.0.0
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable comfyui
sudo systemctl start comfyui
sudo systemctl status comfyui
```

### Docker Setup

```dockerfile
FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

RUN apt-get update && apt-get install -y \
    python3.10 python3-pip git

WORKDIR /app
RUN git clone https://github.com/comfyanonymous/ComfyUI.git
WORKDIR /app/ComfyUI

RUN pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu121
RUN pip install -r requirements.txt

EXPOSE 8188
CMD ["python3", "main.py", "--listen", "0.0.0.0"]
```

Build and run:
```bash
docker build -t comfyui .
docker run --gpus all -p 8188:8188 -v ./models:/app/ComfyUI/models comfyui
```

### Remote ComfyUI Setup

To use ComfyUI on a remote server:

1. **Server side:**
   ```bash
   python main.py --listen 0.0.0.0 --port 8188
   ```

2. **Client side (imggen):**
   ```bash
   export IMGGEN_COMFYUI_URL=http://remote-server-ip:8188
   ./dev.sh config show
   ```

3. **Security:** Consider using SSH tunnel:
   ```bash
   ssh -L 8188:localhost:8188 user@remote-server
   export IMGGEN_COMFYUI_URL=http://localhost:8188
   ```

## Additional Models

### SDXL Refiner (Optional)

For even better quality:

```bash
cd ComfyUI/models/checkpoints
wget https://huggingface.co/stabilityai/stable-diffusion-xl-refiner-1.0/resolve/main/sd_xl_refiner_1.0.safetensors
```

### VAE (Optional)

For better color accuracy:

```bash
cd ComfyUI/models/vae
wget https://huggingface.co/stabilityai/sdxl-vae/resolve/main/sdxl_vae.safetensors
```

## Performance Benchmarks

Typical generation times (1024x1024, 25 steps):

| GPU | VRAM | Time |
|-----|------|------|
| RTX 4090 | 24GB | ~5s |
| RTX 3090 | 24GB | ~8s |
| RTX 3080 | 10GB | ~12s |
| RTX 3060 Ti | 8GB | ~18s |
| RTX 2060 | 6GB | ~35s (lowvram) |

## Resources

- **ComfyUI GitHub:** https://github.com/comfyanonymous/ComfyUI
- **ComfyUI Wiki:** https://github.com/comfyanonymous/ComfyUI/wiki
- **SDXL Paper:** https://arxiv.org/abs/2307.01952
- **ComfyUI Community:** https://www.reddit.com/r/comfyui/

## Getting Help

If you encounter issues:

1. Check ComfyUI logs for errors
2. Verify GPU drivers are up to date
3. Check CUDA compatibility
4. Visit ComfyUI GitHub issues
5. Check imggen documentation

## Next Steps

Once ComfyUI is running:

1. Test the connection:
   ```bash
   curl http://127.0.0.1:8188/system_stats
   ```

2. Generate your first image:
   ```bash
   ./dev.sh generate generate "a beautiful sunset"
   ```

3. Explore advanced options:
   ```bash
   ./dev.sh generate generate --help
   ```

Happy generating! 🎨

