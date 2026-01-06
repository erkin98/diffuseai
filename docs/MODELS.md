# Model Sizes Guide

imggen supports multiple model sizes to accommodate different GPU capabilities and use cases.

## Available Models

### Small - Stable Diffusion 1.5

**Best for:** Quick iterations, low VRAM GPUs, fast generation

- **Checkpoint:** `v1-5-pruned-emaonly.safetensors`
- **Native Resolution:** 512x512
- **Recommended Steps:** 20
- **Minimum VRAM:** 2GB
- **Generation Time:** ~3-5 seconds (RTX 3060)
- **File Size:** ~4GB

**Characteristics:**
- Fast generation speed
- Lower quality compared to newer models
- Good for drafts and iterations
- Works on budget GPUs
- Can generate higher resolutions (slower)

**Download:**
```bash
cd ComfyUI/models/checkpoints
wget https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors
```

### Medium - Stable Diffusion 2.1

**Best for:** Balanced quality and speed, mid-range GPUs

- **Checkpoint:** `v2-1_768-ema-pruned.safetensors`
- **Native Resolution:** 768x768
- **Recommended Steps:** 25
- **Minimum VRAM:** 4GB
- **Generation Time:** ~6-10 seconds (RTX 3060)
- **File Size:** ~5GB

**Characteristics:**
- Better quality than SD 1.5
- Still relatively fast
- Good balance of speed/quality
- Works well on most modern GPUs

**Download:**
```bash
cd ComfyUI/models/checkpoints
wget https://huggingface.co/stabilityai/stable-diffusion-2-1/resolve/main/v2-1_768-ema-pruned.safetensors
```

### Large - SDXL Base 1.0 (Default)

**Best for:** Maximum quality, powerful GPUs

- **Checkpoint:** `sd_xl_base_1.0.safetensors`
- **Native Resolution:** 1024x1024
- **Recommended Steps:** 25
- **Minimum VRAM:** 8GB
- **Generation Time:** ~10-25 seconds (RTX 3060)
- **File Size:** ~6.9GB

**Characteristics:**
- Best quality and detail
- Slower generation
- Requires 8GB+ VRAM
- Industry standard for high-quality output
- Can use refiner for even better quality

**Download:**
```bash
cd ComfyUI/models/checkpoints
wget https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors
```

## Usage

### List Available Models

```bash
./dev.sh generate models
```

### Generate with Specific Model

```bash
# Small (fast, SD 1.5)
./dev.sh generate generate "your prompt" --model small

# Medium (balanced, SD 2.1)
./dev.sh generate generate "your prompt" --model medium

# Large (best quality, SDXL)
./dev.sh generate generate "your prompt" --model large
```

### Short Form

```bash
./dev.sh generate generate "prompt" -m small
./dev.sh generate generate "prompt" -m medium
./dev.sh generate generate "prompt" -m large
```

## Model Comparison

| Feature | Small (SD 1.5) | Medium (SD 2.1) | Large (SDXL) |
|---------|----------------|-----------------|--------------|
| Quality | ★★☆☆☆ | ★★★☆☆ | ★★★★★ |
| Speed | ★★★★★ | ★★★★☆ | ★★★☆☆ |
| VRAM | 2GB | 4GB | 8GB |
| Detail | Basic | Good | Excellent |
| Native Size | 512px | 768px | 1024px |
| Best For | Iterations | General use | Final renders |

## Choosing the Right Model

### Use SMALL when:
- ✅ You have a GPU with <4GB VRAM
- ✅ You need very fast iterations
- ✅ You're doing concept exploration
- ✅ Quality isn't critical
- ✅ You're testing prompts

### Use MEDIUM when:
- ✅ You have 4-6GB VRAM
- ✅ You want balanced speed/quality
- ✅ You need decent quality fast
- ✅ You're on a mid-range GPU
- ✅ You generate frequently

### Use LARGE when:
- ✅ You have 8GB+ VRAM
- ✅ You need maximum quality
- ✅ You're making final images
- ✅ Detail and realism matter
- ✅ You can wait 15-30 seconds

## Resolution Guidelines

### Small (SD 1.5)
- **Native:** 512x512 (fastest)
- **Max recommended:** 768x768
- **Good for:** 512x512, 512x768, 768x512

### Medium (SD 2.1)
- **Native:** 768x768 (fastest)
- **Max recommended:** 1024x768
- **Good for:** 768x768, 768x1024, 1024x768

### Large (SDXL)
- **Native:** 1024x1024 (optimal)
- **Max recommended:** 1536x1536
- **Good for:** 1024x1024, 1024x1536, 1536x1024

**Note:** Non-native resolutions may be slower and produce lower quality.

## Performance Tips

### For Small Model:
```bash
# Fast 512x512
./dev.sh generate generate "prompt" -m small --steps 15

# Higher quality 512x512
./dev.sh generate generate "prompt" -m small --steps 25
```

### For Medium Model:
```bash
# Balanced
./dev.sh generate generate "prompt" -m medium --size 768x768

# Portrait
./dev.sh generate generate "prompt" -m medium --size 768x1024
```

### For Large Model:
```bash
# Standard quality
./dev.sh generate generate "prompt" -m large --steps 25

# Maximum quality
./dev.sh generate generate "prompt" -m large --steps 40

# Square
./dev.sh generate generate "prompt" -m large --size 1024x1024

# Landscape
./dev.sh generate generate "prompt" -m large --size 1536x1024
```

## Automatic Model Selection

The CLI automatically uses the model's native resolution if you don't specify `--size`:

```bash
# Uses 512x512 automatically
./dev.sh generate generate "prompt" -m small

# Uses 768x768 automatically
./dev.sh generate generate "prompt" -m medium

# Uses 1024x1024 automatically
./dev.sh generate generate "prompt" -m large
```

## Setting Default Model

You can set a default model via environment variable:

```bash
export IMGGEN_DEFAULT_MODEL=medium
./dev.sh config show
```

## Download All Models

Script to download all three models:

```bash
#!/bin/bash
cd ComfyUI/models/checkpoints

# Small
echo "Downloading SD 1.5..."
wget https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors

# Medium
echo "Downloading SD 2.1..."
wget https://huggingface.co/stabilityai/stable-diffusion-2-1/resolve/main/v2-1_768-ema-pruned.safetensors

# Large
echo "Downloading SDXL..."
wget https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors

echo "All models downloaded!"
```

## Disk Space Requirements

- **Small only:** ~4GB
- **Medium only:** ~5GB
- **Large only:** ~7GB
- **All three:** ~16GB

## Troubleshooting

### Model Not Found

Make sure the checkpoint file is in `ComfyUI/models/checkpoints/`:

```bash
ls -lh ComfyUI/models/checkpoints/
```

### Out of Memory with Large Model

Try medium or small:
```bash
./dev.sh generate generate "prompt" -m medium
```

Or use lowvram mode:
```bash
cd ComfyUI && python main.py --lowvram
```

### Slow Generation

1. Use smaller model
2. Reduce steps: `--steps 20`
3. Use native resolution
4. Enable lowvram mode

## Examples

```bash
# Quick draft with small model
./dev.sh generate generate "red apple" -m small --steps 15

# Balanced quality portrait
./dev.sh generate generate "portrait of a wizard" -m medium --size 768x1024

# Maximum quality landscape
./dev.sh generate generate "epic fantasy landscape" -m large --steps 40 --size 1536x1024

# Fast iteration on small
for i in {1..10}; do
  ./dev.sh generate generate "test $i" -m small --seed $i
done

# Final render on large
./dev.sh generate generate "final masterpiece" -m large --steps 50
```

## Summary

- **Small**: Fast, 2GB VRAM, 512x512, SD 1.5
- **Medium**: Balanced, 4GB VRAM, 768x768, SD 2.1
- **Large**: Best, 8GB VRAM, 1024x1024, SDXL (default)

Choose based on your GPU and needs!

