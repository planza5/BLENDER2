"""
Ejemplo de batch processing con ComfyUI API
Procesa múltiples renders de Blender automáticamente

Modelo usado: RealVisXL_V5.0.safetensors
"""
import requests
import json
import time
import os
from pathlib import Path

# Configuración
COMFYUI_URL = "http://localhost:8188"
WORKFLOW_FILE = "interior_depth_only.json"
INPUT_DIR = "../output_clean_rooms"  # Donde están tus renders de Blender
OUTPUT_PREFIX = "interior_generated"

# Prompts para diferentes tipos de habitaciones
ROOM_PROMPTS = {
    "living_room": {
        "positive": "modern living room interior, scandinavian design, large sofa, wooden coffee table, indoor plants, minimalist decor, natural light from windows, warm lighting, photorealistic, 8k",
        "negative": "blurry, low quality, cartoon, painting, sketch, unrealistic, distorted, deformed, bad geometry, wrong perspective, duplicate objects, floating objects, bad lighting, text, watermark"
    },
    "bedroom": {
        "positive": "cozy bedroom interior, queen size bed with white linens, wooden nightstands, modern pendant lights, area rug, plants, contemporary design, soft morning light, photorealistic, architectural photography",
        "negative": "blurry, low quality, cartoon, painting, sketch, unrealistic, distorted, deformed, bad geometry, wrong perspective, duplicate objects, floating objects, bad lighting, text, watermark"
    },
    "kitchen": {
        "positive": "modern kitchen interior, white cabinets, marble countertops, stainless steel appliances, island with bar stools, pendant lights, minimalist design, natural lighting, photorealistic, 8k, clean",
        "negative": "blurry, low quality, cartoon, painting, sketch, unrealistic, distorted, deformed, bad geometry, wrong perspective, duplicate objects, floating objects, bad lighting, text, watermark"
    },
    "bathroom": {
        "positive": "luxury bathroom interior, modern vanity, large mirror, walk-in shower, marble tiles, chrome fixtures, plants, ambient lighting, spa-like atmosphere, photorealistic, high-end design",
        "negative": "blurry, low quality, cartoon, painting, sketch, unrealistic, distorted, deformed, bad geometry, wrong perspective, duplicate objects, floating objects, bad lighting, text, watermark"
    }
}


def load_workflow(workflow_path):
    """Cargar workflow JSON"""
    with open(workflow_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def update_workflow_params(workflow, depth_image, prompt_type="living_room", seed=None):
    """
    Actualizar parámetros del workflow

    Args:
        workflow: dict del workflow JSON
        depth_image: nombre del archivo depth map (ej: "interior_00000_depth.png")
        prompt_type: tipo de habitación ("living_room", "bedroom", etc)
        seed: seed para reproducibilidad (None = aleatorio)
    """
    # Buscar nodos por tipo
    for node in workflow['nodes']:
        # LoadImage - actualizar depth map
        if node['type'] == 'LoadImage' and node['id'] == 2:
            node['widgets_values'][0] = depth_image

        # CLIPTextEncode - positive prompt
        elif node['type'] == 'CLIPTextEncode' and node['id'] == 5:
            node['widgets_values'][0] = ROOM_PROMPTS[prompt_type]['positive']

        # CLIPTextEncode - negative prompt
        elif node['type'] == 'CLIPTextEncode' and node['id'] == 6:
            node['widgets_values'][0] = ROOM_PROMPTS[prompt_type]['negative']

        # KSampler - seed
        elif node['type'] == 'KSampler' and node['id'] == 8:
            if seed is not None:
                node['widgets_values'][0] = seed
                node['widgets_values'][1] = "fixed"  # No randomize
            else:
                node['widgets_values'][1] = "randomize"

    return workflow


def queue_prompt(workflow):
    """
    Enviar workflow a ComfyUI para procesamiento

    Returns:
        prompt_id si tuvo éxito, None si falló
    """
    try:
        response = requests.post(
            f"{COMFYUI_URL}/prompt",
            json={"prompt": workflow}
        )
        response.raise_for_status()
        result = response.json()
        return result.get('prompt_id')
    except Exception as e:
        print(f"Error al enviar prompt: {e}")
        return None


def wait_for_completion(prompt_id, timeout=300):
    """
    Esperar a que se complete la generación

    Args:
        prompt_id: ID del prompt en la cola
        timeout: tiempo máximo de espera en segundos

    Returns:
        True si se completó, False si falló o timeout
    """
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            # Verificar estado de la cola
            response = requests.get(f"{COMFYUI_URL}/history/{prompt_id}")
            history = response.json()

            if prompt_id in history:
                status = history[prompt_id].get('status', {})
                if status.get('completed', False):
                    print(f"✓ Completado: {prompt_id}")
                    return True
                elif 'error' in status:
                    print(f"✗ Error: {status['error']}")
                    return False

            time.sleep(2)  # Esperar 2 segundos antes de verificar de nuevo

        except Exception as e:
            print(f"Error al verificar estado: {e}")
            time.sleep(2)

    print(f"✗ Timeout esperando {prompt_id}")
    return False


def find_depth_maps(input_dir):
    """
    Encontrar todos los depth maps en el directorio de entrada

    Returns:
        Lista de tuplas (scene_id, depth_file_path)
    """
    input_path = Path(input_dir)
    depth_maps = []

    for depth_file in sorted(input_path.glob("*_depth.png")):
        # Extraer ID de la escena (ej: "interior_00000" de "interior_00000_depth.png")
        scene_id = depth_file.stem.replace("_depth", "")
        depth_maps.append((scene_id, depth_file.name))

    return depth_maps


def batch_process(num_scenes=10, variations_per_scene=3):
    """
    Procesar múltiples escenas en batch

    Args:
        num_scenes: número de escenas a procesar
        variations_per_scene: cuántas variaciones generar por escena
    """
    # Cargar workflow base
    print(f"Cargando workflow: {WORKFLOW_FILE}")
    workflow_template = load_workflow(WORKFLOW_FILE)

    # Encontrar depth maps
    print(f"Buscando depth maps en: {INPUT_DIR}")
    depth_maps = find_depth_maps(INPUT_DIR)

    if not depth_maps:
        print("✗ No se encontraron depth maps!")
        return

    print(f"✓ Encontrados {len(depth_maps)} depth maps")

    # Procesar cada escena
    total_processed = 0
    total_failed = 0

    for scene_id, depth_file in depth_maps[:num_scenes]:
        print(f"\n{'='*60}")
        print(f"Procesando escena: {scene_id}")
        print(f"{'='*60}")

        # Generar variaciones
        for i in range(variations_per_scene):
            # Elegir tipo de habitación (rotar entre opciones)
            room_types = list(ROOM_PROMPTS.keys())
            room_type = room_types[i % len(room_types)]

            print(f"\n  Variación {i+1}/{variations_per_scene} - Tipo: {room_type}")

            # Crear workflow con parámetros actualizados
            workflow = json.loads(json.dumps(workflow_template))  # Deep copy
            workflow = update_workflow_params(
                workflow,
                depth_image=depth_file,
                prompt_type=room_type,
                seed=None  # Aleatorio
            )

            # Actualizar output prefix
            for node in workflow['nodes']:
                if node['type'] == 'SaveImage':
                    node['widgets_values'][0] = f"{OUTPUT_PREFIX}_{scene_id}_{room_type}_{i}"

            # Enviar a ComfyUI
            prompt_id = queue_prompt(workflow)

            if prompt_id:
                print(f"  → Encolado: {prompt_id}")

                # Esperar a que se complete
                if wait_for_completion(prompt_id, timeout=300):
                    total_processed += 1
                    print(f"  ✓ Generado exitosamente")
                else:
                    total_failed += 1
                    print(f"  ✗ Falló la generación")
            else:
                total_failed += 1
                print(f"  ✗ Error al encolar")

            # Pequeña pausa entre variaciones
            time.sleep(1)

    # Resumen final
    print(f"\n{'='*60}")
    print(f"RESUMEN")
    print(f"{'='*60}")
    print(f"Escenas procesadas: {num_scenes}")
    print(f"Variaciones por escena: {variations_per_scene}")
    print(f"Total generadas: {total_processed}")
    print(f"Total fallidas: {total_failed}")
    print(f"Tasa de éxito: {total_processed/(total_processed+total_failed)*100:.1f}%")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Batch processing con ComfyUI")
    parser.add_argument("--scenes", type=int, default=10, help="Número de escenas a procesar")
    parser.add_argument("--variations", type=int, default=3, help="Variaciones por escena")
    parser.add_argument("--workflow", type=str, default="interior_depth_only.json", help="Archivo workflow JSON")

    args = parser.parse_args()

    WORKFLOW_FILE = args.workflow

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║  ComfyUI Batch Processor - Perspectiva2                     ║
╚══════════════════════════════════════════════════════════════╝

Configuración:
  - Workflow: {WORKFLOW_FILE}
  - Input dir: {INPUT_DIR}
  - Escenas: {args.scenes}
  - Variaciones: {args.variations}
  - ComfyUI URL: {COMFYUI_URL}

Asegúrate de que ComfyUI esté corriendo en {COMFYUI_URL}
    """)

    input("Presiona ENTER para comenzar...")

    batch_process(num_scenes=args.scenes, variations_per_scene=args.variations)
