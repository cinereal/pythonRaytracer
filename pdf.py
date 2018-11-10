from onb import ONB
from vec3 import Vec3
import math, random

def random_cosine_direction():
    r1 = random.random()
    r2 = random.random()
    z = math.sqrt(1 - r2)
    phi = 2 * math.pi * r1
    x = math.cos(phi) * 2 * math.sqrt(r2)
    y = math.sin(phi) * 2 * math.sqrt(r2)
    return Vec3(x, y, z)

def random_to_sphere(radius, distance_squared):
    r1 = random.random()
    r2 = random.random()
    z = 1 + r2 * math.sqrt((1 - radius*radius/distance_squared) - 1)
    phi = 2 * math.pi * r1
    x = math.cos(phi) * 2 * math.sqrt(1-z*z)
    y = math.sin(phi) * 2 * math.sqrt(1-z*z)
    return Vec3(x, y, z)

def random_in_unit_sphere():
    while True:
        p = 2 * Vec3(random.random(), random.random(), random.random()) - Vec3(1, 1, 1)
        #if p.squared_length() < 1:
        if p.dot(p) < 1.0:
            return p.unit()

class PDF:
    def value(self, direction):
        raise NotImplementedError()
    
    def generate(self):
        raise NotImplementedError()

class CosinePDF(PDF):
    def __init__(self, w):
        self.uvw = ONB()
        self.uvw.build_from_w(w)

    def value(self, direction):
        cosine = direction.unit().dot(self.uvw.w)
        if cosine > 0:
            return cosine / math.pi
        else:
            return 0

    def generate(self):
        return self.uvw.local(random_cosine_direction())

class HitablePDF(PDF):
    def __init__(self, p, o):
        self.ptr = p
        self.origin = o

    def value(self, direction):
        return self.ptr.pdf_value(self.origin, direction)

    def generate(self):
        return self.ptr.random(self.origin)


class MixturePDF(PDF):
    def __init__(self, p0, p1):
        self.p0 = p0
        self.p1 = p1

    def value(self, direction):
        return 0.5 * self.p0.value(direction) + self.p1.value(direction)

    def generate(self):
        if random.random() < 0.5:
            return self.p0.generate()
        else:
            return self.p1.generate()
