import bpy
import json

def export_material_nodes(material_name=None):
    """Exporta los nodos del material activo o especificado a JSON"""
    
    if material_name:
        mat = bpy.data.materials.get(material_name)
    else:
        obj = bpy.context.active_object
        if obj and obj.active_material:
            mat = obj.active_material
        else:
            return {"error": "No hay material activo"}
    
    if not mat or not mat.use_nodes:
        return {"error": "El material no usa nodos"}
    
    nodes_data = []
    links_data = []
    
    for node in mat.node_tree.nodes:
        node_info = {
            "name": node.name,
            "type": node.bl_idname,
            "location": [node.location.x, node.location.y],
            "inputs": {},
            "outputs": list(out.name for out in node.outputs),
            "properties": {}
        }
        
        # Guardar valores de inputs no conectados
        for inp in node.inputs:
            if not inp.is_linked and hasattr(inp, 'default_value'):
                try:
                    val = inp.default_value
                    if hasattr(val, '__iter__') and not isinstance(val, str):
                        node_info["inputs"][inp.name] = list(val)
                    else:
                        node_info["inputs"][inp.name] = val
                except:
                    pass
        
        # Propiedades específicas por tipo de nodo
        if node.bl_idname == 'ShaderNodeTexNoise':
            node_info["properties"] = {
                "noise_dimensions": node.noise_dimensions,
                "scale": node.inputs['Scale'].default_value if 'Scale' in node.inputs else None,
                "detail": node.inputs['Detail'].default_value if 'Detail' in node.inputs else None,
                "roughness": node.inputs['Roughness'].default_value if 'Roughness' in node.inputs else None,
            }
        
        elif node.bl_idname == 'ShaderNodeTexWave':
            node_info["properties"] = {
                "wave_type": node.wave_type,
                "bands_direction": node.bands_direction,
                "wave_profile": node.wave_profile,
                "scale": node.inputs['Scale'].default_value if 'Scale' in node.inputs else None,
                "distortion": node.inputs['Distortion'].default_value if 'Distortion' in node.inputs else None,
                "detail": node.inputs['Detail'].default_value if 'Detail' in node.inputs else None,
                "detail_scale": node.inputs['Detail Scale'].default_value if 'Detail Scale' in node.inputs else None,
                "detail_roughness": node.inputs['Detail Roughness'].default_value if 'Detail Roughness' in node.inputs else None,
            }
        
        elif node.bl_idname == 'ShaderNodeValToRGB':  # ColorRamp
            stops = []
            for element in node.color_ramp.elements:
                stops.append({
                    "position": element.position,
                    "color": list(element.color)
                })
            node_info["properties"] = {
                "color_mode": node.color_ramp.color_mode,
                "interpolation": node.color_ramp.interpolation,
                "stops": stops
            }
        
        elif node.bl_idname == 'ShaderNodeMix':
            node_info["properties"] = {
                "data_type": node.data_type,
                "blend_type": node.blend_type if node.data_type == 'RGBA' else None,
                "clamp_factor": node.clamp_factor,
                "factor": node.inputs['Factor'].default_value if 'Factor' in node.inputs else None,
            }
        
        elif node.bl_idname == 'ShaderNodeMath':
            node_info["properties"] = {
                "operation": node.operation,
                "use_clamp": node.use_clamp,
            }
        
        elif node.bl_idname == 'ShaderNodeVectorMath':
            node_info["properties"] = {
                "operation": node.operation,
            }
        
        elif node.bl_idname == 'ShaderNodeBump':
            node_info["properties"] = {
                "invert": node.invert,
                "strength": node.inputs['Strength'].default_value if 'Strength' in node.inputs else None,
                "distance": node.inputs['Distance'].default_value if 'Distance' in node.inputs else None,
            }
        
        elif node.bl_idname == 'ShaderNodeMapping':
            node_info["properties"] = {
                "vector_type": node.vector_type,
            }
        
        nodes_data.append(node_info)
    
    # Exportar conexiones
    for link in mat.node_tree.links:
        links_data.append({
            "from_node": link.from_node.name,
            "from_socket": link.from_socket.name,
            "to_node": link.to_node.name,
            "to_socket": link.to_socket.name
        })
    
    result = {
        "material_name": mat.name,
        "nodes": nodes_data,
        "links": links_data
    }
    
    return result


# Ejecutar y guardar
data = export_material_nodes()
output_path = bpy.path.abspath("//material_nodes.json")

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Exportado a: {output_path}")