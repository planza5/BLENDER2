"""
Test de Texturas de Llana - Comparativa Visual
==============================================
Ejecutar: blender --background --python test_llana_textures.py
O desde Blender UI: Scripting > Run Script

Genera 4 variantes de marcas de llana para comparar:
1. Wave actual (CONTROL)
2. Noise anisotrópico (estirado + rotación)
3. Wave + distorsión fuerte con Noise
4. Musgrave Ridged (orgánico)
"""

import bpy
import math
import random
from pathlib import Path
import os

# Configuración
OUTPUT_DIR = Path(os.path.dirname(os.path.abspath(__file__))) / "test_output"
RESOLUTION = 512
RENDER_SAMPLES = 64

# Parámetros fijos para comparación justa
BASE_PARAMS = {
    "noise_scale": 8.0,
    "noise_detail": 5.0,
    "noise_roughness": 0.5,
    "color_base": (0.65, 0.65, 0.60, 1.0),
    "color_light": (0.88, 0.88, 0.85, 1.0),
}

def clear_scene():
    """Limpia la escena completamente."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Limpiar materiales
    for mat in bpy.data.materials:
        bpy.data.materials.remove(mat)


def setup_camera_and_lights():
    """Configura cámara ortográfica e iluminación."""
    # Cámara ortográfica
    bpy.ops.object.camera_add(location=(0, 0, 3))
    camera = bpy.context.active_object
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = 5.0  # Para ver los 4 planos
    camera.rotation_euler = (0, 0, 0)
    bpy.context.scene.camera = camera

    # Luz uniforme
    bpy.ops.object.light_add(type='SUN', location=(2, 2, 5))
    sun = bpy.context.active_object
    sun.data.energy = 3.0
    sun.rotation_euler = (math.radians(45), 0, math.radians(45))

    return camera


def configure_render():
    """Configura parámetros de renderizado."""
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = RENDER_SAMPLES
    scene.cycles.use_denoising = True
    scene.render.resolution_x = RESOLUTION * 2
    scene.render.resolution_y = RESOLUTION * 2
    scene.render.image_settings.file_format = 'PNG'

    # GPU con CUDA
    scene.cycles.device = 'GPU'
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'CUDA'
    prefs.get_devices()

    for device in prefs.devices:
        if device.type == 'CUDA':
            device.use = True
            print(f"  GPU: {device.name}")


def create_base_nodes(mat):
    """Crea nodos base compartidos por todos los materiales."""
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Coordenadas
    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-1200, 0)

    mapping = nodes.new('ShaderNodeMapping')
    mapping.location = (-1000, 0)
    links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])

    # Ruido base (común a todos)
    noise_base = nodes.new('ShaderNodeTexNoise')
    noise_base.location = (-700, 300)
    noise_base.name = "NoiseBase"
    noise_base.inputs['Scale'].default_value = BASE_PARAMS["noise_scale"]
    noise_base.inputs['Detail'].default_value = BASE_PARAMS["noise_detail"]
    noise_base.inputs['Roughness'].default_value = BASE_PARAMS["noise_roughness"]
    links.new(mapping.outputs['Vector'], noise_base.inputs['Vector'])

    return nodes, links, mapping, noise_base


def create_output_nodes(nodes, links, mixed_output):
    """Crea nodos de salida (ColorRamp + BSDF)."""
    # ColorRamp
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (200, 0)
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = BASE_PARAMS["color_base"]
    ramp.color_ramp.elements[1].position = 1.0
    ramp.color_ramp.elements[1].color = BASE_PARAMS["color_light"]
    links.new(mixed_output, ramp.inputs['Fac'])

    # BSDF
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (500, 0)
    bsdf.inputs['Roughness'].default_value = 0.4

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (750, 0)

    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])


# =============================================================================
# VARIANTE 1: WAVE ACTUAL (CONTROL)
# =============================================================================
def create_material_wave_control():
    """Material original con Wave texture."""
    mat = bpy.data.materials.new(name="1_Wave_Control")
    mat.use_nodes = True
    mat.node_tree.nodes.clear()

    nodes, links, mapping, noise_base = create_base_nodes(mat)

    # Wave texture (como el original)
    wave = nodes.new('ShaderNodeTexWave')
    wave.location = (-700, 0)
    wave.name = "Wave"
    wave.wave_type = 'BANDS'
    wave.bands_direction = 'DIAGONAL'
    wave.wave_profile = 'SIN'
    wave.inputs['Scale'].default_value = 3.0
    wave.inputs['Distortion'].default_value = 5.0
    wave.inputs['Detail'].default_value = 2.0
    links.new(mapping.outputs['Vector'], wave.inputs['Vector'])

    # Mix con ruido base
    mix = nodes.new('ShaderNodeMixRGB')
    mix.location = (-400, 150)
    mix.blend_type = 'OVERLAY'
    mix.inputs['Fac'].default_value = 0.3
    links.new(noise_base.outputs['Fac'], mix.inputs['Color1'])
    links.new(wave.outputs['Fac'], mix.inputs['Color2'])

    create_output_nodes(nodes, links, mix.outputs['Color'])
    return mat


# =============================================================================
# VARIANTE 2: NOISE ANISOTRÓPICO (Estirado + Rotación)
# =============================================================================
def create_material_noise_anisotropic():
    """Noise estirado para simular direccionalidad de llana."""
    mat = bpy.data.materials.new(name="2_Noise_Anisotropic")
    mat.use_nodes = True
    mat.node_tree.nodes.clear()

    nodes, links, mapping, noise_base = create_base_nodes(mat)

    # Mapping específico para llana (escala anisotrópica)
    mapping_llana = nodes.new('ShaderNodeMapping')
    mapping_llana.location = (-850, -100)
    mapping_llana.inputs['Scale'].default_value = (25.0, 3.0, 1.0)  # Muy estirado en X
    mapping_llana.inputs['Rotation'].default_value = (0, 0, math.radians(35))  # Rotación
    links.new(mapping.outputs['Vector'], mapping_llana.inputs['Vector'])

    # Noise para distorsión (hace irregular las marcas)
    noise_distort = nodes.new('ShaderNodeTexNoise')
    noise_distort.location = (-850, -300)
    noise_distort.inputs['Scale'].default_value = 6.0
    noise_distort.inputs['Detail'].default_value = 3.0
    links.new(mapping.outputs['Vector'], noise_distort.inputs['Vector'])

    # Vector Math: añadir distorsión
    vec_add = nodes.new('ShaderNodeVectorMath')
    vec_add.location = (-600, -200)
    vec_add.operation = 'ADD'
    links.new(mapping_llana.outputs['Vector'], vec_add.inputs[0])
    links.new(noise_distort.outputs['Color'], vec_add.inputs[1])

    # Noise de llana (con coordenadas distorsionadas)
    noise_llana = nodes.new('ShaderNodeTexNoise')
    noise_llana.location = (-700, -100)
    noise_llana.name = "NoiseLlana"
    noise_llana.inputs['Scale'].default_value = 1.0
    noise_llana.inputs['Detail'].default_value = 1.0
    links.new(vec_add.outputs['Vector'], noise_llana.inputs['Vector'])

    # ColorRamp para aumentar contraste del noise de llana
    ramp_llana = nodes.new('ShaderNodeValToRGB')
    ramp_llana.location = (-500, -100)
    ramp_llana.color_ramp.elements[0].position = 0.3
    ramp_llana.color_ramp.elements[1].position = 0.7
    links.new(noise_llana.outputs['Fac'], ramp_llana.inputs['Fac'])

    # Mix con ruido base (intensidad aumentada)
    mix = nodes.new('ShaderNodeMixRGB')
    mix.location = (-400, 150)
    mix.blend_type = 'OVERLAY'
    mix.inputs['Fac'].default_value = 0.6  # Aumentado de 0.25 a 0.6
    links.new(noise_base.outputs['Fac'], mix.inputs['Color1'])
    links.new(ramp_llana.outputs['Color'], mix.inputs['Color2'])

    create_output_nodes(nodes, links, mix.outputs['Color'])
    return mat


# =============================================================================
# VARIANTE 3: WAVE + DISTORSIÓN FUERTE
# =============================================================================
def create_material_wave_distorted():
    """Wave con coordenadas fuertemente distorsionadas."""
    mat = bpy.data.materials.new(name="3_Wave_Distorted")
    mat.use_nodes = True
    mat.node_tree.nodes.clear()

    nodes, links, mapping, noise_base = create_base_nodes(mat)

    # Noise para distorsionar coordenadas
    noise_warp = nodes.new('ShaderNodeTexNoise')
    noise_warp.location = (-850, -100)
    noise_warp.inputs['Scale'].default_value = 4.0
    noise_warp.inputs['Detail'].default_value = 5.0
    noise_warp.inputs['Distortion'].default_value = 3.0
    links.new(mapping.outputs['Vector'], noise_warp.inputs['Vector'])

    # Vector Math: distorsión fuerte
    vec_multiply = nodes.new('ShaderNodeVectorMath')
    vec_multiply.location = (-650, -100)
    vec_multiply.operation = 'MULTIPLY'
    vec_multiply.inputs[1].default_value = (0.8, 0.8, 0.0)  # Factor de distorsión
    links.new(noise_warp.outputs['Color'], vec_multiply.inputs[0])

    vec_add = nodes.new('ShaderNodeVectorMath')
    vec_add.location = (-500, 0)
    vec_add.operation = 'ADD'
    links.new(mapping.outputs['Vector'], vec_add.inputs[0])
    links.new(vec_multiply.outputs['Vector'], vec_add.inputs[1])

    # Wave con coordenadas distorsionadas
    wave = nodes.new('ShaderNodeTexWave')
    wave.location = (-700, 0)
    wave.wave_type = 'BANDS'
    wave.bands_direction = 'DIAGONAL'
    wave.wave_profile = 'SIN'
    wave.inputs['Scale'].default_value = 3.0
    wave.inputs['Distortion'].default_value = 2.0
    links.new(vec_add.outputs['Vector'], wave.inputs['Vector'])

    # ColorRamp para ajustar contraste
    ramp_wave = nodes.new('ShaderNodeValToRGB')
    ramp_wave.location = (-500, 0)
    ramp_wave.color_ramp.elements[0].position = 0.35
    ramp_wave.color_ramp.elements[1].position = 0.65
    links.new(wave.outputs['Fac'], ramp_wave.inputs['Fac'])

    # Mix (intensidad aumentada)
    mix = nodes.new('ShaderNodeMixRGB')
    mix.location = (-400, 150)
    mix.blend_type = 'OVERLAY'
    mix.inputs['Fac'].default_value = 0.6  # Aumentado de 0.3 a 0.6
    links.new(noise_base.outputs['Fac'], mix.inputs['Color1'])
    links.new(ramp_wave.outputs['Color'], mix.inputs['Color2'])

    create_output_nodes(nodes, links, mix.outputs['Color'])
    return mat


# =============================================================================
# VARIANTE 4: VORONOI CRACKLE (Orgánico - marcas irregulares)
# =============================================================================
def create_material_voronoi_crackle():
    """Voronoi Crackle para marcas orgánicas e irregulares."""
    mat = bpy.data.materials.new(name="4_Voronoi_Crackle")
    mat.use_nodes = True
    mat.node_tree.nodes.clear()

    nodes, links, mapping, noise_base = create_base_nodes(mat)

    # Mapping con rotación para direccionalidad
    mapping_voronoi = nodes.new('ShaderNodeMapping')
    mapping_voronoi.location = (-850, -100)
    mapping_voronoi.inputs['Scale'].default_value = (20.0, 5.0, 1.0)
    mapping_voronoi.inputs['Rotation'].default_value = (0, 0, math.radians(40))
    links.new(mapping.outputs['Vector'], mapping_voronoi.inputs['Vector'])

    # Voronoi Crackle (crea patrones de grietas/líneas orgánicas)
    voronoi = nodes.new('ShaderNodeTexVoronoi')
    voronoi.location = (-700, -100)
    voronoi.distance = 'EUCLIDEAN'
    voronoi.feature = 'DISTANCE_TO_EDGE'  # Crea líneas en los bordes
    voronoi.inputs['Scale'].default_value = 3.0
    links.new(mapping_voronoi.outputs['Vector'], voronoi.inputs['Vector'])

    # ColorRamp para suavizar y controlar intensidad
    ramp_voronoi = nodes.new('ShaderNodeValToRGB')
    ramp_voronoi.location = (-500, -100)
    ramp_voronoi.color_ramp.elements[0].position = 0.2  # Más contraste
    ramp_voronoi.color_ramp.elements[1].position = 0.7
    links.new(voronoi.outputs['Distance'], ramp_voronoi.inputs['Fac'])

    # Mix (intensidad aumentada)
    mix = nodes.new('ShaderNodeMixRGB')
    mix.location = (-400, 150)
    mix.blend_type = 'OVERLAY'  # Cambiado de SOFT_LIGHT a OVERLAY
    mix.inputs['Fac'].default_value = 0.55  # Aumentado de 0.25 a 0.55
    links.new(noise_base.outputs['Fac'], mix.inputs['Color1'])
    links.new(ramp_voronoi.outputs['Color'], mix.inputs['Color2'])

    create_output_nodes(nodes, links, mix.outputs['Color'])
    return mat


# =============================================================================
# SETUP DE ESCENA CON 4 PLANOS
# =============================================================================
def create_comparison_scene():
    """Crea escena con 4 planos en grid 2x2."""
    clear_scene()
    configure_render()
    setup_camera_and_lights()

    # Crear materiales
    materials = [
        create_material_wave_control(),
        create_material_noise_anisotropic(),
        create_material_wave_distorted(),
        create_material_voronoi_crackle()
    ]

    # Crear 4 planos en grid
    positions = [
        (-1.2, 1.2, 0),   # Top-left
        (1.2, 1.2, 0),    # Top-right
        (-1.2, -1.2, 0),  # Bottom-left
        (1.2, -1.2, 0)    # Bottom-right
    ]

    planes = []
    for i, (mat, pos) in enumerate(zip(materials, positions)):
        bpy.ops.mesh.primitive_plane_add(size=2, location=pos)
        plane = bpy.context.active_object
        plane.name = f"Plane_{i+1}_{mat.name}"
        plane.data.materials.append(mat)
        planes.append(plane)
        print(f"  Plano {i+1}: {mat.name} en {pos}")

    return planes


# =============================================================================
# RENDER
# =============================================================================
def render_comparison():
    """Renderiza la comparativa."""
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("\n" + "="*60)
    print("TEST DE TEXTURAS DE LLANA - Comparativa")
    print("="*60)

    create_comparison_scene()

    # Render
    output_path = OUTPUT_DIR / "llana_comparison.png"
    bpy.context.scene.render.filepath = str(output_path)

    print(f"\nRenderizando comparativa...")
    print(f"Output: {output_path}")
    bpy.ops.render.render(write_still=True)

    print("\n✓ Comparativa generada")
    print(f"\nLayout:")
    print("  ┌─────────────────┬─────────────────┐")
    print("  │  1. Wave        │  2. Noise       │")
    print("  │  (Control)      │  (Anisotrópico) │")
    print("  ├─────────────────┼─────────────────┤")
    print("  │  3. Wave        │  4. Voronoi     │")
    print("  │  (Distorsionado)│  (Crackle)      │")
    print("  └─────────────────┴─────────────────┘")
    print(f"\nArchivo: {output_path}")


# =============================================================================
# MAIN
# =============================================================================
if __name__ == "__main__":
    render_comparison()
else:
    render_comparison()
