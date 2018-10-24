from math import sin
from vec3 import Vec3
from perlin import Perlin

class Texture:
    def __init__(self, color):
        self.color = color
    def value(self, u=0, v=0, p=Vec3()):
        return self.color

class ConstantTexture(Texture):
    def __init__(self, color):
        #super().__init__()
        self.color = color

    def value(self, u=0, v=0, p=Vec3()):
        return self.color

class CheckerTexture(Texture):
    def __init__(self, t0, t1):
        #super().__init__()
        self.t0 = t0
        self.t1 = t1

    def value(self, u=0, v=0, p=Vec3()):
        sines = sin(10*p.x) * sin(10*p.y) * sin(10*p.z)
        if sines < 0:
            return self.t0.value(u, v, p)
        return self.t1.value(u, v, p)

class NoiseTexture(Texture):
    def __init__(self):
        self.color = Vec3(1,1,1)

    def value(self, u=0, v=0, p=Vec3()):
        noise = Perlin.noise(p)
        #print(noise)
        return noise*Vec3(1,1,1)
