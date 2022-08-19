import bpy
import json
from math import sqrt
   

def distance(p1,p2):
    return sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2 + (p2.z - p1.z)**2)


selection=bpy.context.selected_objects

print("import java.util.*;\r\n")

print("class Point{")
print("\tpublic float x;")
print("\tpublic float y;")
print("\tpublic float z;\r\n")        
print("\tpublic Point(float x, float y, float z){")
print("\t\tthis.x=x;");
print("\t\tthis.y=y;");
print("\t\tthis.z=z;");
print("\t}")
print("}\r\n")

print("class Spline{") 
print("\tpublic List<Point> control_point=new ArrayList();")
print("\tpublic List<Point> handle_left=new ArrayList();")
print("\tpublic List<Point> handle_right=new ArrayList();")        
print("\tpublic float len;")
print("\tpublic boolean cyclic;")
print("}\r\n")

print("class Curve{") 
print("\tpublic List<Spline> splines=new ArrayList();\r\n")

print("\tpublic static Curve getCurve(){")

for i in range(len(selection)): 
    if selection[i].type =='CURVE':
        curve=selection[i]   
        print("\tCurve curve=new Curve();")
        print("\tSpline spline=null;\r\n")
                         
        i=0;   
        
        for spline in curve.data.splines:
            i=i+1
            print("\t//SPLINE {:n}".format(i))           
            print("\tspline=new Spline();")
           
            state = "true" if spline.use_cyclic_u else "false"    
            print("\tspline.cyclic="+state+";")
            print("\tcurve.splines.add(spline);")   
            
            
            for bezier_point in spline.bezier_points:
                co=bezier_point.co
                hr=bezier_point.handle_right
                hl=bezier_point.handle_left                             
                                    
                print ("\tspline.control_point.add(new Point({:f}f,{:f}f,{:f}f));".format(co.x,co.y,co.z))
                print ("\tspline.handle_left.add(new Point({:f}f,{:f}f,{:f}f));".format(hl.x,hl.y,hl.z))
                print ("\tspline.handle_right.add(new Point({:f}f,{:f}f,{:f}f));".format(hr.x,hr.y,hr.z))                                

print("\r\n");
print("\treturn curve;");    
print("\t}")
print("}\r\n")    
   
   