from math import sqrt

class Point:
    x=0
    y=0
    z=0
    
    def __init__(self, x, y, z):
        self.x=x
        self.y=y
        self.z=z
        
    def print(self):
        print(self.x,self.y,self.z)        

class Utils:
    @staticmethod
    def _getPointComponent(t, a, b, c, d):
        p1 = (1 - t)**3 * a
        p2 = 3 * (1 - t)**2 * t * b
        p3 = 3 * (1 - t) * t**2 * c
        p4 = t**3 * d
        
        return p1+p2+p3+p4

    @staticmethod
    def getInterpolated(delta, initPoint, handleInit, handleEnd, endPoint):
        x = Utils._getPointComponent(delta, initPoint.x, handleInit.x, handleEnd.x, endPoint.x);
        y = Utils._getPointComponent(delta, initPoint.y, handleInit.y, handleEnd.y, endPoint.y);
        z = Utils._getPointComponent(delta, initPoint.z, handleInit.z, handleEnd.z, endPoint.z);

        return Point(x,y,z)
    
    @staticmethod
    def getDistance(p1,p2):
        if p1==None or p2==None:
            print('Point null in distance method param')
            return -1
        
        return sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2 + (p2.z - p1.z)**2)    