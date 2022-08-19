import bpy
import json
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
    return sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2 + (p2.z - p1.z)**2)

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

print("public class Spline{") 
print("\tpublic List<Point> control_point=new List<Point>();")
print("\tpublic List<Point> handle_left=new List<Point>();")
print("\tpublic List<Point> handle_right=new List<Point>();")
print("\tpublic List<float> len = new List<float>();")        
print("\tpublic bool cyclic;")
print("}\r\n")

print("public class Curve:MonoBehaviour{") 
print("\tpublic List<Spline> splines=new List<Spline>();\r\n")

print("\tpublic Curve(){")

for i in range(len(selection)): 
    if selection[i].type =='CURVE':
        curve=selection[i]   
        print("\tSpline spline=null;\r\n")
                         
        i=0;   
        
        for spline in curve.data.splines:
            i=i+1
            print("\t//SPLINE {:n}".format(i))           
            print("\tspline=new Spline();")
           
            state = "true" if spline.use_cyclic_u else "false"    
            print("\tspline.cyclic="+state+";")
            
            print("\tsplines.Add(spline);")   
            
           
            for bpIdx in range(len(spline.bezier_points)):
                bp=spline.bezier_points[bpIdx]
                co=bp.co
                hr=bp.handle_right
                hl=bp.handle_left                             
                                    
                print ("\tspline.control_point.Add(new Point({:f}f,{:f}f,{:f}f));".format(co.x,co.z,-1* co.y))
                print ("\tspline.handle_left.Add(new Point({:f}f,{:f}f,{:f}f));".format(hl.x,hl.z,-1 * hl.y))
                print ("\tspline.handle_right.Add(new Point({:f}f,{:f}f,{:f}f));".format(hr.x,hr.z,-1 * hr.y))    

                thelen = 0
                
                if bpIdx==len(spline.bezier_points) - 1:
                    thelen=calculateLen(spline.bezier_points[len(spline.bezier_points)-1],spline.bezier_points[0])
                else:
                    thelen=calculateLen(spline.bezier_points[bpIdx],spline.bezier_points[bpIdx+1])
                
                print ("\tspline.len.Add({:f}f);".format(thelen)) 
 
print("\t}\r\n")

print("}\r\n")    
   
