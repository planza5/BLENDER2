# Sistema de Inferencia de Texturas Procedurales - Microcemento

Este sistema permite inferir los parámetros de un shader procedural de Blender a partir de una imagen de textura real.

## Flujo de trabajo

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  1. GENERAR     │     │  2. ENTRENAR    │     │  3. INFERIR     │
│    DATASET      │ --> │     MODELO      │ --> │   PARÁMETROS    │
│                 │     │                 │     │                 │
│  Blender +      │     │  PyTorch        │     │  Imagen real    │
│  parámetros     │     │  CNN            │     │  → parámetros   │
│  aleatorios     │     │                 │     │  → Blender      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Requisitos

### Para generación de dataset (Blender)
- Blender 3.x o 4.x

### Para entrenamiento (Python)
```bash
pip install torch torchvision pillow tqdm numpy
```

## Uso

### Paso 1: Generar dataset

Edita la configuración en `microcemento_dataset_generator.py`:
```python
CONFIG = {
    "output_dir": "/ruta/a/tu/dataset",
    "num_samples": 10000,      # Número de muestras
    "resolution": 512,         # Resolución de imágenes
    "samples_render": 64,      # Samples de Cycles
}
```

Ejecuta:
```bash
blender --background --python microcemento_dataset_generator.py
```

Esto genera:
- `/tu/dataset/images/` - 10,000 imágenes PNG
- `/tu/dataset/dataset.json` - Metadatos y parámetros

### Paso 2: Entrenar modelo

```bash
python train_microcemento.py \
    --dataset /ruta/a/tu/dataset \
    --epochs 100 \
    --batch_size 32 \
    --backbone efficientnet_b0 \
    --output ./checkpoints
```

Opciones:
- `--backbone`: `efficientnet_b0` (default) o `resnet34`
- `--lr`: Learning rate (default: 1e-4)
- `--device`: `cuda` o `cpu`

### Paso 3: Inferir y aplicar

Desde línea de comandos:
```bash
blender --background --python apply_inferred_params.py -- \
    --checkpoint ./checkpoints/best.pth \
    --dataset /ruta/a/tu/dataset \
    --image /foto/real/microcemento.jpg \
    --output resultado.blend
```

O desde el editor de Blender:
1. Abre `apply_inferred_params.py`
2. Edita las rutas en `PATHS`
3. Run Script

## Parámetros del shader

El sistema ajusta 14 parámetros:

| Parámetro | Descripción | Rango |
|-----------|-------------|-------|
| `noise_scale` | Escala del ruido base | 2.0 - 15.0 |
| `noise_detail` | Nivel de detalle | 2.0 - 8.0 |
| `noise_roughness` | Rugosidad del ruido | 0.3 - 0.7 |
| `wave_scale` | Escala marcas de llana | 1.0 - 5.0 |
| `wave_distortion` | Distorsión de marcas | 1.0 - 10.0 |
| `wave_detail` | Detalle de marcas | 0.0 - 4.0 |
| `wave_intensity` | Visibilidad de marcas | 0.1 - 0.5 |
| `voronoi_scale` | Escala manchas | 3.0 - 12.0 |
| `voronoi_intensity` | Visibilidad manchas | 0.05 - 0.25 |
| `color1_value` | Luminosidad tono oscuro | 0.55 - 0.75 |
| `color1_warmth` | Calidez tono oscuro | 0.0 - 0.08 |
| `color2_value` | Luminosidad tono claro | 0.80 - 0.95 |
| `color2_warmth` | Calidez tono claro | 0.0 - 0.08 |
| `ramp_midpoint` | Posición tono medio | 0.35 - 0.65 |

## Estructura del node tree

```
TexCoord → Mapping ─┬→ Noise ──────┐
                    │              ├→ Mix (Overlay) ─┐
                    ├→ Wave ───────┘                 │
                    │                                ├→ Mix (Soft Light) → ColorRamp → BSDF
                    └→ Voronoi ──────────────────────┘
```

## Tips

### Para mejorar resultados:

1. **Más muestras**: 10,000 es un mínimo, con 50,000+ obtendrás mejores resultados

2. **Data augmentation**: El script de entrenamiento ya incluye flips y rotaciones

3. **Domain gap**: Si la inferencia en fotos reales no funciona bien, prueba:
   - Añadir ruido/variaciones a las imágenes sintéticas durante la generación
   - Hacer fine-tuning con un pequeño dataset de pares reales etiquetados manualmente

4. **Expandir el shader**: Si necesitas más control, añade parámetros al diccionario `PARAMETERS` y actualiza las funciones `apply_parameters()`

## Troubleshooting

**El renderizado es muy lento**
- Reduce `samples_render` a 32
- Usa GPU: el script ya configura `scene.cycles.device = 'GPU'`

**Errores de memoria durante el entrenamiento**
- Reduce `batch_size`
- Usa `resnet34` en lugar de `efficientnet_b0`

**Los colores inferidos no coinciden**
- Ajusta los rangos de `color1_warmth` y `color2_warmth`
- Considera añadir más colores al ramp

## Extensiones posibles

- [ ] Añadir inferencia de roughness/normal maps
- [ ] Soporte para otros materiales (mármol, hormigón, etc.)
- [ ] GUI en Blender con panel de control
- [ ] Optimización con refinamiento iterativo (enfoque híbrido)
