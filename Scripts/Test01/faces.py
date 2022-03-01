import bpy
import bmesh

obj=bpy.context.active_object

print('start')

if(obj.mode=='EDIT'):
    bm=bmesh.from_edit_mesh(obj.data)
    hist=bm.select_history
            
    if(len(hist)==2 and bm.select_mode=={'FACE'}):
        print('vamos')
        verts1=''