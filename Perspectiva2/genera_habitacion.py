"""
Script para generar habitaciones con parámetros configurables.
Lee parámetros de un archivo JSON y genera una imagen.
"""
import bpy
import math
import json
import sys
from pathlib import Path


# Leer parámetros del archivo JSON
params_file = Path(__file__).parent / "room_params.json"
if params_file.exists():
    with open(params_file, 'r') as f:
        params = json.load(f)
else:
    # Parámetros por defecto
    params = {
        "room_width": 4.0,
        "room_depth": 4.0,
        "room_height": 2.5,
        "cam_x_ratio": 0.3,
        "cam_y_ratio": 0.3,
        "cam_z_ratio": 0.5,
        "target_x_ratio": 0.7,
        "target_y_ratio": 0.7,
        "target_z_ratio": 0.5,
        "fov": 70,
        "bg_strength": 0.8,
        "light_energy": 300
    }


def clear_scene():
    """Limpia la escena."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)


def create_room(width, depth, height):
    """Crea una habitación."""

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
    wall = bpy.context.object
    wall.name = "Wall_Front"
    wall.scale = (width/2, 1, height/2)
    wall.rotation_euler = (math.radians(90), 0, 0)

    # Pared trasera (Y=depth)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(width/2, depth, height/2))
    wall = bpy.context.object
    wall.name = "Wall_Back"
    wall.scale = (width/2, 1, height/2)
    wall.rotation_euler = (math.radians(90), 0, 0)

    # Pared izquierda (X=0)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, depth/2, height/2))
    wall = bpy.context.object
    wall.name = "Wall_Left"
    wall.scale = (1, depth/2, height/2)
    wall.rotation_euler = (math.radians(90), 0, math.radians(90))

    # Pared derecha (X=width)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(width, depth/2, height/2))
    wall = bpy.context.object
    wall.name = "Wall_Right"
    wall.scale = (1, depth/2, height/2)
    wall.rotation_euler = (math.radians(90), 0, math.radians(90))


def create_material(name, color):
    """Crea un material."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")

    if bsdf:
        bsdf.inputs['Base Color'].default_value = (*color, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.8

    return mat


def apply_materials():
    """Aplica materiales."""
    # Paredes grises
    wall_mat = create_material("WallMaterial", (0.85, 0.85, 0.85))
    for obj in bpy.data.objects:
        if "Wall" in obj.name:
            obj.data.materials.clear()
            obj.data.materials.append(wall_mat)

    # Suelo marrón
    floor_mat = create_material("FloorMaterial", (0.5, 0.4, 0.3))
    if "Floor" in bpy.data.objects:
        bpy.data.objects["Floor"].data.materials.clear()
        bpy.data.objects["Floor"].data.materials.append(floor_mat)

    # Techo blanco
    ceiling_mat = create_material("CeilingMaterial", (0.95, 0.95, 0.95))
    if "Ceiling" in bpy.data.objects:
        bpy.data.objects["Ceiling"].data.materials.clear()
        bpy.data.objects["Ceiling"].data.materials.append(ceiling_mat)


def setup_camera(width, depth, height, cam_x_ratio, cam_y_ratio, cam_z_ratio,
                 target_x_ratio, target_y_ratio, target_z_ratio, fov):
    """Configura la cámara."""

    # Posición de cámara
    cam_x = width * cam_x_ratio
    cam_y = depth * cam_y_ratio
    cam_z = height * cam_z_ratio

    # Punto objetivo
    target_x = width * target_x_ratio
    target_y = depth * target_y_ratio
    target_z = height * target_z_ratio

    # Crear cámara
    bpy.ops.object.camera_add(location=(cam_x, cam_y, cam_z))
    camera = bpy.context.object
    camera.name = "Camera"

    # Crear target
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(target_x, target_y, target_z))
    target = bpy.context.object

    # Orientar cámara
    constraint = camera.constraints.new(type='TRACK_TO')
    constraint.target = target
    constraint.track_axis = 'TRACK_NEGATIVE_Z'
    constraint.up_axis = 'UP_Y'

    bpy.context.view_layer.update()

    # Eliminar constraint y target
    camera.constraints.remove(constraint)
    bpy.data.objects.remove(target, do_unlink=True)

    # Configurar FOV
    camera.data.lens_unit = 'FOV'
    camera.data.angle = math.radians(fov)

    # Activar cámara
    bpy.context.scene.camera = camera


def setup_lighting(width, depth, height, bg_strength, light_energy):
    """Configura iluminación."""

    # Luz ambiente
    world = bpy.context.scene.world
    world.use_nodes = True
    bg = world.node_tree.nodes['Background']
    bg.inputs['Strength'].default_value = bg_strength
    bg.inputs['Color'].default_value = (1.0, 1.0, 1.0, 1.0)

    # Luz principal
    bpy.ops.object.light_add(type='AREA', location=(width/2, depth/2, height - 0.3))
    light = bpy.context.object
    light.name = "MainLight"
    light.data.energy = light_energy
    light.data.size = 2.0


def setup_render():
    """Configura render."""
    scene = bpy.context.scene

    scene.render.image_settings.file_format = 'PNG'
    scene.render.resolution_x = 512
    scene.render.resolution_y = 512
    scene.render.resolution_percentage = 100

    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 32  # Reducido para rapidez
    scene.cycles.use_denoising = True


def render_image(output_path):
    """Renderiza la imagen."""
    scene = bpy.context.scene
    scene.render.filepath = str(output_path)
    bpy.ops.render.render(write_still=True)


def main():
    """Función principal."""

    clear_scene()

    # Extraer parámetros
    width = params["room_width"]
    depth = params["room_depth"]
    height = params["room_height"]

    create_room(width, depth, height)
    apply_materials()
    setup_camera(
        width, depth, height,
        params["cam_x_ratio"],
        params["cam_y_ratio"],
        params["cam_z_ratio"],
        params["target_x_ratio"],
        params["target_y_ratio"],
        params["target_z_ratio"],
        params["fov"]
    )
    setup_lighting(width, depth, height, params["bg_strength"], params["light_energy"])
    setup_render()

    output_path = Path(__file__).parent / "output.png"
    render_image(output_path)

    print(f"✓ Imagen renderizada: {output_path}")


if __name__ == "__main__":
    main()
