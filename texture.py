from math import sin
from vec3 import Vec3
from perlin import Perlin

class Texture:
##    def __init__(self, color):
##        self.color = color
    def value(self, u, v, p):
        return Vec3(0, 0, 0)

class ConstantTexture(Texture):
    def __init__(self, color):
        self.color = color

    def value(self, u, v, p):
        return self.color

class CheckerTexture(Texture):
    def __init__(self, t0, t1):
        self.t0 = t0
        self.t1 = t1

    def value(self, u, v, p):
        sines = sin(10*p.x) * sin(10*p.y) * sin(10*p.z)
        if sines < 0:
            return self.t0.value(u, v, p)
        return self.t1.value(u, v, p)

class NoiseTexture(Texture):
    def __init__(self):
        self.color = Vec3(1,1,1)

    def value(self, u, v, p):
        noise = Perlin.noise(p)
        return noise*Vec3(1,1,1)
