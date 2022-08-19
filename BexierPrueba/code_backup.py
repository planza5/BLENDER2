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


def distancebp(bp1,bp2):
    return sqrt((bp2.x - bp1.x)**2 + (bp2.y - bp1.y)**2 + (bp2.z - bp1.z)**2)

def calculateLen(bp1,bp2):
    thelen=0
    therange=100
    
    for t in range(therange):
        delta1=t/therange
        delta2=(t+1)/therange        
#        print(delta1,delta2)
        p1=getInterpolated(delta1,bp1.co,bp1.handle_right,bp2.handle_left,bp2.co)
        p2=getInterpolated(delta2,bp1.co,bp1.handle_right,bp2.handle_left,bp2.co)        
        thelen += distance(p1,p2)    

    return thelen


def buildSegments(bm,a,b,maxDistance,isclosed, othersplinevertex):
    print("buildSegments")
    
    if a==None or b==None:
        print ('a or b is null')
        return None
    
    t=0
    d=0;
    
    lastInterpolated=Point(a.co.x,a.co.y,a.co.z)
    lastvertex=bm.verts.new((lastInterpolated.x,lastInterpolated.y+20,lastInterpolated.z))
    
     
    if othersplinevertex!=None:
        pass
    
    
    while t < 1:
        nowInterpolated=getInterpolated(t,a.co,a.handle_right,b.handle_left,b.co)                
        d=distance(lastInterpolated,nowInterpolated)
                  
        if d>maxDistance:
            vertex=bm.verts.new((nowInterpolated.x,nowInterpolated.y+20,nowInterpolated.z))          
            lastInterpolated=nowInterpolated   
            
            if lastvertex!=None:
                bm.edges.new((lastvertex,vertex))
                 
            lastvertex=vertex
        t+=0.001
    
    if isclosed==False:
        vertex=bm.verts.new((b.co.x,b.co.y+20,b.co.z))
        bm.edges.new((lastvertex,vertex))                    

    return lastvertex

#START PROGRAM    


selection=bpy.context.selected_objects

print("using System.Collections.Generic;")
print("using UnityEngine;\r\n")


print("public class Point{")
print("\tpublic float x;")
print("\tpublic float y;")
print("\tpublic float z;\r\n")        
print("\tpublic Point(float x, float y, float z){")
print("\t\tthis.x=x;");
print("\t\tthis.y=y;");
print("\t\tthis.z=z;");
print("\t}")
print("}\r\n")


print("public class Segment");
print("{");
print("\tpublic Point a;");
print("\tpublic Point b;");
print(" \tpublic float distance;");
print("}\r\n");

print("public class Curve:MonoBehaviour{") 
print("\tpublic List<Segment> segments=new List<Segment>();\r\n")

print("\tpublic Curve(){")



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
        
        for spline in curve.data.splines:
            i=i+1
            print("\t//SPLINE {:n}".format(i))           
            print("\tspline=new Spline();")
           
            state = "true" if spline.use_cyclic_u else "false"    
            print("\tspline.cyclic="+state+";")
            
            print("\tsplines.Add(spline);")   
            
            maxDistance=10
            thelen=len(spline.bezier_points)
            lastvertex=None
                           
            for bpIdx in range(thelen):
                print("point "+str(bpIdx))
                
                if bpIdx==thelen-1:
                    if spline.use_cyclic_u:
                        lastvertex=buildSegments(bm,spline.bezier_points[thelen-1],spline.bezier_points[0],maxDistance,spline.use_cyclic_u, lastvertex)        
                else:
                    lastvertex=buildSegments(bm,spline.bezier_points[bpIdx],spline.bezier_points[bpIdx+1],maxDistance,spline.use_cyclic_u, lastvertex)

  
        bm.to_mesh(mesh)
        bm.free()
        
print("\t}\r\n")

print("}\r\n")    
   
