from vec3 import Vec3
from ray import Ray
from texture import Texture
from collections import namedtuple
import random
import math

def random_in_unit_sphere():
    p = Vec3(1, 1, 1)
    while True:
        s = 2 * Vec3(random.random(), random.random(), random.random()) - p
        if s.squared_length() < 1:
            return s

ScatterRecord = namedtuple('ScatterRecord', ['attenuation', 'scattered'])

class Material:
    def scatter(self, ray, rec):
        raise NotImplementedError()

    def emitted(self, u, v, p):
        return Vec3(0, 0, 0)

class DiffuseLight(Material):
    def __init__(self, emit):
        super().__init__()
        self.emit = emit

    def scatter(self, ray, rec):
        return None

    def emitted(self, u, v, p):
        return self.emit.value(u, v, p)

class Lambertian(Material):
    def __init__(self, albedo):
        super().__init__()
        self.albedo = albedo

    def scatter(self, ray, rec):
        target = rec.p + rec.normal + random_in_unit_sphere()
        scattered = Ray(rec.p, target - rec.p, ray.time)
        #attenuation = self.albedo
        #attenuation = Texture().value(self.albedo)
        attenuation = self.albedo.value(0, 0, rec.p)
        return ScatterRecord(attenuation, scattered)

def reflect(v, n):
    return v - 2*v.dot(n)*n

class Metal(Material):
    def __init__(self, albedo, fuzz=0):
        super().__init__()
        self.albedo = albedo
        self.fuzz = min(1, max(0, fuzz))
        
    def scatter(self, ray, rec):
        reflected = reflect(ray.direction.unit(), rec.normal + self.fuzz*random_in_unit_sphere())
        scattered = Ray(rec.p, reflected)
        attenuation = self.albedo.value(0, 0, rec.p)
        if scattered.direction.dot(rec.normal) > 0:
            return ScatterRecord(attenuation, scattered)
        return None

def refract(v, n, ni_over_nt):
    uv = v.unit()
    dt = uv.dot(n)
    discriminant = 1 - ni_over_nt*ni_over_nt*(1-dt*dt)
    if discriminant > 0:
        refracted = ni_over_nt*(uv - dt*n) - (math.sqrt(discriminant))*n
        return refracted
    return None

def schlick(cosine, ref_idx):
    r0 = (1 - ref_idx) / (1 + ref_idx)
    r0 *= r0
    #return r0 + (1 - r0) * (1 - cosine)**5
    return r0 + (1 - r0) * pow(1 - cosine, 5)

class Dielectric(Material):
    def __init__(self, ref_idx):
        super().__init__()
        self.ref_idx = ref_idx
        
    def scatter(self, ray, rec):
        reflected = reflect(ray.direction.unit(), rec.normal)
        attenuation = Vec3(1, 1, 1)
        
        if ray.direction.dot(rec.normal) > 0:
            outward_normal = -rec.normal
            ni_over_nt = self.ref_idx
            cosine = self.ref_idx * ray.direction.dot(rec.normal) / ray.direction.length()
        else:
            outward_normal = rec.normal
            ni_over_nt = 1 / self.ref_idx
            cosine = -ray.direction.dot(rec.normal) / ray.direction.length()

        refracted = refract(ray.direction, outward_normal, ni_over_nt)
        
        if refracted:
            reflect_prob = schlick(cosine, self.ref_idx)
        else:
            reflect_prob = 1

        if random.random() < reflect_prob:
            scattered = Ray(rec.p, reflected)
        else:
            scattered = Ray(rec.p, refracted)
            
        return ScatterRecord(attenuation, scattered)
