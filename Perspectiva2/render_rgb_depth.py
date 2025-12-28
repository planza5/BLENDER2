"""
Script simple para generar imágenes RGB y Depth de una habitación.

Uso:
    blender --background --python render_rgb_depth.py

    O con una escena existente:
    blender --background tu_escena.blend --python render_rgb_depth.py
"""
import bpy
import math
import random
from pathlib import Path


# ============================================================================
# CONFIGURACIÓN
# ============================================================================

OUTPUT_DIR = Path(__file__).parent / "output"
IMAGE_WIDTH = 1024
IMAGE_HEIGHT = 1024

# Dimensiones de la habitación (metros)
ROOM_WIDTH = 4.0
ROOM_DEPTH = 4.0
ROOM_HEIGHT = 2.5

# Configuración de renderizado
RENDER_ENGINE = "CYCLES"
SAMPLES = 64


# ============================================================================
# FUNCIONES
# ============================================================================

def clear_scene():
    """Limpia toda la escena."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Limpiar datos huérfanos
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)


def create_room(width, depth, height):
    """Crea una habitación simple con paredes, suelo y techo."""

    # Suelo
    bpy.ops.mesh.primitive_plane_add(size=1, location=(width/2, depth/2, 0))
    floor = bpy.context.object
    floor.name = "Floor"
    floor.scale = (width/2, depth/2, 1)

    # Techo
    bpy.ops.mesh.primitive_plane_add(size=1, location=(width/2, depth/2, height))
    ceiling = bpy.context.object
    ceiling.name = "Ceiling"
    ceiling.scale = (width/2, depth/2, 1)

    # Pared frontal (Y=0)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(width/2, 0, height/2))
    wall_front = bpy.context.object
    wall_front.name = "Wall_Front"
    wall_front.scale = (width/2, 1, height/2)
    wall_front.rotation_euler = (math.radians(90), 0, 0)

    # Pared trasera (Y=depth)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(width/2, depth, height/2))
    wall_back = bpy.context.object
    wall_back.name = "Wall_Back"
    wall_back.scale = (width/2, 1, height/2)
    wall_back.rotation_euler = (math.radians(90), 0, 0)

    # Pared izquierda (X=0)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, depth/2, height/2))
    wall_left = bpy.context.object
    wall_left.name = "Wall_Left"
    wall_left.scale = (1, depth/2, height/2)
    wall_left.rotation_euler = (math.radians(90), 0, math.radians(90))

    # Pared derecha (X=width)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(width, depth/2, height/2))
    wall_right = bpy.context.object
    wall_right.name = "Wall_Right"
    wall_right.scale = (1, depth/2, height/2)
    wall_right.rotation_euler = (math.radians(90), 0, math.radians(90))

    print(f"✓ Habitación creada: {width}x{depth}x{height}m")


def create_simple_material(name, color):
    """Crea un material simple con color."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")

    if bsdf:
        bsdf.inputs['Base Color'].default_value = (*color, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.8

    return mat


def apply_materials():
    """Aplica materiales a los objetos de la escena."""

    # Material para paredes (blanco)
    wall_mat = create_simple_material("WallMaterial", (0.9, 0.9, 0.9))
    for obj in bpy.data.objects:
        if "Wall" in obj.name:
            obj.data.materials.clear()
            obj.data.materials.append(wall_mat)

    # Material para suelo (madera)
    floor_mat = create_simple_material("FloorMaterial", (0.5, 0.4, 0.3))
    if "Floor" in bpy.data.objects:
        bpy.data.objects["Floor"].data.materials.clear()
        bpy.data.objects["Floor"].data.materials.append(floor_mat)

    # Material para techo (blanco)
    ceiling_mat = create_simple_material("CeilingMaterial", (0.95, 0.95, 0.95))
    if "Ceiling" in bpy.data.objects:
        bpy.data.objects["Ceiling"].data.materials.clear()
        bpy.data.objects["Ceiling"].data.materials.append(ceiling_mat)

    print("✓ Materiales aplicados")


def setup_camera(width, depth, height):
    """Configura la cámara en una esquina mirando al centro."""

    # Posición en esquina
    cam_x = width * 0.2
    cam_y = depth * 0.2
    cam_z = height * 0.6

    # Crear cámara
    bpy.ops.object.camera_add(location=(cam_x, cam_y, cam_z))
    camera = bpy.context.object
    camera.name = "Camera"

    # Apuntar hacia el centro opuesto
    target_x = width * 0.8
    target_y = depth * 0.8
    target_z = cam_z

    # Crear punto de referencia temporal
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(target_x, target_y, target_z))
    target = bpy.context.object

    # Orientar cámara hacia el punto
    constraint = camera.constraints.new(type='TRACK_TO')
    constraint.target = target
    constraint.track_axis = 'TRACK_NEGATIVE_Z'
    constraint.up_axis = 'UP_Y'

    bpy.context.view_layer.update()

    # Eliminar constraint y punto de referencia
    camera.constraints.remove(constraint)
    bpy.data.objects.remove(target, do_unlink=True)

    # Configurar FOV
    camera.data.lens_unit = 'FOV'
    camera.data.angle = math.radians(70)

    # Activar cámara
    bpy.context.scene.camera = camera

    print(f"✓ Cámara configurada en ({cam_x:.2f}, {cam_y:.2f}, {cam_z:.2f})")


def setup_lighting(width, depth, height):
    """Configura iluminación básica."""

    # Luz ambiente
    world = bpy.context.scene.world
    world.use_nodes = True
    bg = world.node_tree.nodes['Background']
    bg.inputs['Strength'].default_value = 1.2
    bg.inputs['Color'].default_value = (1.0, 1.0, 1.0, 1.0)

    # Luz principal cenital
    bpy.ops.object.light_add(type='AREA', location=(width/2, depth/2, height - 0.3))
    light = bpy.context.object
    light.name = "MainLight"
    light.data.energy = 400
    light.data.size = 2.0

    print("✓ Iluminación configurada")


def setup_render():
    """Configura los ajustes de renderizado."""
    scene = bpy.context.scene

    # Resolución
    scene.render.image_settings.file_format = 'PNG'
    scene.render.resolution_x = IMAGE_WIDTH
    scene.render.resolution_y = IMAGE_HEIGHT
    scene.render.resolution_percentage = 100

    # Engine
    scene.render.engine = RENDER_ENGINE

    if RENDER_ENGINE == 'CYCLES':
        scene.cycles.samples = SAMPLES
        scene.cycles.use_denoising = True

        # Habilitar pass de depth
        scene.view_layers[0].use_pass_z = True

    print(f"✓ Render configurado: {IMAGE_WIDTH}x{IMAGE_HEIGHT}, {SAMPLES} samples")


def render_rgb_and_depth(output_dir):
    """Renderiza y guarda RGB y Depth."""

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    scene = bpy.context.scene

    # Configurar compositor
    scene.use_nodes = True
    tree = scene.node_tree
    tree.nodes.clear()

    # Nodo de render layers
    rl = tree.nodes.new('CompositorNodeRLayers')
    rl.location = (0, 0)

    print("\nRenderizando...")

    # === RENDER RGB ===
    print("  Renderizando RGB...")
    rgb_output = tree.nodes.new('CompositorNodeOutputFile')
    rgb_output.location = (400, 200)
    rgb_output.base_path = str(output_path)
    rgb_output.file_slots[0].path = "rgb"
    tree.links.new(rl.outputs['Image'], rgb_output.inputs[0])

    bpy.ops.render.render(write_still=False)

    # Renombrar archivo
    rgb_file = output_path / "rgb0001.png"
    if rgb_file.exists():
        rgb_final = output_path / "rgb.png"
        rgb_file.replace(rgb_final)
        print(f"  ✓ RGB guardado: {rgb_final}")

    tree.nodes.remove(rgb_output)

    # === RENDER DEPTH ===
    print("  Renderizando Depth...")
    depth_output = tree.nodes.new('CompositorNodeOutputFile')
    depth_output.location = (400, -200)
    depth_output.base_path = str(output_path)
    depth_output.file_slots[0].path = "depth"
    depth_output.format.color_mode = 'BW'
    depth_output.format.color_depth = '16'

    # Normalizar depth
    normalize = tree.nodes.new('CompositorNodeNormalize')
    normalize.location = (200, -200)
    tree.links.new(rl.outputs['Depth'], normalize.inputs[0])
    tree.links.new(normalize.outputs[0], depth_output.inputs[0])

    bpy.ops.render.render(write_still=False)

    # Renombrar archivo
    depth_file = output_path / "depth0001.png"
    if depth_file.exists():
        depth_final = output_path / "depth.png"
        depth_file.replace(depth_final)
        print(f"  ✓ Depth guardado: {depth_final}")

    tree.nodes.remove(depth_output)
    tree.nodes.remove(normalize)

    print(f"\n✓ Renderizado completo! Archivos en: {output_path}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Función principal."""

    print("\n" + "="*60)
    print("RENDER RGB + DEPTH")
    print("="*60 + "\n")

    # Siempre limpiar y crear escena nueva
    print("Creando habitación...")
    clear_scene()
    create_room(ROOM_WIDTH, ROOM_DEPTH, ROOM_HEIGHT)
    apply_materials()
    setup_camera(ROOM_WIDTH, ROOM_DEPTH, ROOM_HEIGHT)
    setup_lighting(ROOM_WIDTH, ROOM_DEPTH, ROOM_HEIGHT)

    setup_render()
    render_rgb_and_depth(OUTPUT_DIR)

    print("\n" + "="*60)
    print("COMPLETADO!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
