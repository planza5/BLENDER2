"""
Generador de Dataset de Microcemento para Blender
==================================================
Ejecutar desde Blender: blender --background --python microcemento_dataset_generator.py
O desde la interfaz: Scripting > Run Script

Genera pares de (imagen, parámetros) para entrenar una red neuronal
que infiera parámetros procedurales a partir de texturas reales.
"""

import bpy
import random
import json
import os
import math
from pathlib import Path

# =============================================================================
# CONFIGURACIÓN
# =============================================================================

CONFIG = {
    "num_samples": 20000,
    "resolution": 512,
    "samples_render": 32,  # Reducido para acelerar, suficiente para texturas planas
}

def get_output_dir():
    """Obtiene el directorio de salida relativo al script."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, "output")

# =============================================================================
# DEFINICIÓN DE PARÁMETROS Y SUS RANGOS
# =============================================================================

PARAMETERS = {
    # Ruido base - variación tonal
    "noise_scale": {"min": 2.0, "max": 15.0},
    "noise_detail": {"min": 2.0, "max": 8.0},
    "noise_roughness": {"min": 0.3, "max": 0.7},
    
    # Marcas de llana (Wave texture)
    "wave_scale": {"min": 1.0, "max": 5.0},
    "wave_distortion": {"min": 1.0, "max": 10.0},
    "wave_detail": {"min": 0.0, "max": 4.0},
    "wave_intensity": {"min": 0.1, "max": 0.5},  # Mezcla con el ruido base
    
    # Voronoi - manchas sutiles
    "voronoi_scale": {"min": 3.0, "max": 12.0},
    "voronoi_intensity": {"min": 0.05, "max": 0.25},
    
    # Colores del ramp (grises/beiges cálidos)
    # Color 1 - tono más oscuro
    "color1_value": {"min": 0.55, "max": 0.75},  # Luminosidad
    "color1_warmth": {"min": 0.0, "max": 0.08},  # Desviación hacia beige
    
    # Color 2 - tono más claro  
    "color2_value": {"min": 0.80, "max": 0.95},
    "color2_warmth": {"min": 0.0, "max": 0.08},
    
    # Posición del color medio en el ramp
    "ramp_midpoint": {"min": 0.35, "max": 0.65},
}


def sample_parameters():
    """Genera un conjunto aleatorio de parámetros dentro de los rangos definidos."""
    params = {}
    for name, range_dict in PARAMETERS.items():
        params[name] = random.uniform(range_dict["min"], range_dict["max"])
    return params


# =============================================================================
# CREACIÓN DEL NODE TREE
# =============================================================================

def create_microcemento_material():
    """Crea el material de microcemento con todos los nodos necesarios."""
    
    # Crear material
    mat = bpy.data.materials.get("Microcemento")
    if mat:
        bpy.data.materials.remove(mat)
    
    mat = bpy.data.materials.new(name="Microcemento")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Limpiar nodos por defecto
    nodes.clear()
    
    # === NODOS DE COORDENADAS ===
    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-1200, 0)
    
    mapping = nodes.new('ShaderNodeMapping')
    mapping.location = (-1000, 0)
    links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])
    
    # === CAPA 1: RUIDO BASE (variación tonal) ===
    noise_base = nodes.new('ShaderNodeTexNoise')
    noise_base.location = (-600, 200)
    noise_base.name = "NoiseBase"
    links.new(mapping.outputs['Vector'], noise_base.inputs['Vector'])
    
    # === CAPA 2: WAVE TEXTURE (marcas de llana) ===
    wave = nodes.new('ShaderNodeTexWave')
    wave.location = (-600, -100)
    wave.name = "WaveLlana"
    wave.wave_type = 'BANDS'
    wave.bands_direction = 'DIAGONAL'
    wave.wave_profile = 'SIN'
    links.new(mapping.outputs['Vector'], wave.inputs['Vector'])
    
    # Mezclar ruido base con wave
    mix_noise_wave = nodes.new('ShaderNodeMixRGB')
    mix_noise_wave.location = (-300, 100)
    mix_noise_wave.name = "MixNoiseWave"
    mix_noise_wave.blend_type = 'OVERLAY'
    links.new(noise_base.outputs['Fac'], mix_noise_wave.inputs['Color1'])
    links.new(wave.outputs['Fac'], mix_noise_wave.inputs['Color2'])
    
    # === CAPA 3: VORONOI (manchas sutiles) ===
    voronoi = nodes.new('ShaderNodeTexVoronoi')
    voronoi.location = (-600, -400)
    voronoi.name = "VoronoiManchas"
    voronoi.feature = 'SMOOTH_F1'
    links.new(mapping.outputs['Vector'], voronoi.inputs['Vector'])
    
    # Mezclar con voronoi
    mix_voronoi = nodes.new('ShaderNodeMixRGB')
    mix_voronoi.location = (-100, 0)
    mix_voronoi.name = "MixVoronoi"
    mix_voronoi.blend_type = 'SOFT_LIGHT'
    links.new(mix_noise_wave.outputs['Color'], mix_voronoi.inputs['Color1'])
    links.new(voronoi.outputs['Distance'], mix_voronoi.inputs['Color2'])
    
    # === COLOR RAMP (mapeo a colores finales) ===
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (150, 0)
    ramp.name = "ColorRamp"
    
    # Configurar ramp con 3 colores
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[1].position = 0.5
    
    # Añadir tercer color
    ramp.color_ramp.elements.new(1.0)
    
    links.new(mix_voronoi.outputs['Color'], ramp.inputs['Fac'])
    
    # === OUTPUT ===
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (450, 0)
    bsdf.inputs['Roughness'].default_value = 0.4
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (700, 0)
    
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return mat


def apply_parameters(mat, params):
    """Aplica un conjunto de parámetros al material."""
    nodes = mat.node_tree.nodes
    
    # Ruido base
    noise = nodes["NoiseBase"]
    noise.inputs['Scale'].default_value = params["noise_scale"]
    noise.inputs['Detail'].default_value = params["noise_detail"]
    noise.inputs['Roughness'].default_value = params["noise_roughness"]
    
    # Wave (llana)
    wave = nodes["WaveLlana"]
    wave.inputs['Scale'].default_value = params["wave_scale"]
    wave.inputs['Distortion'].default_value = params["wave_distortion"]
    wave.inputs['Detail'].default_value = params["wave_detail"]
    
    # Mix intensidad wave
    mix_wave = nodes["MixNoiseWave"]
    mix_wave.inputs['Fac'].default_value = params["wave_intensity"]
    
    # Voronoi
    voronoi = nodes["VoronoiManchas"]
    voronoi.inputs['Scale'].default_value = params["voronoi_scale"]
    
    # Mix intensidad voronoi
    mix_voronoi = nodes["MixVoronoi"]
    mix_voronoi.inputs['Fac'].default_value = params["voronoi_intensity"]
    
    # Color ramp
    ramp = nodes["ColorRamp"]
    
    # Color 1 (oscuro) - gris/beige
    v1 = params["color1_value"]
    w1 = params["color1_warmth"]
    ramp.color_ramp.elements[0].color = (v1 + w1, v1, v1 - w1 * 0.5, 1.0)
    
    # Color 2 (medio)
    v_mid = (params["color1_value"] + params["color2_value"]) / 2
    w_mid = (params["color1_warmth"] + params["color2_warmth"]) / 2
    ramp.color_ramp.elements[1].color = (v_mid + w_mid, v_mid, v_mid - w_mid * 0.5, 1.0)
    ramp.color_ramp.elements[1].position = params["ramp_midpoint"]
    
    # Color 3 (claro)
    v2 = params["color2_value"]
    w2 = params["color2_warmth"]
    ramp.color_ramp.elements[2].color = (v2 + w2, v2, v2 - w2 * 0.5, 1.0)


# =============================================================================
# SETUP DE ESCENA
# =============================================================================

def setup_scene():
    """Configura la escena para renderizar texturas planas."""
    
    # Limpiar escena
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Crear plano
    bpy.ops.mesh.primitive_plane_add(size=2, location=(0, 0, 0))
    plane = bpy.context.active_object
    plane.name = "TexturePlane"
    
    # Crear cámara ortográfica mirando hacia abajo
    bpy.ops.object.camera_add(location=(0, 0, 1))
    camera = bpy.context.active_object
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = 2.0
    camera.rotation_euler = (0, 0, 0)
    bpy.context.scene.camera = camera
    
    # Iluminación uniforme
    bpy.ops.object.light_add(type='SUN', location=(0, 0, 3))
    sun = bpy.context.active_object
    sun.data.energy = 3.0
    
    # Configurar render
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = CONFIG["samples_render"]
    scene.cycles.use_denoising = True
    scene.render.resolution_x = CONFIG["resolution"]
    scene.render.resolution_y = CONFIG["resolution"]
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'
    
    # Configurar GPU con CUDA
    scene.cycles.device = 'GPU'
    
    # Activar CUDA (más compatible que OptiX en pods)
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'CUDA'
    prefs.get_devices()
    
    # Activar todos los dispositivos GPU disponibles
    for device in prefs.devices:
        if device.type == 'CUDA':
            device.use = True
            print(f"  GPU activada: {device.name}")
        else:
            device.use = False
    
    return plane


# =============================================================================
# GENERACIÓN DEL DATASET
# =============================================================================

def generate_dataset():
    """Genera el dataset completo de imágenes y parámetros."""
    import shutil
    
    output_dir = Path(get_output_dir())
    
    # Si existe, borrar contenido
    if output_dir.exists():
        shutil.rmtree(output_dir)
        print(f"Directorio existente eliminado: {output_dir}")
    
    # Crear directorios
    images_dir = output_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    
    # Setup
    plane = setup_scene()
    mat = create_microcemento_material()
    plane.data.materials.append(mat)
    
    # Lista para guardar todos los parámetros
    dataset = []
    json_path = output_dir / "dataset.json"
    
    print(f"\nGenerando {CONFIG['num_samples']} muestras...")
    print(f"Output: {output_dir}\n")
    
    for i in range(CONFIG["num_samples"]):
        # Generar parámetros aleatorios
        params = sample_parameters()
        
        # Aplicar al material
        apply_parameters(mat, params)
        
        # Renderizar
        filename = f"sample_{i:06d}.png"
        filepath = images_dir / filename
        bpy.context.scene.render.filepath = str(filepath)
        bpy.ops.render.render(write_still=True)
        
        # Guardar entrada del dataset
        entry = {
            "id": i,
            "filename": filename,
            "parameters": params
        }
        dataset.append(entry)
        
        # Guardar JSON cada 10 muestras (incremental)
        if (i + 1) % 10 == 0:
            with open(json_path, 'w') as f:
                json.dump({
                    "config": CONFIG,
                    "parameters_ranges": PARAMETERS,
                    "samples": dataset
                }, f, indent=2)
        
        # Progress
        if (i + 1) % 100 == 0:
            print(f"  Generadas {i + 1}/{CONFIG['num_samples']} muestras")
    
    # Guardar JSON final
    with open(json_path, 'w') as f:
        json.dump({
            "config": CONFIG,
            "parameters_ranges": PARAMETERS,
            "samples": dataset
        }, f, indent=2)
    
    print(f"\n✓ Dataset generado en {output_dir}")
    print(f"  - {CONFIG['num_samples']} imágenes en /images")
    print(f"  - Parámetros en dataset.json")
    
    return dataset


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    generate_dataset()
else:
    # Blender con --python a veces no entra en __main__
    generate_dataset()
