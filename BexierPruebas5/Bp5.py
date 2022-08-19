import bpy
import bmesh
from math import sqrt

MAX_DISTANCE=5
bm=None

class Point:
    x=0
    y=0
    z=0
    
    def __init__(self,x,y,z):
        self.x=x
        self.y=y
        self.z=z
        


def getDistance(p1,p2):
    if p1==None or p2==None:
        print('Point null in distance method param')
        return
    
    return sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2 + (p2.z - p1.z)**2)

def getPointComponent(t, a, b, c, d):
    p1 = (1 - t)**3 * a
    p2 = 3 * (1 - t)**2 * t * b
    p3 = 3 * (1 - t) * t**2 * c
    p4 = t**3 * d
    
    return p1+p2+p3+p4

def getInterpolated(delta, initPoint, handleInit, handleEnd, endPoint):
    x = getPointComponent(delta, initPoint.x, handleInit.x, handleEnd.x, endPoint.x);
    y = getPointComponent(delta, initPoint.y, handleInit.y, handleEnd.y, endPoint.y);
    z = getPointComponent(delta, initPoint.z, handleInit.z, handleEnd.z, endPoint.z);

    return Point(x,y,z)


def buildSegment(bp1, bp2, lastvert):   
    print('buildSegment111')
    lastpoint=None
    
    if lastvert==None:
        lastvert = bm.verts.new((bp1.co.x,bp1.co.y,bp1.co.z))
        lastpoint = Point(bp1.co.x,bp1.co.y,bp1.co.z)
            
    distance=0
    delta=0
    newvert=None
    
    print ('antes bucle')

    
    while delta<1:
        distance=0
        
        while distance < MAX_DISTANCE:
            delta=delta+0.001          
            newvert=getInterpolated(delta, bp1.co, bp1.handle_right, bp2.handle_left, bp2.co)
            distance=getDistance(lastpoint,Point(newvert.x,newvert.y,newvert.z))

        if delta<1:           
            vert=bm.verts.new((newvert.x,newvert.y,newvert.z))
                            
    return lastpoint

print("\r\n\r\n\r\n\r\n")
print('building mesh')
mcurve=bpy.data.meshes.new("curveMesh")
obj = bpy.data.objects.new("objectCurve", mcurve)
scene = bpy.context.scene
scene.objects.link(obj)
scene.objects.active = obj
obj.select = True
mesh = bpy.context.object.data
bm = bmesh.new()

for one in bpy.context.selected_objects: 
    if one.type =='CURVE':
        curve=one 
        bpy.context.scene.objects.active = curve     
        bpy.ops.object.transform_apply(location = True, scale = True, rotation = True)

        lastvert=None
                    
        for spline in curve.data.splines:
            for i in range(1,len(spline.bezier_points)):
                bp1=spline.bezier_points[i-1]
                bp2=spline.bezier_points[i]
                lastvert=buildSegment(bp1,bp2,lastvert)
            
bm.to_mesh(mesh)
bm.free()                