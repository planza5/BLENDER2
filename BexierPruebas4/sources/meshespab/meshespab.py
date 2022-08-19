import bpy
import bmesh

class MeshesUtils:
    _mesh=None
    _obj=None
    _bmesh=None
    
    def createMesh(name):
        _mesh = bpy.data.meshes.new(name+"-mesh") 
        _obj = bpy.data.objects.new(name+"-obj", _mesh)
        
        bpy.context.scene.objects.link(_obj)
        scene.objects.active = _obj
        _obj.select = True    
        
        _mesh = bpy.context.object.data
        _bmesh = bmesh.new()
        
    def createVertex(self,vertex): 
        return self._bmesh.verts.new(vertex)

    def createEdge(self,p1,p2):
        return self._bmesh.edges.new(p1,p2)
    
    def persistMesh(self):
        _bmesh.to_mesh(_mesh)  
        _bmesh.free()
        
    def draw(self, points):
        print('hola')