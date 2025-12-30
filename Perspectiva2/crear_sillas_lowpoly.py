import bpy
import math

# Limpiar la escena
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# ============= SILLA 1: SIMPLE (4 patas) =============
print("Creando Silla Simple...")
meshes = []
x_pos = -6

# Asiento
bpy.ops.mesh.primitive_cube_add(location=(x_pos, 0, 0.5), size=1)
obj = bpy.context.active_object
obj.scale = (0.5, 0.5, 0.1)
meshes.append(obj)

# Respaldo
bpy.ops.mesh.primitive_cube_add(location=(x_pos - 0.25, 0, 0.85), size=1)
obj = bpy.context.active_object
obj.scale = (0.05, 0.5, 0.35)
meshes.append(obj)

# Pata 1
bpy.ops.mesh.primitive_cube_add(location=(x_pos + 0.2, 0.2, 0.25), size=1)
obj = bpy.context.active_object
obj.scale = (0.04, 0.04, 0.25)
meshes.append(obj)

# Pata 2
bpy.ops.mesh.primitive_cube_add(location=(x_pos + 0.2, -0.2, 0.25), size=1)
obj = bpy.context.active_object
obj.scale = (0.04, 0.04, 0.25)
meshes.append(obj)

# Pata 3
bpy.ops.mesh.primitive_cube_add(location=(x_pos - 0.2, 0.2, 0.25), size=1)
obj = bpy.context.active_object
obj.scale = (0.04, 0.04, 0.25)
meshes.append(obj)

# Pata 4
bpy.ops.mesh.primitive_cube_add(location=(x_pos - 0.2, -0.2, 0.25), size=1)
obj = bpy.context.active_object
obj.scale = (0.04, 0.04, 0.25)
meshes.append(obj)

# Unir
bpy.ops.object.select_all(action='DESELECT')
for m in meshes:
    m.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
bpy.ops.object.join()
bpy.context.active_object.name = "Silla_Simple"

# ============= SILLA 2: MODERNA =============
print("Creando Silla Moderna...")
meshes = []
x_pos = -3

# Asiento
bpy.ops.mesh.primitive_cylinder_add(location=(x_pos, 0, 0.5), radius=0.3, depth=0.08)
obj = bpy.context.active_object
meshes.append(obj)

# Respaldo
bpy.ops.mesh.primitive_cylinder_add(location=(x_pos - 0.28, 0, 0.8), radius=0.3, depth=0.08)
obj = bpy.context.active_object
obj.rotation_euler = (0, math.pi/2, 0)
meshes.append(obj)

# Poste central
bpy.ops.mesh.primitive_cylinder_add(location=(x_pos, 0, 0.25), radius=0.05, depth=0.5)
obj = bpy.context.active_object
meshes.append(obj)

# Base - 5 brazos
for i in range(5):
    ang = math.radians(i * 72)
    x = x_pos + 0.25 * math.cos(ang)
    y = 0.25 * math.sin(ang)
    bpy.ops.mesh.primitive_cube_add(location=(x, y, 0.02), size=1)
    obj = bpy.context.active_object
    obj.scale = (0.1, 0.05, 0.02)
    obj.rotation_euler = (0, 0, ang)
    meshes.append(obj)

# Unir
bpy.ops.object.select_all(action='DESELECT')
for m in meshes:
    m.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
bpy.ops.object.join()
bpy.context.active_object.name = "Silla_Moderna"

# ============= SILLA 3: OFICINA =============
print("Creando Silla Oficina...")
meshes = []
x_pos = 0

# Asiento
bpy.ops.mesh.primitive_cylinder_add(location=(x_pos, 0, 0.5), radius=0.3, depth=0.1)
obj = bpy.context.active_object
meshes.append(obj)

# Respaldo
bpy.ops.mesh.primitive_cube_add(location=(x_pos - 0.28, 0, 0.85), size=1)
obj = bpy.context.active_object
obj.scale = (0.05, 0.35, 0.45)
meshes.append(obj)

# Poste
bpy.ops.mesh.primitive_cylinder_add(location=(x_pos, 0, 0.25), radius=0.04, depth=0.4)
obj = bpy.context.active_object
meshes.append(obj)

# Base con 5 ruedas
for i in range(5):
    ang = math.radians(i * 72)
    dist = 0.35
    x = x_pos + dist * math.cos(ang)
    y = dist * math.sin(ang)

    # Brazo
    bx = x_pos + (dist/2) * math.cos(ang)
    by = (dist/2) * math.sin(ang)
    bpy.ops.mesh.primitive_cube_add(location=(bx, by, 0.03), size=1)
    obj = bpy.context.active_object
    obj.scale = (0.18, 0.03, 0.02)
    obj.rotation_euler = (0, 0, ang)
    meshes.append(obj)

    # Rueda
    bpy.ops.mesh.primitive_cylinder_add(location=(x, y, 0.03), radius=0.06, depth=0.04)
    obj = bpy.context.active_object
    obj.rotation_euler = (math.pi/2, 0, 0)
    meshes.append(obj)

# Unir
bpy.ops.object.select_all(action='DESELECT')
for m in meshes:
    m.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
bpy.ops.object.join()
bpy.context.active_object.name = "Silla_Oficina"

# ============= SILLA 4: TABURETE =============
print("Creando Taburete...")
meshes = []
x_pos = 3

# Asiento
bpy.ops.mesh.primitive_cylinder_add(location=(x_pos, 0, 0.6), radius=0.3, depth=0.08)
obj = bpy.context.active_object
meshes.append(obj)

# 3 Patas
for i in range(3):
    ang = math.radians(i * 120)
    x = x_pos + 0.22 * math.cos(ang)
    y = 0.22 * math.sin(ang)
    bpy.ops.mesh.primitive_cylinder_add(location=(x, y, 0.28), radius=0.03, depth=0.56)
    obj = bpy.context.active_object
    meshes.append(obj)

# Aro de soporte
bpy.ops.mesh.primitive_torus_add(location=(x_pos, 0, 0.25), major_radius=0.22, minor_radius=0.025)
obj = bpy.context.active_object
meshes.append(obj)

# Unir
bpy.ops.object.select_all(action='DESELECT')
for m in meshes:
    m.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
bpy.ops.object.join()
bpy.context.active_object.name = "Taburete"

# ============= SILLA 5: GAMING =============
print("Creando Silla Gaming...")
meshes = []
x_pos = 6

# Asiento
bpy.ops.mesh.primitive_cube_add(location=(x_pos, 0, 0.5), size=1)
obj = bpy.context.active_object
obj.scale = (0.5, 0.5, 0.08)
meshes.append(obj)

# Respaldo
bpy.ops.mesh.primitive_cube_add(location=(x_pos - 0.24, 0, 1.0), size=1)
obj = bpy.context.active_object
obj.scale = (0.06, 0.5, 0.6)
meshes.append(obj)

# Reposacabezas
bpy.ops.mesh.primitive_cube_add(location=(x_pos - 0.26, 0, 1.55), size=1)
obj = bpy.context.active_object
obj.scale = (0.05, 0.3, 0.12)
meshes.append(obj)

# Reposabrazos izquierdo
bpy.ops.mesh.primitive_cube_add(location=(x_pos - 0.05, -0.3, 0.6), size=1)
obj = bpy.context.active_object
obj.scale = (0.3, 0.06, 0.04)
meshes.append(obj)

# Reposabrazos derecho
bpy.ops.mesh.primitive_cube_add(location=(x_pos - 0.05, 0.3, 0.6), size=1)
obj = bpy.context.active_object
obj.scale = (0.3, 0.06, 0.04)
meshes.append(obj)

# Poste
bpy.ops.mesh.primitive_cylinder_add(location=(x_pos, 0, 0.25), radius=0.05, depth=0.4)
obj = bpy.context.active_object
meshes.append(obj)

# Base con 5 ruedas
for i in range(5):
    ang = math.radians(i * 72)
    dist = 0.4
    x = x_pos + dist * math.cos(ang)
    y = dist * math.sin(ang)

    # Brazo
    bx = x_pos + (dist/2) * math.cos(ang)
    by = (dist/2) * math.sin(ang)
    bpy.ops.mesh.primitive_cube_add(location=(bx, by, 0.03), size=1)
    obj = bpy.context.active_object
    obj.scale = (0.2, 0.05, 0.03)
    obj.rotation_euler = (0, 0, ang)
    meshes.append(obj)

    # Rueda
    bpy.ops.mesh.primitive_cylinder_add(location=(x, y, 0.03), radius=0.07, depth=0.05)
    obj = bpy.context.active_object
    obj.rotation_euler = (math.pi/2, 0, 0)
    meshes.append(obj)

# Unir
bpy.ops.object.select_all(action='DESELECT')
for m in meshes:
    m.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
bpy.ops.object.join()
bpy.context.active_object.name = "Silla_Gaming"

print("=" * 50)
print("¡COMPLETADO!")
print("5 sillas lowpoly creadas:")
print("1. Silla_Simple - 4 patas clásica")
print("2. Silla_Moderna - pie central con base estrella")
print("3. Silla_Oficina - con 5 ruedas")
print("4. Taburete - 3 patas con aro")
print("5. Silla_Gaming - estilo racing con reposabrazos")
print("=" * 50)

# Guardar archivo
import os
filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cinco_sillas.blend")
bpy.ops.wm.save_as_mainfile(filepath=filepath)
print(f"Archivo guardado en: {filepath}")
