# START HERE - ComfyUI Workflows para Interiores

## Inicio Rápido

### 1. Elige tu workflow

#### Principiante / Primera Vez
**Usa:** `interior_depth_only.json`
- Solo necesitas el depth map de Blender
- Más rápido de procesar
- Excelente para primeras pruebas

#### Avanzado / Máxima Calidad
**Usa:** `interior_multi_controlnet.json`
- Usa depth + normal + ambient occlusion
- Mejor preservación de detalles
- Resultados más fotorrealistas

### 2. Descarga los modelos necesarios

#### Para `interior_depth_only.json`:
```
ComfyUI/models/controlnet/diffusers_xl_depth_full.safetensors
```
[Descargar desde HuggingFace](https://huggingface.co/diffusers/controlnet-depth-sdxl-1.0)

#### Para `interior_multi_controlnet.json` (además del anterior):
```
ComfyUI/models/controlnet/sai_xl_normalbae.safetensors
ComfyUI/models/controlnet/t2i-adapter_xl_sketch.safetensors
```

### 3. Prepara tus renders de Blender

Ya tienes los scripts para generar escenas:

```bash
# Generar una escena aleatoria
blender --background --python generate_random_room.py

# Resultado:
# - random_room.blend (escena)
# - Renders automáticos con depth, normal, AO, etc.
```

### 4. Carga el workflow en ComfyUI

1. Abre ComfyUI: `http://localhost:8188`
2. Arrastra el archivo JSON al navegador
3. Ajusta las rutas de las imágenes en los nodos LoadImage
4. Click en "Queue Prompt"

## Archivos en esta carpeta

| Archivo | Propósito |
|---------|-----------|
| **interior_depth_only.json** | Workflow simple (solo depth) |
| **interior_multi_controlnet.json** | Workflow completo (depth+normal+AO) |
| **README.md** | Documentación completa y detallada |
| **WORKFLOW_JSON_GUIDE.md** | Aprende a crear/modificar workflows |
| **batch_process_example.py** | Script para procesar múltiples escenas |
| **example.json** | Workflow de ejemplo de tu ComfyUI |

## Flujo de trabajo completo

```
┌─────────────────────────────────────────────────────────────┐
│ 1. BLENDER                                                  │
│    generate_random_room.py → habitación vacía               │
│    ↓                                                        │
│    Renders: depth.png, normal.png, ao.png                   │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. COMFYUI                                                  │
│    Cargar workflow → Configurar → Queue Prompt              │
│    ↓                                                        │
│    Output: Habitación fotorrealista con muebles            │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. DATASET                                                  │
│    Imagen fotorrealista + metadata JSON (pose de cámara)    │
│    ↓                                                        │
│    Entrenar modelo de predicción de pose                    │
└─────────────────────────────────────────────────────────────┘
```

## Personalización rápida

### Cambiar tipo de habitación

En el nodo CLIPTextEncode (positive prompt), cambia:

```
"modern interior living room" → "modern interior bedroom"
"modern interior living room" → "modern interior kitchen"
"modern interior living room" → "modern interior bathroom"
```

### Ajustar influencia del depth map

En el nodo ControlNetApplyAdvanced:

```json
"widgets_values": [1.0, 0.0, 1.0]
                   ↑ Cambia esto
```

- `0.8` = Más libertad creativa, menos fiel a geometría
- `1.0` = Equilibrado (recomendado)
- `1.2` = Máxima fidelidad a geometría

### Cambiar modelo base

Los workflows usan **RealVisXL_V5.0.safetensors** por defecto.

En el nodo CheckpointLoaderSimple puedes cambiar a:
- `juggernautXL_v9Rdphoto2Lightning.safetensors`
- `DreamShaperXL.safetensors`
- Cualquier otro modelo SDXL que tengas

## Próximos pasos

1. Lee `README.md` para configuración detallada
2. Prueba `interior_depth_only.json` primero
3. Experimenta con diferentes prompts
4. Cuando funcione bien, prueba `interior_multi_controlnet.json`
5. Usa `batch_process_example.py` para procesar múltiples escenas
6. Lee `WORKFLOW_JSON_GUIDE.md` para crear tus propios workflows

## Problemas comunes

**"Cannot find model diffusers_xl_depth_full.safetensors"**
→ Descarga el modelo ControlNet y ponlo en `ComfyUI/models/controlnet/`

**"Image not found interior_00000_depth.png"**
→ Copia tus renders de Blender a `ComfyUI/input/`

**"La geometría no se respeta"**
→ Aumenta el strength del ControlNet de depth a 1.2 o 1.5

**"Generación muy lenta"**
→ Reduce steps de 25 a 15-20, o usa un sampler más rápido como `euler`

---

**¿Necesitas ayuda?** Lee `README.md` para documentación completa.
