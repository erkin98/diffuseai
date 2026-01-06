# ComfyUI Quick Reference

One-page reference for ComfyUI setup and usage with imggen.

## 🚀 Quick Setup

```bash
# Automated setup (recommended)
./setup_comfyui.sh

# Manual setup
cd ..
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt

# Download SDXL model to models/checkpoints/
# https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0
```

## ▶️ Start ComfyUI

```bash
# Standard start
cd ComfyUI
python main.py

# Low VRAM (8GB or less)
python main.py --lowvram

# Very low VRAM (6GB or less)
python main.py --lowvram --preview-method none

# CPU mode (slow)
python main.py --cpu

# Custom port
python main.py --port 8188

# Remote access
python main.py --listen 0.0.0.0
```

## 🔗 Connect to imggen

```bash
# Test connection
curl http://127.0.0.1:8188/system_stats

# Set custom URL
export IMGGEN_COMFYUI_URL=http://localhost:8188

# Generate test image
./dev.sh generate generate "test image"
```

## 📁 Directory Structure

```
ComfyUI/
├── main.py              # Main server
├── models/
│   ├── checkpoints/     # SDXL models go here
│   ├── vae/            # VAE models (optional)
│   ├── loras/          # LoRA models (optional)
│   └── embeddings/     # Embeddings (optional)
├── output/             # Generated images
└── input/              # Input images
```

## 📦 Required Files

**Minimum (required):**
- `models/checkpoints/sd_xl_base_1.0.safetensors` (6.9GB)

**Optional (better quality):**
- `models/checkpoints/sd_xl_refiner_1.0.safetensors` (6.1GB)
- `models/vae/sdxl_vae.safetensors` (335MB)

## 🔧 Common Issues

| Problem | Solution |
|---------|----------|
| CUDA out of memory | Use `--lowvram` flag |
| Model not found | Check `models/checkpoints/` directory |
| Connection refused | Verify ComfyUI is running on port 8188 |
| Slow generation | Reduce steps or size in imggen |
| Import errors | Run `pip install -r requirements.txt` |

## 🎨 imggen Commands

```bash
# Basic generation
./dev.sh generate generate "your prompt"

# Custom settings
./dev.sh generate generate "prompt" \
  --steps 30 \
  --size 1024x768 \
  --cfg 7.5 \
  --seed 42 \
  -n "negative prompt"
```

## 📊 Performance Tips

**8GB VRAM:**
- Use `--lowvram`
- Keep resolution at 1024x1024
- Use 20-30 steps

**6GB VRAM:**
- Use `--lowvram --preview-method none`
- Reduce resolution to 768x768
- Use 15-25 steps

**4GB VRAM:**
- Use `--novram --cpu-vae`
- Resolution 512x512
- Use 10-20 steps

## 🌐 Web UI

Once running, access ComfyUI at:
- Local: http://127.0.0.1:8188
- Remote: http://your-ip:8188 (with `--listen 0.0.0.0`)

## 📝 Environment Variables

```bash
# Set custom ComfyUI URL
export IMGGEN_COMFYUI_URL=http://localhost:8188

# Set custom timeout
export IMGGEN_COMFYUI_TIMEOUT=600

# Show current config
./dev.sh config show
```

## 🔄 Update ComfyUI

```bash
cd ComfyUI
git pull
pip install -r requirements.txt --upgrade
```

## 🐛 Debug Mode

```bash
# Start with verbose logging
cd ComfyUI
python main.py --verbose

# Check logs
tail -f comfyui.log
```

## 🔗 Useful Links

- ComfyUI: https://github.com/comfyanonymous/ComfyUI
- SDXL: https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0
- Full guide: [COMFYUI_SETUP.md](COMFYUI_SETUP.md)

## ⚡ Quick Test

```bash
# 1. Start ComfyUI
cd ComfyUI && python main.py

# 2. In another terminal, test imggen
cd diffuseai
./dev.sh user login
./dev.sh generate generate "a red apple"
./dev.sh gallery list
```

## 📞 Get Help

- **ComfyUI not starting:** Check Python version (3.10-3.11)
- **Model errors:** Verify file in `models/checkpoints/`
- **Connection errors:** Check port 8188 is not in use
- **GPU errors:** Update NVIDIA drivers

For detailed troubleshooting, see [COMFYUI_SETUP.md](COMFYUI_SETUP.md)

