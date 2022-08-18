import bpy
import bmesh

def joinfaces(obj, bm, f1,f2):   
    print('joining')
    
    targetmap={f1.verts[0]:f2.verts[0]}
    dict=bmesh.ops.weld_verts(bm,targetmap=targetmap)
    
    targetmap={f1.verts[1]:f2.verts[1]}
    dict=bmesh.ops.weld_verts(bm,targetmap=targetmap)
    
    targetmap={f1.verts[2]:f2.verts[2]}
    dict=bmesh.ops.weld_verts(bm,targetmap=targetmap)
    
    targetmap={f1.verts[3]:f2.verts[3]}
    dict=bmesh.ops.weld_verts(bm,targetmap=targetmap)
        
    print(dict)
    bmesh.update_edit_mesh(obj.data ,True)
    

obj=bpy.context.active_object

print('start')

if(obj.mode=='EDIT'):
    bm=bmesh.from_edit_mesh(obj.data)
    bmesh.ops.weld_verts(bm)
    hist=bm.select_history
            
    if(len(hist)==2 and bm.select_mode=={'FACE'}):
        if(len(hist[0].verts) == len(hist[1].verts)):
            joinfaces(obj,bm,hist[0],hist[1])
    else:
        print(len(hist))        