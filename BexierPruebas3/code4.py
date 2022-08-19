import bpy
import json
import bmesh
from math import sqrt

class Point:
    x=0
    y=0
    z=0
    
    def __init__(self,x,y,z):
        self.x=x
        self.y=y
        self.z=z

def getPointComponent(t, a, b, c, d):
    p1 = (1 - t)**3 * a
    p2 = 3 * (1 - t)**2 * t * b
    p3 = 3 * (1 - t) * t**2 * c
    p4 = t**3 * d
    
    return p1+p2+p3+p4
    
def getInterpolated(delta,initPoint, handleInit, handleEnd, endPoint):
    x = getPointComponent(delta, initPoint.x, handleInit.x, handleEnd.x, endPoint.x);
    y = getPointComponent(delta, initPoint.y, handleInit.y, handleEnd.y, endPoint.y);
    z = getPointComponent(delta, initPoint.z, handleInit.z, handleEnd.z, endPoint.z);

    return Point(x,y,z)

def distance(p1,p2):
    if p1==None or p2==None:
        print('Point null in distance method param')
        return -1
    
    return sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2 + (p2.z - p1.z)**2)



selection=bpy.context.selected_objects





for i in range(len(selection)): 
    if selection[i].type =='CURVE':
        curve=selection[i]   
        mcurve=bpy.data.meshes.new("curveMesh-"+str(i))
        obj = bpy.data.objects.new("objectCurve-"+str(i), mcurve)
        
        scene = bpy.context.scene
        scene.objects.link(obj)
        scene.objects.active = obj
        obj.select = True

        mesh = bpy.context.object.data
        bm = bmesh.new()                                
        
        i=0;   
        
