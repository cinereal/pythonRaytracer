from vec3 import Vec3
from math import fabs

# Ortho-normal Bases - three mutually orthogonal unit vectors
class ONB:
    def __init__(self):
        self.u = Vec3()
        self.v = Vec3()
        self.w = Vec3()
        
    def local(self, a, b=0, c=0):
        if isinstance(a, float):
            return a * self.u + b * self.v + c * self.w
        elif isinstance(a, Vec3):
            return a.x * self.u + a.y * self.v + a.z * self.w
        else:
            raise ValueError('parameter is not a float or Vec3')

    def build_from_w(self, n):
        self.w = n.unit()
        if fabs(self.w.x) > 0.9:
            a = Vec3(0, 1, 0)
        else:
            a = Vec3(1, 0, 0)
        self.v = self.w.cross(a).unit()
        self.u = self.w.cross(self.v)
