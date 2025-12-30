import bpy
import bmesh
import math

def limpiar_escena():
    """Elimina todos los objetos de la escena."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.curves:
        if block.users == 0:
            bpy.data.curves.remove(block)

def preparar_objeto(obj):
    """Aplica transformaciones, recalcula normales y centra origen."""
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')

def crear_tubo_hueco_hex(radio_int, radio_ext, altura, num_lados_int=6, num_lados_ext=32):
    """
    Crea un tubo con hueco interior (hexagonal o circular).
    Construye la geometría explícitamente: tapa inferior, paredes, tapa superior.
    """
    bm = bmesh.new()
    
    # === VERTICES ===
    # Anillo interior inferior (z=0)
    verts_int_bot = []
    for i in range(num_lados_int):
        angulo = math.radians(360 * i / num_lados_int + 30)  # +30 para cara plana arriba
        x = radio_int * math.cos(angulo)
        y = radio_int * math.sin(angulo)
        verts_int_bot.append(bm.verts.new((x, y, 0)))
    
    # Anillo exterior inferior (z=0)
    verts_ext_bot = []
    for i in range(num_lados_ext):
        angulo = math.radians(360 * i / num_lados_ext)
        x = radio_ext * math.cos(angulo)
        y = radio_ext * math.sin(angulo)
        verts_ext_bot.append(bm.verts.new((x, y, 0)))
    
    # Anillo interior superior (z=altura)
    verts_int_top = []
    for i in range(num_lados_int):
        angulo = math.radians(360 * i / num_lados_int + 30)
        x = radio_int * math.cos(angulo)
        y = radio_int * math.sin(angulo)
        verts_int_top.append(bm.verts.new((x, y, altura)))
    
    # Anillo exterior superior (z=altura)
    verts_ext_top = []
    for i in range(num_lados_ext):
        angulo = math.radians(360 * i / num_lados_ext)
        x = radio_ext * math.cos(angulo)
        y = radio_ext * math.sin(angulo)
        verts_ext_top.append(bm.verts.new((x, y, altura)))
    
    bm.verts.ensure_lookup_table()
    
    # === CARAS LATERALES EXTERIORES ===
    for i in range(num_lados_ext):
        i_next = (i + 1) % num_lados_ext
        bm.faces.new([
            verts_ext_bot[i],
            verts_ext_bot[i_next],
            verts_ext_top[i_next],
            verts_ext_top[i]
        ])
    
    # === CARAS LATERALES INTERIORES (hueco) ===
    for i in range(num_lados_int):
        i_next = (i + 1) % num_lados_int
        # Invertido para normales hacia adentro del hueco (hacia afuera del sólido)
        bm.faces.new([
            verts_int_bot[i_next],
            verts_int_bot[i],
            verts_int_top[i],
            verts_int_top[i_next]
        ])
    
    # === TAPAS (anillos entre interior y exterior) ===
    # Para las tapas necesitamos conectar el hexágono con el círculo
    # Usamos un fill simple creando triángulos
    
    # Tapa inferior
    bmesh.ops.bridge_loops(bm, edges=[e for e in bm.edges if 
        all(v in verts_int_bot for v in e.verts) or 
        all(v in verts_ext_bot for v in e.verts)])
    
    # Tapa superior  
    bmesh.ops.bridge_loops(bm, edges=[e for e in bm.edges if 
        all(v in verts_int_top for v in e.verts) or 
        all(v in verts_ext_top for v in e.verts)])
    
    return bm

def crear_seccion_tubo(radio_int, radio_ext, altura, num_lados_int=6, num_lados_ext=32, nombre="Tubo"):
    """Crea una sección de tubo y la convierte en objeto."""
    bm = bmesh.new()
    
    # Vértices inferiores
    verts_int_bot = []
    for i in range(num_lados_int):
        ang = math.radians(360 * i / num_lados_int + 30)
        verts_int_bot.append(bm.verts.new((radio_int * math.cos(ang), radio_int * math.sin(ang), 0)))
    
    verts_ext_bot = []
    for i in range(num_lados_ext):
        ang = math.radians(360 * i / num_lados_ext)
        verts_ext_bot.append(bm.verts.new((radio_ext * math.cos(ang), radio_ext * math.sin(ang), 0)))
    
    # Vértices superiores
    verts_int_top = []
    for i in range(num_lados_int):
        ang = math.radians(360 * i / num_lados_int + 30)
        verts_int_top.append(bm.verts.new((radio_int * math.cos(ang), radio_int * math.sin(ang), altura)))
    
    verts_ext_top = []
    for i in range(num_lados_ext):
        ang = math.radians(360 * i / num_lados_ext)
        verts_ext_top.append(bm.verts.new((radio_ext * math.cos(ang), radio_ext * math.sin(ang), altura)))
    
    bm.verts.ensure_lookup_table()
    
    # Caras laterales exteriores
    for i in range(num_lados_ext):
        j = (i + 1) % num_lados_ext
        bm.faces.new([verts_ext_bot[i], verts_ext_bot[j], verts_ext_top[j], verts_ext_top[i]])
    
    # Caras laterales interiores (normales invertidas)
    for i in range(num_lados_int):
        j = (i + 1) % num_lados_int
        bm.faces.new([verts_int_bot[j], verts_int_bot[i], verts_int_top[i], verts_int_top[j]])
    
    # Tapa inferior - conectar anillos con triángulos
    # Dividir el círculo exterior en segmentos que correspondan al hexágono
    seg_por_lado = num_lados_ext // num_lados_int
    
    for i in range(num_lados_int):
        i_next = (i + 1) % num_lados_int
        ext_start = i * seg_por_lado
        ext_end = (i + 1) * seg_por_lado
        
        # Primer triángulo del sector
        bm.faces.new([verts_int_bot[i], verts_ext_bot[ext_start], verts_int_bot[i_next]])
        
        # Triángulos del arco exterior
        for k in range(ext_start, ext_end):
            k_next = (k + 1) % num_lados_ext
            if k_next == ext_end % num_lados_ext:
                bm.faces.new([verts_int_bot[i_next], verts_ext_bot[k], verts_ext_bot[k_next]])
            else:
                bm.faces.new([verts_int_bot[i_next], verts_ext_bot[k], verts_ext_bot[k_next]])
    
    # Tapa superior - igual pero invertida
    for i in range(num_lados_int):
        i_next = (i + 1) % num_lados_int
        ext_start = i * seg_por_lado
        ext_end = (i + 1) * seg_por_lado
        
        bm.faces.new([verts_int_top[i_next], verts_ext_top[ext_start], verts_int_top[i]])
        
        for k in range(ext_start, ext_end):
            k_next = (k + 1) % num_lados_ext
            bm.faces.new([verts_ext_top[k_next], verts_ext_top[k], verts_int_top[i_next]])
    
    # Crear mesh
    mesh = bpy.data.meshes.new(nombre)
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(nombre, mesh)
    bpy.context.collection.objects.link(obj)
    
    return obj

def crear_llave_tubo():
    """Genera la llave de tubo hueca M3/M4."""
    
    # === PARÁMETROS (en mm) ===
    m3_entre_caras = 5.5
    m4_entre_caras = 7.0
    
    holgura = 0.15
    espesor_pared = 1.5
    
    profundidad_m3 = 6.0
    profundidad_m4 = 7.0
    longitud_mango = 25.0
    
    # Radios
    radio_m3 = m3_entre_caras / 2 + holgura
    radio_m4 = m4_entre_caras / 2 + holgura
    radio_ext = radio_m4 + espesor_pared
    
    longitud_total = profundidad_m3 + longitud_mango + profundidad_m4
    
    # Usar 30 lados exteriores (divisible por 6)
    num_ext = 30
    
    # === CREAR SECCIONES ===
    
    # Sección M3 (hueco hexagonal)
    seccion_m3 = crear_seccion_tubo(radio_m3, radio_ext, profundidad_m3, 6, num_ext, "Seccion_M3")
    seccion_m3.location = (0, 0, 0)
    
    # Sección mango (hueco circular, usa radio_m3 para continuidad)
    seccion_mango = crear_seccion_tubo(radio_m3, radio_ext, longitud_mango, num_ext, num_ext, "Mango")
    seccion_mango.location = (0, 0, profundidad_m3)
    
    # Sección M4 (hueco hexagonal)
    seccion_m4 = crear_seccion_tubo(radio_m4, radio_ext, profundidad_m4, 6, num_ext, "Seccion_M4")
    seccion_m4.location = (0, 0, profundidad_m3 + longitud_mango)
    
    # Preparar objetos
    preparar_objeto(seccion_m3)
    preparar_objeto(seccion_mango)
    preparar_objeto(seccion_m4)
    
    # === UNIR ===
    bpy.ops.object.select_all(action='DESELECT')
    seccion_m3.select_set(True)
    seccion_mango.select_set(True)
    seccion_m4.select_set(True)
    bpy.context.view_layer.objects.active = seccion_m3
    bpy.ops.object.join()
    
    llave = bpy.context.active_object
    llave.name = "Llave_Tubo_M3_M4"
    
    # === LIMPIAR ===
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(threshold=0.01)
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # === MATERIAL ===
    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')
    
    mat = bpy.data.materials.new(name="Metal_Cromado")
    mat.use_nodes = True
    principled = mat.node_tree.nodes.get("Principled BSDF")
    if principled:
        principled.inputs["Base Color"].default_value = (0.8, 0.8, 0.85, 1)
        principled.inputs["Metallic"].default_value = 1.0
        principled.inputs["Roughness"].default_value = 0.2
    llave.data.materials.append(mat)
    
    print("\n=== LLAVE DE TUBO HUECA M3/M4 ===")
    print(f"Extremo M3: hexágono {m3_entre_caras}mm (prof: {profundidad_m3}mm)")
    print(f"Extremo M4: hexágono {m4_entre_caras}mm (prof: {profundidad_m4}mm)")
    print(f"Diámetro exterior: {radio_ext * 2:.1f}mm")
    print(f"Longitud total: {longitud_total}mm")
    print("Hueca - sin soportes para impresión")
    print("==================================\n")
    
    return llave

def crear_llave_L():
    """Genera la llave plana con forma de pista y huecos hexagonales M3.5 y M4."""
    
    # === PARÁMETROS (en mm) ===
    m35_entre_caras = 6.0  # M3.5
    m4_entre_caras = 7.0   # M4
    
    holgura = 0.15
    
    # Dimensiones de la llave
    altura_llave = 3.0
    ancho_llave = 12.0  # ancho en Y
    longitud_total = 55.0
    
    # Radios hexagonales
    radio_m35 = m35_entre_caras / 2 + holgura
    radio_m4 = m4_entre_caras / 2 + holgura
    
    # Posición de los huecos
    radio_semicirculo = ancho_llave / 2
    pos_hueco_izq = radio_semicirculo
    pos_hueco_der = longitud_total - radio_semicirculo
    
    # === CREAR FORMA EXTERIOR (pista) con bmesh ===
    bm = bmesh.new()
    
    num_seg = 16  # segmentos por semicírculo
    
    # Contorno exterior - semicírculo izquierdo
    verts_bot = []
    verts_top = []
    
    for i in range(num_seg + 1):
        angulo = math.radians(90 + 180 * i / num_seg)
        x = pos_hueco_izq + radio_semicirculo * math.cos(angulo)
        y = radio_semicirculo * math.sin(angulo)
        verts_bot.append(bm.verts.new((x, y, 0)))
        verts_top.append(bm.verts.new((x, y, altura_llave)))
    
    # Contorno exterior - semicírculo derecho
    for i in range(num_seg + 1):
        angulo = math.radians(-90 + 180 * i / num_seg)
        x = pos_hueco_der + radio_semicirculo * math.cos(angulo)
        y = radio_semicirculo * math.sin(angulo)
        verts_bot.append(bm.verts.new((x, y, 0)))
        verts_top.append(bm.verts.new((x, y, altura_llave)))
    
    bm.verts.ensure_lookup_table()
    
    n = len(verts_bot)
    
    # Caras laterales exteriores
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([verts_bot[i], verts_bot[j], verts_top[j], verts_top[i]])
    
    # Tapa inferior y superior
    bm.faces.new(verts_bot)
    bm.faces.new(verts_top[::-1])
    
    mesh = bpy.data.meshes.new("Llave_Plana")
    bm.to_mesh(mesh)
    bm.free()
    
    llave = bpy.data.objects.new("Llave_Plana", mesh)
    bpy.context.collection.objects.link(llave)
    
    bpy.ops.object.select_all(action='DESELECT')
    llave.select_set(True)
    bpy.context.view_layer.objects.active = llave
    
    # Recalcular normales
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # === HUECO M3.5 (izquierdo) ===
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=6, 
        radius=radio_m35, 
        depth=altura_llave + 2, 
        location=(pos_hueco_izq, 0, altura_llave/2)
    )
    hueco_izq = bpy.context.active_object
    hueco_izq.rotation_euler = (0, 0, math.radians(30))
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    
    # Boolean M3.5
    mod = llave.modifiers.new(name="Bool_M35", type='BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.solver = 'EXACT'
    mod.object = hueco_izq
    
    bpy.context.view_layer.objects.active = llave
    bpy.ops.object.modifier_apply(modifier="Bool_M35")
    bpy.data.objects.remove(hueco_izq, do_unlink=True)
    
    # === HUECO M4 (derecho) ===
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=6, 
        radius=radio_m4, 
        depth=altura_llave + 2, 
        location=(pos_hueco_der, 0, altura_llave/2)
    )
    hueco_der = bpy.context.active_object
    hueco_der.rotation_euler = (0, 0, math.radians(30))
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    
    # Boolean M4
    mod = llave.modifiers.new(name="Bool_M4", type='BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.solver = 'EXACT'
    mod.object = hueco_der
    
    bpy.context.view_layer.objects.active = llave
    bpy.ops.object.modifier_apply(modifier="Bool_M4")
    bpy.data.objects.remove(hueco_der, do_unlink=True)
    
    # === LIMPIAR ===
    llave.name = "Llave_Plana_M35_M4"
    
    bpy.ops.object.select_all(action='DESELECT')
    llave.select_set(True)
    bpy.context.view_layer.objects.active = llave
    
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(threshold=0.01)
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')
    
    # === MATERIAL ===
    mat = bpy.data.materials.new(name="Metal_Cromado_Plana")
    mat.use_nodes = True
    principled = mat.node_tree.nodes.get("Principled BSDF")
    if principled:
        principled.inputs["Base Color"].default_value = (0.7, 0.7, 0.75, 1)
        principled.inputs["Metallic"].default_value = 1.0
        principled.inputs["Roughness"].default_value = 0.25
    llave.data.materials.append(mat)
    
    print("\n=== LLAVE PLANA M3.5 / M4 ===")
    print(f"Hueco izquierdo: M3.5 ({m35_entre_caras}mm)")
    print(f"Hueco derecho: M4 ({m4_entre_caras}mm)")
    print(f"Dimensiones: {longitud_total}mm x {ancho_llave}mm x {altura_llave}mm")
    print("Forma de pista (extremos redondeados)")
    print("=============================\n")
    
    return llave


if __name__ == "__main__":
    limpiar_escena()
    
    # Crear llave tubo recta
    llave_tubo = crear_llave_tubo()
    llave_tubo.location = (-20, 0, 0)
    
    # Crear llave plana (más separada)
    llave_L = crear_llave_L()
    llave_L.location = (25, 0, 0)
