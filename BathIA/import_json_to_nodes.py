import bpy
import json

# CONFIGURACIÓN: Cambia esta ruta al JSON que quieras importar
JSON_PATH = bpy.path.abspath("//material_nodes.json")


def import_material_nodes(json_path, material_name=None):
    """Importa nodos desde JSON al material activo o especificado"""
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Obtener o crear material
    if material_name:
        mat = bpy.data.materials.get(material_name)
        if not mat:
            mat = bpy.data.materials.new(name=material_name)
    else:
        obj = bpy.context.active_object
        if obj and obj.active_material:
            mat = obj.active_material
        else:
            mat = bpy.data.materials.new(name=data.get("material_name", "Imported_Material"))
            if obj:
                obj.data.materials.append(mat)
    
    mat.use_nodes = True
    tree = mat.node_tree
    
    # Limpiar nodos existentes
    tree.nodes.clear()
    
    # Mapeo de tipos de nodos
    node_type_map = {
        "ShaderNodeTexNoise": "ShaderNodeTexNoise",
        "ShaderNodeTexWave": "ShaderNodeTexWave",
        "ShaderNodeValToRGB": "ShaderNodeValToRGB",
        "ShaderNodeMix": "ShaderNodeMix",
        "ShaderNodeMath": "ShaderNodeMath",
        "ShaderNodeVectorMath": "ShaderNodeVectorMath",
        "ShaderNodeBump": "ShaderNodeBump",
        "ShaderNodeMapping": "ShaderNodeMapping",
        "ShaderNodeTexCoord": "ShaderNodeTexCoord",
        "ShaderNodeBsdfPrincipled": "ShaderNodeBsdfPrincipled",
        "ShaderNodeOutputMaterial": "ShaderNodeOutputMaterial",
    }
    
    created_nodes = {}
    
    # Crear nodos
    for node_data in data["nodes"]:
        node_type = node_data["type"]
        
        if node_type not in node_type_map:
            print(f"Tipo de nodo no soportado: {node_type}")
            continue
        
        node = tree.nodes.new(type=node_type)
        node.name = node_data["name"]
        node.location = node_data["location"]
        created_nodes[node_data["name"]] = node
        
        props = node_data.get("properties", {})
        
        # Configurar propiedades específicas
        if node_type == "ShaderNodeTexNoise":
            if "noise_dimensions" in props:
                node.noise_dimensions = props["noise_dimensions"]
        
        elif node_type == "ShaderNodeTexWave":
            if "wave_type" in props:
                node.wave_type = props["wave_type"]
            if "bands_direction" in props:
                node.bands_direction = props["bands_direction"]
            if "wave_profile" in props:
                node.wave_profile = props["wave_profile"]
        
        elif node_type == "ShaderNodeValToRGB":
            if "color_mode" in props:
                node.color_ramp.color_mode = props["color_mode"]
            if "interpolation" in props:
                node.color_ramp.interpolation = props["interpolation"]
            if "stops" in props:
                elements = node.color_ramp.elements
                # Eliminar elementos por defecto excepto el primero
                while len(elements) > 1:
                    elements.remove(elements[-1])
                
                for i, stop in enumerate(props["stops"]):
                    if i == 0:
                        elements[0].position = stop["position"]
                        elements[0].color = stop["color"]
                    else:
                        el = elements.new(stop["position"])
                        el.color = stop["color"]
        
        elif node_type == "ShaderNodeMix":
            if "data_type" in props:
                node.data_type = props["data_type"]
            if "blend_type" in props and props["blend_type"]:
                node.blend_type = props["blend_type"]
            if "clamp_factor" in props:
                node.clamp_factor = props["clamp_factor"]
        
        elif node_type == "ShaderNodeMath":
            if "operation" in props:
                node.operation = props["operation"]
            if "use_clamp" in props:
                node.use_clamp = props["use_clamp"]
        
        elif node_type == "ShaderNodeVectorMath":
            if "operation" in props:
                node.operation = props["operation"]
        
        elif node_type == "ShaderNodeBump":
            if "invert" in props:
                node.invert = props["invert"]
        
        elif node_type == "ShaderNodeMapping":
            if "vector_type" in props:
                node.vector_type = props["vector_type"]
        
        # Configurar inputs no conectados
        inputs = node_data.get("inputs", {})
        for input_name, value in inputs.items():
            if input_name in node.inputs:
                inp = node.inputs[input_name]
                if hasattr(inp, 'default_value'):
                    try:
                        if isinstance(value, list):
                            inp.default_value = value[:len(inp.default_value)]
                        elif not isinstance(value, str):
                            inp.default_value = value
                    except:
                        pass
    
    # Crear conexiones
    for link_data in data["links"]:
        from_node = created_nodes.get(link_data["from_node"])
        to_node = created_nodes.get(link_data["to_node"])
        
        if not from_node or not to_node:
            print(f"No se puede crear link: {link_data}")
            continue
        
        from_socket = None
        to_socket = None
        
        # Buscar sockets por nombre
        for out in from_node.outputs:
            if out.name == link_data["from_socket"]:
                from_socket = out
                break
        
        for inp in to_node.inputs:
            if inp.name == link_data["to_socket"]:
                to_socket = inp
                break
        
        if from_socket and to_socket:
            tree.links.new(from_socket, to_socket)
        else:
            print(f"Socket no encontrado: {link_data}")
    
    print(f"Material '{mat.name}' importado con {len(created_nodes)} nodos")
    return mat


# Ejecutar
import_material_nodes(JSON_PATH)