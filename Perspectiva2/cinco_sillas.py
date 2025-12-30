import bpy
import math

# Limpiar la escena
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def unir_mesh(objetos, nombre):
    """Une objetos en un solo mesh"""
    if len(objetos) == 0:
        return None

    bpy.ops.object.select_all(action='DESELECT')
    for obj in objetos:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objetos[0]
    bpy.ops.object.join()
    bpy.context.active_object.name = nombre
    return bpy.context.active_object

# ============= SILLA 1: SIMPLE (4 patas) =============
print("Creando Silla Simple...")
parts = []
x_pos = -6

# Asiento
bpy.ops.mesh.primitive_cube_add(location=(x_pos, 0, 0.5), size=1)
bpy.context.object.scale = (0.5, 0.5, 0.1)
parts.append(bpy.context.object)

# Respaldo
bpy.ops.mesh.primitive_cube_add(location=(x_pos - 0.25, 0, 0.85), size=1)
bpy.context.object.scale = (0.05, 0.5, 0.35)
parts.append(bpy.context.object)

# 4 Patas
bpy.ops.mesh.primitive_cube_add(location=(x_pos + 0.2, 0.2, 0.25), size=1)
bpy.context.object.scale = (0.04, 0.04, 0.25)
parts.append(bpy.context.object)

bpy.ops.mesh.primitive_cube_add(location=(x_pos + 0.2, -0.2, 0.25), size=1)
bpy.context.object.scale = (0.04, 0.04, 0.25)
parts.append(bpy.context.object)

bpy.ops.mesh.primitive_cube_add(location=(x_pos - 0.2, 0.2, 0.25), size=1)
bpy.context.object.scale = (0.04, 0.04, 0.25)
parts.append(bpy.context.object)

bpy.ops.mesh.primitive_cube_add(location=(x_pos - 0.2, -0.2, 0.25), size=1)
bpy.context.object.scale = (0.04, 0.04, 0.25)
parts.append(bpy.context.object)

unir_mesh(parts, "Silla_Simple")

# ============= SILLA 2: MODERNA (pie central) =============
print("Creando Silla Moderna...")
parts = []
x_pos = -3

# Asiento
bpy.ops.mesh.primitive_cylinder_add(location=(x_pos, 0, 0.5), radius=0.3, depth=0.08)
parts.append(bpy.context.object)

# Respaldo
bpy.ops.mesh.primitive_cylinder_add(location=(x_pos - 0.28, 0, 0.8), radius=0.3, depth=0.08)
bpy.context.object.rotation_euler = (0, math.pi/2, 0)
parts.append(bpy.context.object)

# Poste central
bpy.ops.mesh.primitive_cylinder_add(location=(x_pos, 0, 0.25), radius=0.05, depth=0.5)
parts.append(bpy.context.object)

# Base - 5 brazos
for i in range(5):
    ang = math.radians(i * 72)
    x = x_pos + 0.25 * math.cos(ang)
    y = 0.25 * math.sin(ang)
    bpy.ops.mesh.primitive_cube_add(location=(x, y, 0.02), size=1)
    bpy.context.object.scale = (0.1, 0.05, 0.02)
    bpy.context.object.rotation_euler = (0, 0, ang)
    parts.append(bpy.context.object)

unir_mesh(parts, "Silla_Moderna")

# ============= SILLA 3: OFICINA (con ruedas) =============
print("Creando Silla Oficina...")
parts = []
x_pos = 0

# Asiento
bpy.ops.mesh.primitive_cylinder_add(location=(x_pos, 0, 0.5), radius=0.3, depth=0.1)
parts.append(bpy.context.object)

# Respaldo
bpy.ops.mesh.primitive_cube_add(location=(x_pos - 0.28, 0, 0.85), size=1)
bpy.context.object.scale = (0.05, 0.35, 0.45)
parts.append(bpy.context.object)

# Poste
bpy.ops.mesh.primitive_cylinder_add(location=(x_pos, 0, 0.25), radius=0.04, depth=0.4)
parts.append(bpy.context.object)

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
    bpy.context.object.scale = (0.18, 0.03, 0.02)
    bpy.context.object.rotation_euler = (0, 0, ang)
    parts.append(bpy.context.object)

    # Rueda
    bpy.ops.mesh.primitive_cylinder_add(location=(x, y, 0.03), radius=0.06, depth=0.04)
    bpy.context.object.rotation_euler = (math.pi/2, 0, 0)
    parts.append(bpy.context.object)

unir_mesh(parts, "Silla_Oficina")

# ============= SILLA 4: TABURETE (3 patas) =============
print("Creando Taburete...")
parts = []
x_pos = 3

# Asiento
bpy.ops.mesh.primitive_cylinder_add(location=(x_pos, 0, 0.6), radius=0.3, depth=0.08)
parts.append(bpy.context.object)

# 3 Patas
for i in range(3):
    ang = math.radians(i * 120)
    x = x_pos + 0.22 * math.cos(ang)
    y = 0.22 * math.sin(ang)
    bpy.ops.mesh.primitive_cylinder_add(location=(x, y, 0.28), radius=0.03, depth=0.56)
    parts.append(bpy.context.object)

# Aro de soporte
bpy.ops.mesh.primitive_torus_add(location=(x_pos, 0, 0.25), major_radius=0.22, minor_radius=0.025)
parts.append(bpy.context.object)

unir_mesh(parts, "Taburete")

# ============= SILLA 5: GAMING (estilo racing) =============
print("Creando Silla Gaming...")
parts = []
x_pos = 6

# Asiento
bpy.ops.mesh.primitive_cube_add(location=(x_pos, 0, 0.5), size=1)
bpy.context.object.scale = (0.5, 0.5, 0.08)
parts.append(bpy.context.object)

# Respaldo
bpy.ops.mesh.primitive_cube_add(location=(x_pos - 0.24, 0, 1.0), size=1)
bpy.context.object.scale = (0.06, 0.5, 0.6)
parts.append(bpy.context.object)

# Reposacabezas
bpy.ops.mesh.primitive_cube_add(location=(x_pos - 0.26, 0, 1.55), size=1)
bpy.context.object.scale = (0.05, 0.3, 0.12)
parts.append(bpy.context.object)

# Reposabrazos izquierdo
bpy.ops.mesh.primitive_cube_add(location=(x_pos - 0.05, -0.3, 0.6), size=1)
bpy.context.object.scale = (0.3, 0.06, 0.04)
parts.append(bpy.context.object)

# Reposabrazos derecho
bpy.ops.mesh.primitive_cube_add(location=(x_pos - 0.05, 0.3, 0.6), size=1)
bpy.context.object.scale = (0.3, 0.06, 0.04)
parts.append(bpy.context.object)

# Poste
bpy.ops.mesh.primitive_cylinder_add(location=(x_pos, 0, 0.25), radius=0.05, depth=0.4)
parts.append(bpy.context.object)

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
    bpy.context.object.scale = (0.2, 0.05, 0.03)
    bpy.context.object.rotation_euler = (0, 0, ang)
    parts.append(bpy.context.object)

    # Rueda
    bpy.ops.mesh.primitive_cylinder_add(location=(x, y, 0.03), radius=0.07, depth=0.05)
    bpy.context.object.rotation_euler = (math.pi/2, 0, 0)
    parts.append(bpy.context.object)

unir_mesh(parts, "Silla_Gaming")

print("¡Listo! 5 sillas creadas:")
print("1. Silla Simple (4 patas)")
print("2. Silla Moderna (pie central)")
print("3. Silla Oficina (con ruedas)")
print("4. Taburete (3 patas)")
print("5. Silla Gaming (estilo racing)")
