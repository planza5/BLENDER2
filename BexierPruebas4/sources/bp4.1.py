import bpy

print("\r\n\r\n\r\n\r\n")

selection=bpy.context.selected_objects

ncurve=1
nspline=1;

for selection in selection: 
    if selection.type =='CURVE':
        curve=selection   
        bpy.context.scene.objects.active = curve     
        bpy.ops.object.transform_apply(location = True, scale = True, rotation = True)
        print("Curve curve{:n}=new Curve();".format(ncurve))            
        print("curves.Add(curve{:n});".format(ncurve))                    
        
        for spline in curve.data.splines:          
            print("Spline spline{:n}=new Spline();".format(nspline))  
            print("spline{:n}.cyclic=".format(nspline)+("true;" if spline.use_cyclic_u else "false;"))              
            print("curve{:n}.splines.Add(spline{:n});".format(ncurve,nspline))                                              
                      
            for bp in spline.bezier_points:
                print("vco=new Vector3({:f}f,{:f}f,{:f}f);".format(bp.co.x,-bp.co.z,bp.co.y))
                print("vhl=new Vector3({:f}f,{:f}f,{:f}f);".format(bp.handle_left.x,-bp.handle_left.z,bp.handle_left.y))
                print("vhr=new Vector3({:f}f,{:f}f,{:f}f);".format(bp.handle_right.x,-bp.handle_right.z,bp.handle_right.y))
                print("spline{:n}.points.Add(new BezierPoint(vco,vhl,vhr));".format(nspline))  

                
            nspline=nspline+1
                            
        print("") 
        ncurve=ncurve+1;      