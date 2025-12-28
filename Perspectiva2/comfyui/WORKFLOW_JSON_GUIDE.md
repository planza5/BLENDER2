# Guía: Estructura JSON de Workflows en ComfyUI

Esta guía te enseña cómo están estructurados los workflows JSON de ComfyUI para que puedas crear o modificar los tuyos propios.

## Estructura General

Un workflow JSON de ComfyUI tiene esta estructura de alto nivel:

```json
{
  "id": "unique-workflow-id",
  "revision": 0,
  "last_node_id": 10,
  "last_link_id": 15,
  "nodes": [...],
  "links": [...],
  "groups": [],
  "config": {},
  "extra": {...},
  "version": 0.4
}
```

### Campos principales:

- **id**: Identificador único del workflow (**DEBE ser un UUID válido**, ej: "a1b2c3d4-e5f6-47a8-b9c0-d1e2f3a4b5c6")
- **revision**: Versión/revisión del workflow
- **last_node_id**: ID del último nodo (para asignar nuevos IDs)
- **last_link_id**: ID del último link (para asignar nuevos IDs)
- **nodes**: Array de nodos (los componentes del workflow)
- **links**: Array de conexiones entre nodos
- **groups**: Agrupaciones visuales (opcional)
- **config**: Configuración adicional
- **extra**: Metadata de la UI (zoom, posición, versión)
- **version**: Versión del formato JSON (0.4 en tu caso)

---

## Estructura de un Nodo

Cada nodo en el array `nodes` tiene esta estructura:

```json
{
  "id": 1,
  "type": "CheckpointLoaderSimple",
  "pos": [50, 50],
  "size": [378, 159.59375],
  "flags": {},
  "order": 0,
  "mode": 0,
  "inputs": [...],
  "outputs": [...],
  "properties": {...},
  "widgets_values": [...]
}
```

### Campos del nodo:

#### 1. **id** (número)
Identificador único del nodo. Debe ser único en todo el workflow.

```json
"id": 1
```

#### 2. **type** (string)
Tipo de nodo. Define qué operación realiza.

Tipos comunes:
- `CheckpointLoaderSimple` - Cargar modelo base (SDXL, SD1.5, etc)
- `LoadImage` - Cargar imagen desde archivo
- `ControlNetLoader` - Cargar modelo ControlNet
- `ControlNetApplyAdvanced` - Aplicar ControlNet con parámetros avanzados
- `CLIPTextEncode` - Codificar prompt de texto
- `KSampler` - Generar imagen con diffusion
- `VAEDecode` - Decodificar latent a imagen
- `SaveImage` - Guardar imagen generada
- `EmptyLatentImage` - Crear latent vacío

```json
"type": "CheckpointLoaderSimple"
```

#### 3. **pos** (array [x, y])
Posición del nodo en el canvas de ComfyUI (solo para UI).

```json
"pos": [50, 50]
```

#### 4. **size** (array [width, height])
Tamaño del nodo en el canvas (solo para UI).

```json
"size": [378, 159.59375]
```

#### 5. **flags** (object)
Flags especiales del nodo (generalmente vacío).

```json
"flags": {}
```

#### 6. **order** (número)
Orden de ejecución del nodo (0 = primero).

```json
"order": 0
```

#### 7. **mode** (número)
Modo del nodo:
- `0` = Activo (normal)
- `2` = Muted (desactivado)
- `4` = Bypass (saltado)

```json
"mode": 0
```

#### 8. **inputs** (array)
Inputs del nodo (conexiones de entrada).

Cada input tiene:
- `name`: Nombre del input
- `type`: Tipo de dato (`MODEL`, `CLIP`, `IMAGE`, `LATENT`, `CONDITIONING`, etc)
- `link`: ID del link que se conecta (o `null` si no hay conexión)

```json
"inputs": [
  {
    "name": "clip",
    "type": "CLIP",
    "link": 5
  }
]
```

#### 9. **outputs** (array)
Outputs del nodo (conexiones de salida).

Cada output tiene:
- `name`: Nombre del output
- `type`: Tipo de dato
- `slot_index`: Índice del slot (generalmente 0)
- `links`: Array de IDs de links conectados (puede ser `null` o `[]` si no hay conexiones)

```json
"outputs": [
  {
    "name": "CONDITIONING",
    "type": "CONDITIONING",
    "slot_index": 0,
    "links": [6]
  }
]
```

#### 10. **properties** (object)
Propiedades del nodo (metadatos).

```json
"properties": {
  "cnr_id": "comfy-core",
  "ver": "0.4.0",
  "Node name for S&R": "CheckpointLoaderSimple"
}
```

#### 11. **widgets_values** (array)
**¡MUY IMPORTANTE!** Valores de los widgets (parámetros configurables del nodo).

El orden y cantidad de valores depende del tipo de nodo:

**CheckpointLoaderSimple:**
```json
"widgets_values": ["juggernautXL_v9Rdphoto2Lightning.safetensors"]
// [0] = nombre del checkpoint
```

**LoadImage:**
```json
"widgets_values": ["interior_00000_depth.png", "image"]
// [0] = nombre del archivo
// [1] = modo ("image" o "mask")
```

**CLIPTextEncode:**
```json
"widgets_values": ["beautiful scenery, photorealistic, 8k"]
// [0] = texto del prompt
```

**KSampler:**
```json
"widgets_values": [123456, "randomize", 20, 7.0, "dpmpp_2m", "karras", 1.0]
// [0] = seed (número)
// [1] = control de seed ("randomize", "fixed", "increment")
// [2] = steps (número de pasos)
// [3] = cfg (CFG scale)
// [4] = sampler_name (nombre del sampler)
// [5] = scheduler (nombre del scheduler)
// [6] = denoise (0.0 a 1.0)
```

**ControlNetApplyAdvanced:**
```json
"widgets_values": [1.0, 0.0, 1.0]
// [0] = strength (fuerza del ControlNet, 0.0 a 2.0)
// [1] = start_percent (cuándo empieza a aplicarse, 0.0 a 1.0)
// [2] = end_percent (cuándo termina de aplicarse, 0.0 a 1.0)
```

**EmptyLatentImage:**
```json
"widgets_values": [1024, 1024, 1]
// [0] = width (ancho en píxeles)
// [1] = height (alto en píxeles)
// [2] = batch_size (número de imágenes a generar)
```

**SaveImage:**
```json
"widgets_values": ["ComfyUI"]
// [0] = filename_prefix (prefijo del archivo de salida)
```

---

## Estructura de un Link

Los links conectan outputs de un nodo con inputs de otro nodo.

Cada link es un array con 6 elementos:

```json
[link_id, source_node_id, source_output_index, target_node_id, target_input_index, data_type]
```

### Ejemplo:

```json
[1, 4, 0, 3, 0, "MODEL"]
```

Esto significa:
- **Link ID:** 1
- **Source node ID:** 4 (nodo que provee el dato)
- **Source output index:** 0 (primer output del nodo fuente)
- **Target node ID:** 3 (nodo que recibe el dato)
- **Target input index:** 0 (primer input del nodo destino)
- **Data type:** "MODEL" (tipo de dato que se transfiere)

### Tipos de datos comunes:

- `MODEL` - Modelo de diffusion (UNet)
- `CLIP` - Modelo de encoding de texto
- `VAE` - Autoencoder variacional
- `IMAGE` - Imagen (tensor)
- `LATENT` - Representación latent (tensor comprimido)
- `CONDITIONING` - Conditioning vector (prompt codificado)
- `CONTROL_NET` - Modelo ControlNet
- `MASK` - Máscara (para inpainting)

---

## Ejemplo Completo: Workflow Simple

Aquí hay un workflow simple que genera una imagen desde un prompt:

```json
{
  "id": "c3d4e5f6-a7b8-49c0-d1e2-f3a4b5c6d7e8",
  "revision": 0,
  "last_node_id": 5,
  "last_link_id": 6,
  "nodes": [
    {
      "id": 1,
      "type": "CheckpointLoaderSimple",
      "pos": [0, 0],
      "size": [378, 159.59375],
      "flags": {},
      "order": 0,
      "mode": 0,
      "inputs": [],
      "outputs": [
        {"name": "MODEL", "type": "MODEL", "slot_index": 0, "links": [1]},
        {"name": "CLIP", "type": "CLIP", "slot_index": 1, "links": [2]},
        {"name": "VAE", "type": "VAE", "slot_index": 2, "links": [3]}
      ],
      "properties": {
        "cnr_id": "comfy-core",
        "ver": "0.4.0",
        "Node name for S&R": "CheckpointLoaderSimple"
      },
      "widgets_values": ["juggernautXL_v9Rdphoto2Lightning.safetensors"]
    },
    {
      "id": 2,
      "type": "CLIPTextEncode",
      "pos": [400, 0],
      "size": [510, 246.703125],
      "flags": {},
      "order": 1,
      "mode": 0,
      "inputs": [
        {"name": "clip", "type": "CLIP", "link": 2}
      ],
      "outputs": [
        {"name": "CONDITIONING", "type": "CONDITIONING", "slot_index": 0, "links": [4]}
      ],
      "properties": {
        "cnr_id": "comfy-core",
        "ver": "0.4.0",
        "Node name for S&R": "CLIPTextEncode"
      },
      "widgets_values": ["beautiful landscape, photorealistic, 8k"]
    },
    {
      "id": 3,
      "type": "EmptyLatentImage",
      "pos": [400, 300],
      "size": [378, 179.59375],
      "flags": {},
      "order": 2,
      "mode": 0,
      "inputs": [],
      "outputs": [
        {"name": "LATENT", "type": "LATENT", "slot_index": 0, "links": [5]}
      ],
      "properties": {
        "cnr_id": "comfy-core",
        "ver": "0.4.0",
        "Node name for S&R": "EmptyLatentImage"
      },
      "widgets_values": [1024, 1024, 1]
    },
    {
      "id": 4,
      "type": "KSampler",
      "pos": [950, 0],
      "size": [378, 353.59375],
      "flags": {},
      "order": 3,
      "mode": 0,
      "inputs": [
        {"name": "model", "type": "MODEL", "link": 1},
        {"name": "positive", "type": "CONDITIONING", "link": 4},
        {"name": "latent_image", "type": "LATENT", "link": 5}
      ],
      "outputs": [
        {"name": "LATENT", "type": "LATENT", "slot_index": 0, "links": [6]}
      ],
      "properties": {
        "cnr_id": "comfy-core",
        "ver": "0.4.0",
        "Node name for S&R": "KSampler"
      },
      "widgets_values": [123456, "randomize", 20, 7.0, "dpmpp_2m", "karras", 1.0]
    },
    {
      "id": 5,
      "type": "VAEDecode",
      "pos": [1400, 0],
      "size": [252, 101.59375],
      "flags": {},
      "order": 4,
      "mode": 0,
      "inputs": [
        {"name": "samples", "type": "LATENT", "link": 6},
        {"name": "vae", "type": "VAE", "link": 3}
      ],
      "outputs": [
        {"name": "IMAGE", "type": "IMAGE", "slot_index": 0, "links": null}
      ],
      "properties": {
        "cnr_id": "comfy-core",
        "ver": "0.4.0",
        "Node name for S&R": "VAEDecode"
      },
      "widgets_values": []
    }
  ],
  "links": [
    [1, 1, 0, 4, 0, "MODEL"],
    [2, 1, 1, 2, 0, "CLIP"],
    [3, 1, 2, 5, 1, "VAE"],
    [4, 2, 0, 4, 1, "CONDITIONING"],
    [5, 3, 0, 4, 2, "LATENT"],
    [6, 4, 0, 5, 0, "LATENT"]
  ],
  "groups": [],
  "config": {},
  "extra": {
    "ds": {"scale": 1.0, "offset": [0, 0]},
    "workflowRendererVersion": "Vue",
    "frontendVersion": "1.34.8"
  },
  "version": 0.4
}
```

### Flujo de datos:

```
CheckpointLoader (1)
  ├─ MODEL → KSampler (4)
  ├─ CLIP → CLIPTextEncode (2) → CONDITIONING → KSampler (4)
  └─ VAE → VAEDecode (5)

EmptyLatentImage (3) → LATENT → KSampler (4)

KSampler (4) → LATENT → VAEDecode (5) → IMAGE
```

---

## Cómo Crear un Workflow desde Cero

### Paso 1: Definir la estructura base

**IMPORTANTE:** El campo `id` debe ser un UUID válido. Puedes generarlo con:

```python
import uuid
print(str(uuid.uuid4()))  # Ejemplo: "a1b2c3d4-e5f6-47a8-b9c0-d1e2f3a4b5c6"
```

O usando herramientas online como https://www.uuidgenerator.net/

```json
{
  "id": "a1b2c3d4-e5f6-47a8-b9c0-d1e2f3a4b5c6",
  "revision": 0,
  "last_node_id": 0,
  "last_link_id": 0,
  "nodes": [],
  "links": [],
  "groups": [],
  "config": {},
  "extra": {
    "ds": {"scale": 1.0, "offset": [0, 0]},
    "workflowRendererVersion": "Vue",
    "frontendVersion": "1.34.8"
  },
  "version": 0.4
}
```

### Paso 2: Añadir nodos

Añade nodos al array `nodes`, asignando IDs incrementales:

```json
"nodes": [
  {
    "id": 1,
    "type": "CheckpointLoaderSimple",
    ...
  },
  {
    "id": 2,
    "type": "LoadImage",
    ...
  }
]
```

### Paso 3: Definir inputs y outputs

Para cada nodo, especifica qué inputs y outputs tiene:

```json
"inputs": [
  {"name": "clip", "type": "CLIP", "link": null}
],
"outputs": [
  {"name": "CONDITIONING", "type": "CONDITIONING", "slot_index": 0, "links": []}
]
```

### Paso 4: Crear links

Conecta nodos añadiendo links al array `links`:

```json
"links": [
  [1, source_node_id, source_output_idx, target_node_id, target_input_idx, "TYPE"]
]
```

### Paso 5: Actualizar referencias

- En el output del nodo fuente, añade el link ID a `links`
- En el input del nodo destino, asigna el link ID a `link`

**Nodo fuente (id=1):**
```json
"outputs": [
  {"name": "MODEL", "type": "MODEL", "slot_index": 0, "links": [1]}
]
```

**Nodo destino (id=2):**
```json
"inputs": [
  {"name": "model", "type": "MODEL", "link": 1}
]
```

**Link:**
```json
[1, 1, 0, 2, 0, "MODEL"]
```

### Paso 6: Actualizar contadores

Actualiza `last_node_id` y `last_link_id` al valor más alto usado:

```json
"last_node_id": 5,
"last_link_id": 6
```

---

## Tips para Modificar Workflows

### 1. Cambiar parámetros rápidamente

Modifica solo `widgets_values`:

```python
import json

with open('workflow.json', 'r') as f:
    wf = json.load(f)

# Buscar nodo por tipo e ID
for node in wf['nodes']:
    if node['type'] == 'LoadImage' and node['id'] == 2:
        node['widgets_values'][0] = 'nueva_imagen.png'

with open('workflow_modified.json', 'w') as f:
    json.dump(wf, f, indent=2)
```

### 2. Cambiar checkpoint

```python
for node in wf['nodes']:
    if node['type'] == 'CheckpointLoaderSimple':
        node['widgets_values'][0] = 'otro_modelo.safetensors'
```

### 3. Ajustar strength de ControlNet

```python
for node in wf['nodes']:
    if node['type'] == 'ControlNetApplyAdvanced' and node['id'] == 10:
        node['widgets_values'][0] = 0.8  # Nueva strength
```

### 4. Cambiar prompts

```python
for node in wf['nodes']:
    if node['type'] == 'CLIPTextEncode':
        if node['id'] == 5:  # Positive
            node['widgets_values'][0] = 'nuevo prompt positivo'
        elif node['id'] == 6:  # Negative
            node['widgets_values'][0] = 'nuevo prompt negativo'
```

---

## Depuración

### Verificar que todos los links existan

```python
def validate_links(workflow):
    link_ids = set(link[0] for link in workflow['links'])

    for node in workflow['nodes']:
        # Verificar inputs
        for inp in node.get('inputs', []):
            if inp.get('link') and inp['link'] not in link_ids:
                print(f"ERROR: Nodo {node['id']} input '{inp['name']}' referencia link inexistente {inp['link']}")

        # Verificar outputs
        for out in node.get('outputs', []):
            for link_id in (out.get('links') or []):
                if link_id not in link_ids:
                    print(f"ERROR: Nodo {node['id']} output '{out['name']}' referencia link inexistente {link_id}")
```

### Visualizar estructura

```python
def print_workflow_structure(workflow):
    for node in workflow['nodes']:
        print(f"\nNodo {node['id']}: {node['type']}")
        print(f"  Inputs: {[i['name'] for i in node.get('inputs', [])]}")
        print(f"  Outputs: {[o['name'] for o in node.get('outputs', [])]}")
        print(f"  Widgets: {node.get('widgets_values', [])}")
```

---

## Referencias Rápidas

### Nodos más usados:

| Nodo | Propósito |
|------|-----------|
| CheckpointLoaderSimple | Cargar modelo base |
| LoadImage | Cargar imagen |
| ControlNetLoader | Cargar ControlNet |
| ControlNetApplyAdvanced | Aplicar ControlNet |
| CLIPTextEncode | Codificar prompt |
| KSampler | Generar imagen |
| VAEDecode | Decodificar latent |
| SaveImage | Guardar resultado |
| EmptyLatentImage | Crear latent vacío |

### Tipos de datos:

| Tipo | Descripción |
|------|-------------|
| MODEL | Modelo UNet |
| CLIP | Encoder de texto |
| VAE | Autoencoder |
| IMAGE | Tensor de imagen |
| LATENT | Representación latent |
| CONDITIONING | Prompt codificado |
| CONTROL_NET | Modelo ControlNet |

---

**Ahora puedes crear y modificar tus propios workflows JSON de ComfyUI!**
