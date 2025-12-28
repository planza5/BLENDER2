# Descarga de Modelos Necesarios

## ✅ Modelo Base (Checkpoint SDXL)

### RealVisXL V5.0 (CONFIGURADO POR DEFECTO)

**Descarga:**
- [CivitAI - RealVisXL V5.0](https://civitai.com/models/139562/realvisxl-v50)
- Archivo: `RealVisXL_V5.0.safetensors` (~6.5 GB)

**Instalación:**
```
ComfyUI/models/checkpoints/RealVisXL_V5.0.safetensors
```

**Características:**
- Excelente fotorrealismo
- Muy bueno para arquitectura e interiores
- Colores naturales y realistas
- Funciona muy bien con ControlNet

---

## 📐 ControlNet Models (REQUERIDOS)

### Para `interior_depth_only.json`:

#### ControlNet Depth XL
**Descarga:**
- [HuggingFace - Diffusers ControlNet Depth SDXL](https://huggingface.co/diffusers/controlnet-depth-sdxl-1.0)
- Archivo: `diffusers_xl_depth_full.safetensors` (~2.5 GB)

**Instalación:**
```
ComfyUI/models/controlnet/diffusers_xl_depth_full.safetensors
```

**Descarga directa:**
```bash
# Usando wget o curl:
wget https://huggingface.co/diffusers/controlnet-depth-sdxl-1.0/resolve/main/diffusion_pytorch_model.safetensors -O diffusers_xl_depth_full.safetensors
```

---

### Para `interior_multi_controlnet.json` (además del anterior):

#### ControlNet Normal BAE XL
**Descarga:**
- [HuggingFace - Stability AI Control-LoRA Normal](https://huggingface.co/stabilityai/control-lora)
- Archivo: `sai_xl_normalbae.safetensors` (~2.5 GB)

**Instalación:**
```
ComfyUI/models/controlnet/sai_xl_normalbae.safetensors
```

#### T2I-Adapter Sketch XL
**Descarga:**
- [HuggingFace - T2I-Adapter Sketch SDXL](https://huggingface.co/TencentARC/t2i-adapter-sketch-sdxl-1.0)
- Archivo: `t2i-adapter_xl_sketch.safetensors` (~2.5 GB)

**Instalación:**
```
ComfyUI/models/controlnet/t2i-adapter_xl_sketch.safetensors
```

---

## 📁 Estructura de Directorios ComfyUI

```
ComfyUI/
├── models/
│   ├── checkpoints/
│   │   └── RealVisXL_V5.0.safetensors           ✅ Modelo base
│   ├── controlnet/
│   │   ├── diffusers_xl_depth_full.safetensors  ✅ Depth (obligatorio)
│   │   ├── sai_xl_normalbae.safetensors         ⚠️  Normal (opcional)
│   │   └── t2i-adapter_xl_sketch.safetensors    ⚠️  Sketch/AO (opcional)
│   └── vae/
│       └── (opcional, SDXL incluye VAE)
└── input/
    └── (tus depth maps de Blender)
```

---

## ⚡ Descarga Rápida (Script)

Crea un archivo `download_models.sh`:

```bash
#!/bin/bash

# Directorios
CHECKPOINT_DIR="ComfyUI/models/checkpoints"
CONTROLNET_DIR="ComfyUI/models/controlnet"

# Crear directorios si no existen
mkdir -p "$CHECKPOINT_DIR"
mkdir -p "$CONTROLNET_DIR"

echo "Descargando modelos..."

# ControlNet Depth (obligatorio)
echo "1/4 Descargando ControlNet Depth..."
wget https://huggingface.co/diffusers/controlnet-depth-sdxl-1.0/resolve/main/diffusion_pytorch_model.safetensors \
  -O "$CONTROLNET_DIR/diffusers_xl_depth_full.safetensors"

# ControlNet Normal (opcional)
echo "2/4 Descargando ControlNet Normal..."
wget https://huggingface.co/stabilityai/control-lora/resolve/main/control-lora-normal-rank256.safetensors \
  -O "$CONTROLNET_DIR/sai_xl_normalbae.safetensors"

# T2I Adapter Sketch (opcional)
echo "3/4 Descargando T2I-Adapter Sketch..."
wget https://huggingface.co/TencentARC/t2i-adapter-sketch-sdxl-1.0/resolve/main/diffusion_pytorch_model.safetensors \
  -O "$CONTROLNET_DIR/t2i-adapter_xl_sketch.safetensors"

echo "4/4 Checkpoint RealVisXL debe descargarse manualmente desde CivitAI"
echo "   https://civitai.com/models/139562/realvisxl-v50"

echo "✅ ControlNets descargados!"
echo "⚠️  Descarga manualmente RealVisXL_V5.0.safetensors y colócalo en $CHECKPOINT_DIR"
```

**Uso:**
```bash
chmod +x download_models.sh
./download_models.sh
```

---

## 🔍 Verificar Instalación

### En ComfyUI:

1. Inicia ComfyUI
2. En el nodo **CheckpointLoaderSimple**:
   - Click en el dropdown
   - Debes ver: `RealVisXL_V5.0.safetensors`

3. En el nodo **ControlNetLoader**:
   - Click en el dropdown
   - Debes ver:
     - `diffusers_xl_depth_full.safetensors`
     - `sai_xl_normalbae.safetensors` (si instalaste multi-controlnet)
     - `t2i-adapter_xl_sketch.safetensors` (si instalaste multi-controlnet)

Si no aparecen:
- Verifica las rutas de instalación
- Reinicia ComfyUI
- Revisa los logs de ComfyUI por errores

---

## 📊 Espacio en Disco Requerido

| Modelo | Tamaño | Obligatorio |
|--------|--------|-------------|
| RealVisXL_V5.0 | ~6.5 GB | ✅ Sí |
| diffusers_xl_depth_full | ~2.5 GB | ✅ Sí |
| sai_xl_normalbae | ~2.5 GB | ⚠️ Solo para multi-controlnet |
| t2i-adapter_xl_sketch | ~2.5 GB | ⚠️ Solo para multi-controlnet |
| **TOTAL (depth only)** | **~9 GB** | |
| **TOTAL (multi-controlnet)** | **~14 GB** | |

---

## 🆘 Problemas de Descarga

### CivitAI requiere login
Para descargar de CivitAI (RealVisXL):
1. Crea cuenta gratuita en https://civitai.com
2. Inicia sesión
3. Descarga el modelo

### HuggingFace lento
Si la descarga es muy lenta:
1. Usa un download manager (JDownloader, wget, curl)
2. Prueba en horarios de menos tráfico
3. Descarga desde mirrors alternativos

### Modelo alternativo sin registro
Si no quieres registrarte en CivitAI, usa el modelo base de Stability AI:
```
https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0
Archivo: sd_xl_base_1.0.safetensors
```

Funciona pero es menos fotorrealista que RealVisXL.

---

## ✅ Checklist Completo

- [ ] `RealVisXL_V5.0.safetensors` en `ComfyUI/models/checkpoints/`
- [ ] `diffusers_xl_depth_full.safetensors` en `ComfyUI/models/controlnet/`
- [ ] (Opcional) `sai_xl_normalbae.safetensors` en `ComfyUI/models/controlnet/`
- [ ] (Opcional) `t2i-adapter_xl_sketch.safetensors` en `ComfyUI/models/controlnet/`
- [ ] ComfyUI reiniciado después de instalar modelos
- [ ] Modelos visibles en los dropdowns de ComfyUI

**Una vez completado, estás listo para usar los workflows!**
