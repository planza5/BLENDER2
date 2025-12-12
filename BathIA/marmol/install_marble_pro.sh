#!/bin/bash

echo "=== Instalación modelos PRO para ComfyUI (SDXL + IPAdapter + ControlNet Scribble) ==="

BASE="/workspace/runpod-slim/ComfyUI"

# Crear carpetas necesarias
mkdir -p $BASE/models/checkpoints
mkdir -p $BASE/models/vae
mkdir -p $BASE/models/ipadapter
mkdir -p $BASE/models/clip_vision
mkdir -p $BASE/models/controlnet

echo "Carpetas creadas."

# =============================
# 1. SDXL BASE + VAE
# =============================
echo "Descargando SDXL Base 1.0..."
wget -O $BASE/models/checkpoints/sd_xl_base_1.0.safetensors \
https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors

echo "Descargando VAE oficial SDXL..."
wget -O $BASE/models/vae/sdxl_vae.safetensors \
https://huggingface.co/stabilityai/sdxl-vae/resolve/main/sdxl_vae.safetensors

# =============================
# 2. CLIP VISION ViT-H
# =============================
echo "Descargando CLIP-ViT-H-14..."
wget -O $BASE/models/clip_vision/CLIP-ViT-H-14.safetensors \
https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl/CLIP-ViT-H-14.safetensors

# =============================
# 3. IPAdapter PLUS SDXL
# =============================
echo "Descargando IPAdapter Plus SDXL ViT-H..."
wget -O $BASE/models/ipadapter/ip-adapter-plus_sdxl_vit-h.safetensors \
https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl/ip-adapter-plus_sdxl_vit-h.safetensors

# =============================
# 4. ControlNet Scribble SDXL
# =============================
echo "Descargando ControlNet Scribble SDXL..."
wget -O $BASE/models/controlnet/controlnet-scribble-sdxl.safetensors \
https://huggingface.co/lllyasviel/sd_control_collection/resolve/main/controlnet-scribble-sdxl-1.0.safetensors

echo "=== Instalación finalizada ==="
echo "Los modelos ya están listos en ComfyUI."
