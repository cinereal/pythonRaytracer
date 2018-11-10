from vec3 import Vec3
from ray import Ray
from texture import Texture
from onb import ONB
from collections import namedtuple
import random
import math

def random_in_unit_sphere():
    while True:
        p = 2 * Vec3(random.random(), random.random(), random.random()) - Vec3(1, 1, 1)
        #if p.squared_length() < 1:
        if p.dot(p) < 1.0:
            return p.unit()

def random_cosine_direction():
    r1 = random.random()
    r2 = random.random()
    z = math.sqrt(1 - r2)
    phi = 2 * math.pi * r1
    x = math.cos(phi) * 2 * math.sqrt(r2)
    y = math.sin(phi) * 2 * math.sqrt(r2)
    return Vec3(x, y, z)

ScatterRecord = namedtuple('ScatterRecord', ['attenuation', 'scattered', 'pdf'])

class Material:
    def scatter(self, ray, rec, albedo, scattered, pdf):
        raise NotImplementedError()

    # probability density function
    def scattering_pdf(self, ray, rec, scattered):
        raise NotImplementedError()

    def emitted(self, ray, rec, u, v, p):
        return Vec3(0, 0, 0)

class Lambertian(Material):
    def __init__(self, albedo):
        self.albedo = albedo

    def scattering_pdf(self, ray, rec, scattered):
        cosine = rec.normal.dot(scattered.direction.unit())
        if cosine < 0:
            cosine = 0
        return cosine / math.pi

##    def scatter(self, ray, rec, alb, scattered, pdf):
##        target = rec.p + rec.normal + random_in_unit_sphere()
##        scattered = Ray(rec.p, (target - rec.p).unit(), ray.time)
##        alb = self.albedo.value(0, 0, rec.p)
##        #attenuation = self.albedo.value(0, 0, rec.p)
##        pdf = rec.normal.dot(scattered.direction) / math.pi
##        return ScatterRecord(alb, scattered, pdf)

    def scatter(self, ray, rec, alb, scattered, pdf):
        uvw = ONB()
        uvw.build_from_w(rec.normal)
        direction = uvw.local(random_cosine_direction())
        scattered = Ray(rec.p, direction.unit(), ray.time)
        alb = self.albedo.value(rec.u, rec.v, rec.p)
        pdf = uvw.w.dot(scattered.direction) / math.pi
        return ScatterRecord(alb, scattered, pdf)

def reflect(v, n):
    return v - 2*v.dot(n)*n

class Metal(Material):
    def __init__(self, albedo, fuzz=0):
        self.albedo = albedo
        self.fuzz = min(1, max(0, fuzz))
        
    def scatter(self, ray, rec):
        reflected = reflect(ray.direction.unit(), rec.normal + self.fuzz*random_in_unit_sphere())
        scattered = Ray(rec.p, reflected, ray.time)
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
    return r0 + (1 - r0) * pow(1 - cosine, 5)

class Dielectric(Material):
    def __init__(self, ref_idx):
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
            scattered = Ray(rec.p, reflected, ray.time)
        else:
            scattered = Ray(rec.p, refracted, ray.time)
        return ScatterRecord(attenuation, scattered)

class DiffuseLight(Material):
    def __init__(self, emit):
        self.emit = emit

    def scatter(self, ray, rec, alb, scattered, pdf):
        return None

    def emitted(self, ray, rec, u, v, p):
        if rec.normal.dot(ray.direction) < 0:
            return self.emit.value(u, v, p)
        else:
            return Vec3(0,0,0)

class Isotropic(Material):
    def __init__(self, albedo):
        self.albedo = albedo

    def scatter(self, ray, rec):
        target = rec.p + rec.normal + random_in_unit_sphere()
        scattered = Ray(rec.p, random_in_unit_sphere(), ray.time)
        attenuation = self.albedo.value(rec.u, rec.v, rec.p)
        return ScatterRecord(attenuation, scattered)
