bl_info = {
    "name": "Mi primer add-on",
    "author": "Tu nombre",
    "version": (1, 0),
    "blender": (3, 3, 0),
    "location": "Panel de Herramientas",
    "description": "Descripción de mi add-on",
    "category": "Object",
}

import bpy

class MI_OT_MiOperacion(bpy.types.Operator):
    bl_idname = "object.mi_operacion"
    bl_label = "Mi Operación"

    def execute(self, context):
        # Agregar aquí la lógica de tu operación
        return {'FINISHED'}

class MI_PT_Panel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_mi_panel"
    bl_label = "Mi Panel"
    bl_category = "Mi Categoría"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label(text="Mi Add-on")

        row = layout.row()
        row.operator("object.mi_operacion")

def register():
    bpy.utils.register_class(MI_OT_MiOperacion)
    bpy.utils.register_class(MI_PT_Panel)

def unregister():
    bpy.utils.unregister_class(MI_OT_MiOperacion)
    bpy.utils.unregister_class(MI_PT_Panel)

if __name__ == "__main__":
    register()
   