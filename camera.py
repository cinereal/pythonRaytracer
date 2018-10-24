from vec3 import Vec3
from ray import Ray
import math
import random

class Camera:
    def __init__(self):
        self._lower_left_corner = Vec3(-2, -1, -1)
        self._horizontal = Vec3(4, 0, 0)
        self._vertical = Vec3(0, 2, 0)
        self._origin = Vec3(0, 0, 0)

    def get_ray(self, u, v):
        return Ray(self._origin, self._lower_left_corner + u*self._horizontal + v*self._vertical)

class FOVCamera:
    def __init__(self, vfov, aspect):
        self.theta = vfov * math.pi/180
        half_height = math.tan(self.theta/2)
        half_width = aspect * half_height
        
        self._lower_left_corner = Vec3(-half_width, -half_height, -1)
        self._horizontal = Vec3(2*half_width, 0, 0)
        self._vertical = Vec3(0, 2*half_height, 0)
        self._origin = Vec3(0, 0, 0)

    def get_ray(self, u, v):
        return Ray(self._origin, self._lower_left_corner + u*self._horizontal + v*self._vertical)

class PosCamera:
    def __init__(self, lookfrom, lookat, vup, vfov, aspect):
        self.theta = vfov * math.pi/180
        half_height = math.tan(self.theta/2)
        half_width = aspect * half_height
        self._origin = lookfrom

        w = (lookfrom - lookat).unit()
        u = vup.cross(w).unit()
        v = w.cross(u)
        
        self._lower_left_corner = Vec3(-half_width, -half_height, -1)
        self._lower_left_corner = self._origin - half_width*u - half_height*v - w
        self._horizontal = 2*half_width*u
        self._vertical = 2*half_height*v

    def get_ray(self, s, t):
        return Ray(self._origin, self._lower_left_corner + s*self._horizontal + t*self._vertical - self._origin)

def random_in_unit_disk():
    while True:
        p = 2 * Vec3(random.random(), random.random(), 0) - Vec3(1, 1, 0)
        if p.dot(p) < 1:
            return p
        
class DofCamera:
    def __init__(self, lookfrom, lookat, vup, vfov, aspect, aperture, focus_dist):
        self._lens_radius = aperture / 2
        self.theta = vfov * math.pi/180
        half_height = math.tan(self.theta/2)
        half_width = aspect * half_height
        self._origin = lookfrom

        w = (lookfrom - lookat).unit()
        self._u = u = vup.cross(w).unit()
        self._v = v = w.cross(u)

        self._lower_left_corner = self._origin - half_width*focus_dist*u - half_height*focus_dist*v - focus_dist*w
        self._horizontal = 2*half_width*focus_dist*u
        self._vertical = 2*half_height*focus_dist*v

    def get_ray(self, s, t):
        rd = self._lens_radius * random_in_unit_disk()
        offset = rd.x * self._u +  rd.y * self._v
        return Ray(self._origin + offset, self._lower_left_corner + s*self._horizontal + t*self._vertical - self._origin - offset)

class MoBlurCamera:
    def __init__(self, lookfrom, lookat, vup, vfov, aspect, aperture, focus_dist, time0, time1):
        self.time0 = time0
        self.time1 = time1
        self._lens_radius = aperture / 2
        self.theta = vfov * math.pi/180
        half_height = math.tan(self.theta/2)
        half_width = aspect * half_height
        self._origin = lookfrom

        w = (lookfrom - lookat).unit()
        self._u = u = vup.cross(w).unit()
        self._v = v = w.cross(u)

        self._lower_left_corner = self._origin - half_width*focus_dist*u - half_height*focus_dist*v - focus_dist*w
        self._horizontal = 2*half_width*focus_dist*u
        self._vertical = 2*half_height*focus_dist*v

    def get_ray(self, s, t):
        rd = self._lens_radius * random_in_unit_disk()
        offset = rd.x * self._u +  rd.y * self._v
        time = self.time0 + random.random() * (self.time1 - self.time0)
        return Ray(self._origin + offset, self._lower_left_corner + s*self._horizontal + t*self._vertical - self._origin - offset, time)

