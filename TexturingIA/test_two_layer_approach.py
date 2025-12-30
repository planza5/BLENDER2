"""
Enfoque de Dos Capas para Microcemento
======================================
Ejecutar: blender --background --python test_two_layer_approach.py

Simula el proceso real de aplicación:
1. CAPA BASE: Textura en tiles (sin marcas de llana)
2. CAPA LLANA: Marcas localizadas solo en ciertas zonas (enmascaradas)

Genera 3 variantes:
- Solo base (sin llana)
- Base + llana UNIFORME (enfoque antiguo - malo)
- Base + llana ENMASCARADA (enfoque nuevo - realista)
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

def clear_scene():
    """Limpia la escena completamente."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for mat in bpy.data.materials:
        bpy.data.materials.remove(mat)

def setup_camera_and_lights():
    """Configura cámara ortográfica e iluminación."""
    bpy.ops.object.camera_add(location=(0, 0, 3))
    camera = bpy.context.active_object
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = 4.0
    camera.rotation_euler = (0, 0, 0)
    bpy.context.scene.camera = camera

    bpy.ops.object.light_add(type='SUN', location=(2, 2, 5))
    sun = bpy.context.active_object
    sun.data.energy = 3.0
    sun.rotation_euler = (math.radians(45), 0, math.radians(45))

def configure_render():
    """Configura parámetros de renderizado."""
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = RENDER_SAMPLES
    scene.cycles.use_denoising = True
    scene.render.resolution_x = RESOLUTION * 3
    scene.render.resolution_y = RESOLUTION
    scene.render.image_settings.file_format = 'PNG'

    scene.cycles.device = 'GPU'
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'CUDA'
    prefs.get_devices()

    for device in prefs.devices:
        if device.type == 'CUDA':
            device.use = True


# =============================================================================
# CAPA BASE: Textura tiled (sin llana)
# =============================================================================
def create_base_layer(nodes, links, mapping):
    """Crea la capa base con textura en tiles."""

    # Noise base con TILE/REPEAT
    noise_base = nodes.new('ShaderNodeTexNoise')
    noise_base.location = (-700, 200)
    noise_base.name = "NoiseBase"
    noise_base.inputs['Scale'].default_value = 8.0
    noise_base.inputs['Detail'].default_value = 5.0
    noise_base.inputs['Roughness'].default_value = 0.5
    links.new(mapping.outputs['Vector'], noise_base.inputs['Vector'])

    # Voronoi para manchas sutiles (también tiled)
    voronoi = nodes.new('ShaderNodeTexVoronoi')
    voronoi.location = (-700, -100)
    voronoi.name = "VoronoiBase"
    voronoi.feature = 'SMOOTH_F1'
    voronoi.inputs['Scale'].default_value = 6.0
    links.new(mapping.outputs['Vector'], voronoi.inputs['Vector'])

    # Mix base
    mix_base = nodes.new('ShaderNodeMixRGB')
    mix_base.location = (-450, 100)
    mix_base.name = "MixBase"
    mix_base.blend_type = 'SOFT_LIGHT'
    mix_base.inputs['Fac'].default_value = 0.2
    links.new(noise_base.outputs['Fac'], mix_base.inputs['Color1'])
    links.new(voronoi.outputs['Distance'], mix_base.inputs['Color2'])

    return mix_base.outputs['Color']


# =============================================================================
# CAPA LLANA: Marcas direccionales
# =============================================================================
def create_trowel_layer(nodes, links, mapping):
    """Crea las marcas de llana (noise anisotrópico)."""

    # Mapping estirado para direccionalidad
    mapping_trowel = nodes.new('ShaderNodeMapping')
    mapping_trowel.location = (-850, -400)
    mapping_trowel.inputs['Scale'].default_value = (25.0, 3.0, 1.0)
    mapping_trowel.inputs['Rotation'].default_value = (0, 0, math.radians(35))
    links.new(mapping.outputs['Vector'], mapping_trowel.inputs['Vector'])

    # Noise para distorsión
    noise_distort = nodes.new('ShaderNodeTexNoise')
    noise_distort.location = (-850, -600)
    noise_distort.inputs['Scale'].default_value = 6.0
    noise_distort.inputs['Detail'].default_value = 3.0
    links.new(mapping.outputs['Vector'], noise_distort.inputs['Vector'])

    # Vector Math: distorsión
    vec_add = nodes.new('ShaderNodeVectorMath')
    vec_add.location = (-600, -500)
    vec_add.operation = 'ADD'
    links.new(mapping_trowel.outputs['Vector'], vec_add.inputs[0])
    links.new(noise_distort.outputs['Color'], vec_add.inputs[1])

    # Noise de llana
    noise_trowel = nodes.new('ShaderNodeTexNoise')
    noise_trowel.location = (-700, -400)
    noise_trowel.name = "NoiseTrowel"
    noise_trowel.inputs['Scale'].default_value = 1.0
    noise_trowel.inputs['Detail'].default_value = 1.0
    links.new(vec_add.outputs['Vector'], noise_trowel.inputs['Vector'])

    # ColorRamp para contraste
    ramp_trowel = nodes.new('ShaderNodeValToRGB')
    ramp_trowel.location = (-500, -400)
    ramp_trowel.color_ramp.elements[0].position = 0.3
    ramp_trowel.color_ramp.elements[1].position = 0.7
    links.new(noise_trowel.outputs['Fac'], ramp_trowel.inputs['Fac'])

    return ramp_trowel.outputs['Color']


# =============================================================================
# MÁSCARA: Define dónde aparecen las marcas de llana
# =============================================================================
def create_trowel_mask(nodes, links, mapping):
    """Crea máscara para zonas con marcas de llana."""

    # Voronoi para crear "zonas" aleatorias
    voronoi_mask = nodes.new('ShaderNodeTexVoronoi')
    voronoi_mask.location = (-850, -800)
    voronoi_mask.name = "VoronoiMask"
    voronoi_mask.feature = 'SMOOTH_F1'
    voronoi_mask.inputs['Scale'].default_value = 2.5  # Zonas grandes
    voronoi_mask.inputs['Randomness'].default_value = 1.0
    links.new(mapping.outputs['Vector'], voronoi_mask.inputs['Vector'])

    # ColorRamp para convertir en máscara binaria/suave
    ramp_mask = nodes.new('ShaderNodeValToRGB')
    ramp_mask.location = (-650, -800)
    ramp_mask.name = "MaskRamp"
    # Ajustar para que ~50-70% de la superficie tenga marcas
    ramp_mask.color_ramp.elements[0].position = 0.3
    ramp_mask.color_ramp.elements[1].position = 0.6
    ramp_mask.color_ramp.interpolation = 'EASE'  # Transición suave
    links.new(voronoi_mask.outputs['Distance'], ramp_mask.inputs['Fac'])

    return ramp_mask.outputs['Color']


# =============================================================================
# VARIANTE 1: SOLO BASE (sin llana)
# =============================================================================
def create_material_base_only():
    """Material con solo la textura base, sin marcas de llana."""
    mat = bpy.data.materials.new(name="1_Base_Only")
    mat.use_nodes = True
    mat.node_tree.nodes.clear()

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Coordenadas
    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-1200, 0)

    mapping = nodes.new('ShaderNodeMapping')
    mapping.location = (-1000, 0)
    links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])

    # Solo capa base
    base_output = create_base_layer(nodes, links, mapping)

    # ColorRamp final
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (200, 0)
    ramp.color_ramp.elements[0].color = (0.65, 0.65, 0.60, 1.0)
    ramp.color_ramp.elements[1].color = (0.88, 0.88, 0.85, 1.0)
    links.new(base_output, ramp.inputs['Fac'])

    # BSDF + Output
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (500, 0)
    bsdf.inputs['Roughness'].default_value = 0.4

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (750, 0)

    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    return mat


# =============================================================================
# VARIANTE 2: BASE + LLANA UNIFORME (enfoque antiguo)
# =============================================================================
def create_material_uniform_trowel():
    """Material con llana aplicada uniformemente (malo)."""
    mat = bpy.data.materials.new(name="2_Uniform_Trowel")
    mat.use_nodes = True
    mat.node_tree.nodes.clear()

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Coordenadas
    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-1200, 0)

    mapping = nodes.new('ShaderNodeMapping')
    mapping.location = (-1000, 0)
    links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])

    # Capa base
    base_output = create_base_layer(nodes, links, mapping)

    # Capa llana
    trowel_output = create_trowel_layer(nodes, links, mapping)

    # Mix UNIFORME (sin máscara)
    mix_uniform = nodes.new('ShaderNodeMixRGB')
    mix_uniform.location = (-200, 0)
    mix_uniform.blend_type = 'OVERLAY'
    mix_uniform.inputs['Fac'].default_value = 0.5  # Siempre 50%
    links.new(base_output, mix_uniform.inputs['Color1'])
    links.new(trowel_output, mix_uniform.inputs['Color2'])

    # ColorRamp final
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (200, 0)
    ramp.color_ramp.elements[0].color = (0.65, 0.65, 0.60, 1.0)
    ramp.color_ramp.elements[1].color = (0.88, 0.88, 0.85, 1.0)
    links.new(mix_uniform.outputs['Color'], ramp.inputs['Fac'])

    # BSDF + Output
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (500, 0)
    bsdf.inputs['Roughness'].default_value = 0.4

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (750, 0)

    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    return mat


# =============================================================================
# VARIANTE 3: BASE + LLANA ENMASCARADA (enfoque nuevo - realista)
# =============================================================================
def create_material_masked_trowel():
    """Material con llana enmascarada (solo en ciertas zonas)."""
    mat = bpy.data.materials.new(name="3_Masked_Trowel")
    mat.use_nodes = True
    mat.node_tree.nodes.clear()

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Coordenadas
    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-1200, 0)

    mapping = nodes.new('ShaderNodeMapping')
    mapping.location = (-1000, 0)
    links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])

    # Capa base
    base_output = create_base_layer(nodes, links, mapping)

    # Capa llana
    trowel_output = create_trowel_layer(nodes, links, mapping)

    # MÁSCARA (define dónde aparece la llana)
    mask_output = create_trowel_mask(nodes, links, mapping)

    # Mix ENMASCARADO (intensidad controlada por máscara)
    mix_masked = nodes.new('ShaderNodeMixRGB')
    mix_masked.location = (-200, 0)
    mix_masked.name = "MixMasked"
    mix_masked.blend_type = 'OVERLAY'
    links.new(mask_output, mix_masked.inputs['Fac'])  # Máscara controla intensidad
    links.new(base_output, mix_masked.inputs['Color1'])
    links.new(trowel_output, mix_masked.inputs['Color2'])

    # ColorRamp final
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (200, 0)
    ramp.color_ramp.elements[0].color = (0.65, 0.65, 0.60, 1.0)
    ramp.color_ramp.elements[1].color = (0.88, 0.88, 0.85, 1.0)
    links.new(mix_masked.outputs['Color'], ramp.inputs['Fac'])

    # BSDF + Output
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (500, 0)
    bsdf.inputs['Roughness'].default_value = 0.4

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (750, 0)

    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    return mat


# =============================================================================
# SETUP DE ESCENA CON 3 PLANOS
# =============================================================================
def create_comparison_scene():
    """Crea escena con 3 planos lado a lado."""
    clear_scene()
    configure_render()
    setup_camera_and_lights()

    # Crear materiales
    materials = [
        create_material_base_only(),
        create_material_uniform_trowel(),
        create_material_masked_trowel()
    ]

    # Crear 3 planos en fila horizontal
    positions = [
        (-1.8, 0, 0),   # Izquierda
        (0, 0, 0),      # Centro
        (1.8, 0, 0)     # Derecha
    ]

    planes = []
    for i, (mat, pos) in enumerate(zip(materials, positions)):
        bpy.ops.mesh.primitive_plane_add(size=1.5, location=pos)
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
    print("TEST: Enfoque de Dos Capas")
    print("="*60)

    create_comparison_scene()

    # Render
    output_path = OUTPUT_DIR / "two_layer_comparison.png"
    bpy.context.scene.render.filepath = str(output_path)

    print(f"\nRenderizando comparativa...")
    print(f"Output: {output_path}")
    bpy.ops.render.render(write_still=True)

    print("\n✓ Comparativa generada")
    print(f"\nLayout (horizontal):")
    print("  ┌──────────────┬──────────────┬──────────────┐")
    print("  │   1. Solo    │  2. Llana    │  3. Llana    │")
    print("  │   Base       │  UNIFORME    │  ENMASCARADA │")
    print("  │              │  (malo)      │  (realista)  │")
    print("  └──────────────┴──────────────┴──────────────┘")
    print(f"\nArchivo: {output_path}")


# =============================================================================
# MAIN
# =============================================================================
if __name__ == "__main__":
    render_comparison()
else:
    render_comparison()
