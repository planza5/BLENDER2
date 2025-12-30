"""
Marcas de Llana Circulares - Enfoque Realista
==============================================
Ejecutar: blender --background --python test_circular_trowel_marks.py

Simula marcas de llana REALES:
- Medios círculos/arcos (no líneas)
- Muy sutiles (apenas visibles)
- Pocas y aisladas (3-4 por superficie)
- NO continuas (toques localizados)
"""

import bpy
import math
import random
from pathlib import Path
import os

# Configuración
OUTPUT_DIR = Path(os.path.dirname(os.path.abspath(__file__))) / "test_output"
RESOLUTION = 768
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
    camera.data.ortho_scale = 2.2
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
    scene.render.resolution_x = RESOLUTION
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
# CAPA BASE
# =============================================================================
def create_base_layer(nodes, links, mapping):
    """Crea la capa base de microcemento."""

    # Noise base
    noise_base = nodes.new('ShaderNodeTexNoise')
    noise_base.location = (-700, 200)
    noise_base.name = "NoiseBase"
    noise_base.inputs['Scale'].default_value = 8.0
    noise_base.inputs['Detail'].default_value = 5.0
    noise_base.inputs['Roughness'].default_value = 0.5
    links.new(mapping.outputs['Vector'], noise_base.inputs['Vector'])

    # Voronoi para manchas sutiles
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
# MARCAS CIRCULARES DE LLANA
# =============================================================================
def create_circular_trowel_marks(nodes, links, mapping):
    """Crea marcas circulares/arcos de llana."""

    # Wave en modo RINGS para crear círculos concéntricos
    wave_rings = nodes.new('ShaderNodeTexWave')
    wave_rings.location = (-700, -400)
    wave_rings.name = "WaveRings"
    wave_rings.wave_type = 'RINGS'
    wave_rings.rings_direction = 'SPHERICAL'
    wave_rings.wave_profile = 'SIN'
    wave_rings.inputs['Scale'].default_value = 2.5  # Tamaño de los círculos
    wave_rings.inputs['Distortion'].default_value = 1.5  # Irregularidad
    wave_rings.inputs['Detail'].default_value = 2.0
    links.new(mapping.outputs['Vector'], wave_rings.inputs['Vector'])

    # Gradient radial para crear el efecto de "medio círculo"
    gradient = nodes.new('ShaderNodeTexGradient')
    gradient.location = (-700, -600)
    gradient.name = "GradientRadial"
    gradient.gradient_type = 'RADIAL'
    links.new(mapping.outputs['Vector'], gradient.inputs['Vector'])

    # Math para crear máscara de medio círculo (solo parte de los anillos)
    math_power = nodes.new('ShaderNodeMath')
    math_power.location = (-500, -600)
    math_power.operation = 'POWER'
    math_power.inputs[1].default_value = 3.0  # Suavidad del borde
    links.new(gradient.outputs['Fac'], math_power.inputs[0])

    # Multiply: combinar anillos con máscara radial
    mix_multiply = nodes.new('ShaderNodeMixRGB')
    mix_multiply.location = (-500, -400)
    mix_multiply.blend_type = 'MULTIPLY'
    mix_multiply.inputs['Fac'].default_value = 1.0
    links.new(wave_rings.outputs['Fac'], mix_multiply.inputs['Color1'])
    links.new(math_power.outputs['Value'], mix_multiply.inputs['Color2'])

    # ColorRamp para ajustar sutileza (MUY suave)
    ramp_trowel = nodes.new('ShaderNodeValToRGB')
    ramp_trowel.location = (-300, -400)
    ramp_trowel.name = "RampTrowel"
    # Ajustar para marcas MUY sutiles
    ramp_trowel.color_ramp.elements[0].position = 0.45  # Casi todo igual
    ramp_trowel.color_ramp.elements[1].position = 0.55  # Muy poco contraste
    ramp_trowel.color_ramp.interpolation = 'EASE'  # Transición muy suave
    links.new(mix_multiply.outputs['Color'], ramp_trowel.inputs['Fac'])

    return ramp_trowel.outputs['Color']


# =============================================================================
# MÁSCARA LOCALIZADA (solo 3-4 marcas)
# =============================================================================
def create_sparse_mask(nodes, links, mapping):
    """Crea máscara muy restrictiva - solo 3-4 zonas aisladas."""

    # Voronoi con MUY poca escala (celdas grandes = pocas zonas)
    voronoi_sparse = nodes.new('ShaderNodeTexVoronoi')
    voronoi_sparse.location = (-850, -800)
    voronoi_sparse.name = "VoronoiSparse"
    voronoi_sparse.feature = 'DISTANCE_TO_EDGE'
    voronoi_sparse.inputs['Scale'].default_value = 1.2  # MUY BAJO = pocas celdas
    voronoi_sparse.inputs['Randomness'].default_value = 1.0
    links.new(mapping.outputs['Vector'], voronoi_sparse.inputs['Vector'])

    # ColorRamp MUY restrictivo (solo ~10-15% de superficie)
    ramp_mask = nodes.new('ShaderNodeValToRGB')
    ramp_mask.location = (-650, -800)
    ramp_mask.name = "MaskRamp"
    # Solo las zonas más cercanas al borde de celda
    ramp_mask.color_ramp.elements[0].position = 0.0
    ramp_mask.color_ramp.elements[0].color = (0, 0, 0, 1)  # Negro (sin marca)
    ramp_mask.color_ramp.elements[1].position = 0.15  # Solo 15% tiene marca
    ramp_mask.color_ramp.elements[1].color = (1, 1, 1, 1)  # Blanco (con marca)
    ramp_mask.color_ramp.interpolation = 'EASE'
    links.new(voronoi_sparse.outputs['Distance'], ramp_mask.inputs['Fac'])

    # Noise adicional para romper uniformidad
    noise_break = nodes.new('ShaderNodeTexNoise')
    noise_break.location = (-850, -1000)
    noise_break.inputs['Scale'].default_value = 5.0
    links.new(mapping.outputs['Vector'], noise_break.inputs['Vector'])

    # Multiply: máscara * noise para más aleatoriedad
    mix_mask = nodes.new('ShaderNodeMixRGB')
    mix_mask.location = (-450, -900)
    mix_mask.blend_type = 'MULTIPLY'
    mix_mask.inputs['Fac'].default_value = 1.0
    links.new(ramp_mask.outputs['Color'], mix_mask.inputs['Color1'])
    links.new(noise_break.outputs['Fac'], mix_mask.inputs['Color2'])

    # ColorRamp final para controlar cantidad exacta
    ramp_final = nodes.new('ShaderNodeValToRGB')
    ramp_final.location = (-250, -900)
    ramp_final.color_ramp.elements[0].position = 0.6  # Muy restrictivo
    ramp_final.color_ramp.elements[1].position = 0.8
    links.new(mix_mask.outputs['Color'], ramp_final.inputs['Fac'])

    return ramp_final.outputs['Color']


# =============================================================================
# MATERIAL COMPLETO
# =============================================================================
def create_realistic_trowel_material():
    """Material completo con marcas circulares sutiles y localizadas."""
    mat = bpy.data.materials.new(name="Realistic_Circular_Trowel")
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

    # Marcas circulares
    trowel_output = create_circular_trowel_marks(nodes, links, mapping)

    # Máscara localizada
    mask_output = create_sparse_mask(nodes, links, mapping)

    # Mix con máscara (MUY SUTIL)
    mix_final = nodes.new('ShaderNodeMixRGB')
    mix_final.location = (-100, 0)
    mix_final.name = "MixFinal"
    mix_final.blend_type = 'OVERLAY'
    links.new(mask_output, mix_final.inputs['Fac'])
    links.new(base_output, mix_final.inputs['Color1'])
    links.new(trowel_output, mix_final.inputs['Color2'])

    # ColorRamp final para colores
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (200, 0)
    ramp.color_ramp.elements[0].color = (0.65, 0.65, 0.60, 1.0)
    ramp.color_ramp.elements[1].color = (0.88, 0.88, 0.85, 1.0)
    links.new(mix_final.outputs['Color'], ramp.inputs['Fac'])

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
# VARIANTES PARA COMPARAR
# =============================================================================
def create_comparison_materials():
    """Crea 3 variantes para comparar intensidad de marcas."""

    # Base: sin marcas
    mat_base = bpy.data.materials.new(name="1_Base_NoMarks")
    mat_base.use_nodes = True
    mat_base.node_tree.nodes.clear()
    nodes = mat_base.node_tree.nodes
    links = mat_base.node_tree.links

    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-1200, 0)
    mapping = nodes.new('ShaderNodeMapping')
    mapping.location = (-1000, 0)
    links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])

    base_output = create_base_layer(nodes, links, mapping)

    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (200, 0)
    ramp.color_ramp.elements[0].color = (0.65, 0.65, 0.60, 1.0)
    ramp.color_ramp.elements[1].color = (0.88, 0.88, 0.85, 1.0)
    links.new(base_output, ramp.inputs['Fac'])

    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (500, 0)
    bsdf.inputs['Roughness'].default_value = 0.4
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (750, 0)
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    # Variantes con marcas
    mat_subtle = create_realistic_trowel_material()
    mat_subtle.name = "2_Subtle_Marks"

    return [mat_base, mat_subtle]


# =============================================================================
# SETUP DE ESCENA
# =============================================================================
def create_comparison_scene():
    """Crea escena con plano grande para ver las marcas localizadas."""
    clear_scene()
    configure_render()
    setup_camera_and_lights()

    # Un solo plano grande con el material realista
    mat = create_realistic_trowel_material()

    bpy.ops.mesh.primitive_plane_add(size=2, location=(0, 0, 0))
    plane = bpy.context.active_object
    plane.name = "TrowelMarks_Plane"
    plane.data.materials.append(mat)

    print(f"  Material: {mat.name}")
    return plane


# =============================================================================
# RENDER
# =============================================================================
def render_comparison():
    """Renderiza muestra realista."""
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("\n" + "="*60)
    print("TEST: Marcas Circulares de Llana (Realista)")
    print("="*60)

    create_comparison_scene()

    # Render
    output_path = OUTPUT_DIR / "circular_trowel_marks.png"
    bpy.context.scene.render.filepath = str(output_path)

    print(f"\nRenderizando...")
    print(f"Output: {output_path}")
    print(f"\nCaracterísticas:")
    print("  - Marcas en MEDIOS CÍRCULOS/ARCOS")
    print("  - MUY SUTILES (apenas visibles)")
    print("  - POCAS y AISLADAS (~3-4 zonas)")
    print("  - NO continuas (localizadas)")

    bpy.ops.render.render(write_still=True)

    print(f"\n✓ Render completado: {output_path}")


# =============================================================================
# MAIN
# =============================================================================
if __name__ == "__main__":
    render_comparison()
else:
    render_comparison()
