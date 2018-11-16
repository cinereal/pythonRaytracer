import random
import sys
from ray import Ray
from vec3 import Vec3
from aabb import AABB
from onb import ONB
from pdf import random_to_sphere
from collections import namedtuple
from math import sqrt, atan2, asin, pi, sin, cos, log, fabs
from material import Isotropic

# to compare performance class vs namedtuple
##class HitRecord:
##    def __init__(self, t=0, u=0, v=0, p=Vec3(0,0,0), normal=0):
##        self.t = t
##        self.u = u
##        self.v = v
##        self.p = p
##        self.normal = normal
##        self.material = material

HitRecord = namedtuple('HitRecord', ['t', 'u', 'v', 'p', 'normal', 'material'])

def get_sphere_uv(p):
    phi = atan2(p.z, p.x)
    theta = asin(p.y)
    u = 1 - (phi + pi) / (2 * pi)
    v = (theta + pi / 2) / pi
    return u, v

class Hitable:
    def hit(self, ray, t_min, t_max):
        raise NotImplementedError()
    def bounding_box(self, t0, t1):
        raise NotImplementedError()
    def pdf_value(self, o, v):
        return 0
    def random(self, o):
        return Vec3(1, 0, 0)

class HitableList(Hitable):
    def __init__(self, hit_list):
        self.hit_list = hit_list
        self.list_size = len(self.hit_list)

    def hit(self, ray, t_min, t_max):
        hit_anything = False
        closest_so_far = t_max
        for obj in self.hit_list:
            hit_info = obj.hit(ray, t_min, closest_so_far)
            if hit_info:
                hit_anything = True
                closest_so_far = hit_info.t
                result_info = hit_info
        if hit_anything:
            return result_info
        return False

    def bounding_box(self, t0, t1):
        raise NotImplementedError()
    
    def pdf_value(self, o, v):
        weight = 1 / self.list_size
        sum = 0
        for i in range(self.list_size):
            sum += weight * self.hit_list[i].pdf_value(o, v)
        return sum
    
    def random(self, o):
        index = int(random.random() * self.list_size)
        return self.hit_list[index].random(o)

##    def bounding_box(self, t0, t1, box):
##        temp_box = AABB()
##        if not bounding_box(t0, t1, temp_box):
##            return False
##        else:
##            box = temp_box
##        for i in range(1, 1ist_size):
##            if bounding_box(t0, t1, temp_box):
##                box = surrounding_box(box, temp_box)
##            else:
##                return False
##        return True

# Transformation
class FlipNormals(Hitable):
    def __init__(self, hitable):
        self.hitable = hitable

    def hit(self, ray, t_min, t_max):
        ptr = self.hitable.hit(ray, t_min, t_max)
        if ptr:
            return HitRecord(ptr.t, ptr.u, ptr.v, ptr.p, -ptr.normal, ptr.material)
        return False

    def bounding_box(self, t0, t1, box):
        return box(t0, t1)

class Translate(Hitable):
    def __init__(self, hitable, offset):
        self.hitable = hitable
        self.offset = offset

    def hit(self, ray, t_min, t_max):
        moved_ray = Ray(ray.origin - self.offset, ray.direction, ray.time)
        ptr = self.hitable.hit(moved_ray, t_min, t_max)
        if ptr:
            return HitRecord(ptr.t, ptr.u, ptr.v, ptr.p+self.offset, ptr.normal, ptr.material)
        return False

    def bounding_box(self, t0, t1, box):
        if box:
            box = box(box.min + self.offset, box.max + self.offset)
        return False

class RotateY(Hitable):
    def __init__(self, hitable, angle):
        self.hitable = hitable
        self.radians = (pi / 180) * angle
        self.sin_theta = sin(self.radians)
        self.cos_theta = cos(self.radians)
##        bbox = self.hitable.bounding_box(0, 1)
##        sys_f = sys.float_info.max
##        min_b = Vec3(sys_f, sys_f,sys_f)
##        max_b = -minb
##        if bbox:
##            for i in range(2):
##                for j in range(2):
##                    for k in range(2):
##                        x = i*bbox.max.x + (1-i)*bbox.min.x
##                        y = j*bbox.max.y + (1-j)*bbox.min.y
##                        z = k*bbox.max.z + (1-k)*bbox.min.z
##                        newx = self.cos_theta * x + self.sin_theta * z
##                        newz = -self.sin_theta * x + self.cos_theta * z
##                        tester = Vec3(newx, y, newz)
##                        for c in range(3):
##                            if tester[c] > max[c]:
##                                max[c] = tester[c]
##                            if tester[c] < min[c]:
##                                min[c] = tester[c]
##            self.box = AABB(min_b, max_B)
##        else:
##            self.box = None

    def hit(self, ray, t_min, t_max):
        ox = self.cos_theta * ray.origin.x - self.sin_theta * ray.origin.z
        oz = self.sin_theta * ray.origin.x + self.cos_theta * ray.origin.z
        origin = Vec3(ox, ray.origin.y, oz)
        dx = self.cos_theta * ray.direction.x - self.sin_theta * ray.direction.z
        dz = self.sin_theta * ray.direction.x + self.cos_theta * ray.direction.z
        direction = Vec3(dx, ray.direction.y, dz)
        rotated_ray = Ray(origin, direction, ray.time)
        ptr = self.hitable.hit(rotated_ray, t_min, t_max)
        if ptr:
            px = self.cos_theta * ptr.p.x + self.sin_theta * ptr.p.z
            pz = -self.sin_theta * ptr.p.x + self.cos_theta * ptr.p.z
            nx = self.cos_theta * ptr.normal.x + self.sin_theta * ptr.normal.z
            nz = -self.sin_theta * ptr.normal.x + self.cos_theta * ptr.normal.z
            p = Vec3(px, ptr.p.y, pz)
            normal = Vec3(nx, ptr.normal.y, nz)
            return HitRecord(ptr.t, ptr.u, ptr.v, p, normal, ptr.material)
        return False

    def bounding_box(self, t0, t1, box):
        box = box
        return True


class XYRect(Hitable):
    def __init__(self, x0, x1, y0, y1, k, material=None):
        self.x0 = x0
        self.x1 = x1
        self.y0 = y0
        self.y1 = y1
        self.k = k
        self.material = material

    def hit(self, ray, t0, t1):
        t = (self.k - ray.origin.z) / ray.direction.z
        if t < t0 or t > t1:
            return False
        x = ray.origin.x + t * ray.direction.x
        y = ray.origin.y + t * ray.direction.y
        if x < self.x0 or x > self.x1 or y < self.y0 or y > self.y1:
            return False
        u = (x - self.x0) / (self.x1 - self.x0)
        v = (y - self.y0) / (self.y1 - self.y0)
        p = ray.point_at_parameter(t)
        normal = Vec3(0,0,1)
        return HitRecord(t, u, v, p, normal, self.material)

    def bounding_box(self, t0, t1, box):
        box = AABB(Vec3(x0, y0, k-0.0001), Vec3(x1, y1, k+0.0001))
        return True
        
class XZRect(Hitable):
    def __init__(self, x0, x1, z0, z1, k, material=None):
        self.x0 = x0
        self.x1 = x1
        self.z0 = z0
        self.z1 = z1
        self.k = k
        self.material = material

    def hit(self, ray, t0, t1):
        t = (self.k - ray.origin.y) / ray.direction.y
        if t < t0 or t > t1:
            return False
        x = ray.origin.x + t * ray.direction.x
        z = ray.origin.z + t * ray.direction.z
        if x < self.x0 or x > self.x1 or z < self.z0 or z > self.z1:
            return False
        u = (x - self.x0) / (self.x1 - self.x0)
        v = (z - self.z0) / (self.z1 - self.z0)
        p = ray.point_at_parameter(t)
        normal = Vec3(0,1,0)
        return HitRecord(t, u, v, p, normal, self.material)

    def bounding_box(self, t0, t1, box):
        box = AABB(Vec3(x0, k-0.0001, z0), Vec3(x1, k+0.0001, z1))
        return True

    def pdf_value(self, o, v):
        rec = self.hit(Ray(o, v), 0.001, sys.float_info.max)
        if rec:
            area = (self.x1-self.x0)*(self.z1-self.z0)
            distance_squared = rec.t * rec.t * v.squared_length()
            cosine = fabs(v.dot(rec.normal) / v.length())
            return distance_squared / (cosine * area)
        return 0

    def random(self, o):
        random_point = Vec3(self.x0 + random.random() * (self.x1-self.x0), self.k, self.z0 + random.random() * (self.z1-self.z0))
        return random_point - o

class YZRect(Hitable):
    def __init__(self, y0, y1, z0, z1, k, material=None):
        self.y0 = y0
        self.y1 = y1
        self.z0 = z0
        self.z1 = z1
        self.k = k
        self.material = material

    def hit(self, ray, t0, t1):
        t = (self.k - ray.origin.x) / ray.direction.x
        if t < t0 or t > t1:
            return False
        y = ray.origin.y + t * ray.direction.y
        z = ray.origin.z + t * ray.direction.z
        if y < self.y0 or y > self.y1 or z < self.z0 or z > self.z1:
            return False
        u = (y - self.y0) / (self.y1 - self.y0)
        v = (z - self.z0) / (self.z1 - self.z0)
        p = ray.point_at_parameter(t)
        normal = Vec3(1,0,0)
        return HitRecord(t, u, v, p, normal, self.material)
    
    def bounding_box(self, t0, t1, box):
        box = AABB(Vec3(k-0.0001, y0, z0), Vec3(k+0.0001, y1, z1))
        return True

class Box(Hitable):
    def __init__(self, p0, p1, material=None):
        self.p0 = p0
        self.p1 = p1
        self.ptr = material

    def hit(self, ray, t_min, t_max):
        return self.box().hit(ray, t_min, t_max)

    def box(self):
        hit_list = []
        hit_list.append(XYRect(self.p0.x, self.p1.x, self.p0.y, self.p1.y, self.p1.z, self.ptr))
        hit_list.append(FlipNormals(XYRect(self.p0.x, self.p1.x, self.p0.y, self.p1.y, self.p0.z, self.ptr)))
        hit_list.append(XZRect(self.p0.x, self.p1.x, self.p0.z, self.p1.z, self.p1.y, self.ptr))
        hit_list.append(FlipNormals(XZRect(self.p0.x, self.p1.x, self.p0.z, self.p1.z, self.p0.y, self.ptr)))
        hit_list.append(YZRect(self.p0.y, self.p1.y, self.p0.z, self.p1.z, self.p1.x, self.ptr))
        hit_list.append(FlipNormals(YZRect(self.p0.y, self.p1.y, self.p0.z, self.p1.z, self.p0.x, self.ptr)))
        return HitableList(hit_list)
        
    def bounding_box(self, t0, t1, box):
        box = AABB(self.pmin, self.pmax)
        return True
    

class Sphere(Hitable):
    def __init__(self, center, radius, material=None):
        self.center = center
        self.radius = radius
        self.material = material

    def hit(self, ray, t_min, t_max):
        oc = ray.origin - self.center
        a = ray.direction.dot(ray.direction)
        b = oc.dot(ray.direction)
        c = oc.dot(oc) - self.radius*self.radius
        discriminant = b*b - a*c
        if discriminant > 0:
            dis_sqrt = sqrt(discriminant)
            temp = (-b - dis_sqrt) / a
            if t_min < temp < t_max:
                t = temp
                p = ray.point_at_parameter(t)
                u, v = get_sphere_uv((p-self.center)/self.radius)
                normal = (p - self.center) / self.radius
                return HitRecord(t, u, v, p, normal, self.material)
            temp = (-b + dis_sqrt) / a
            if t_min < temp < t_max:
                t = temp
                p = ray.point_at_parameter(t)
                u, v = get_sphere_uv((p-self.center)/self.radius)
                normal = (p - self.center) / self.radius
                return HitRecord(t, u, v, p, normal, self.material)
        return False

    def bounding_box(self, t0, t1, box):
        box = AABB(self.center - Vec3(self.radius, self.radius, self.radius), self.center + Vec3(self.radius, self.radius, self.radius))
        return True

    def pdf_value(self, o, v):
        rec = self.hit(Ray(o, v), 0.001, sys.float_info.max)
        if rec:
            cos_theta_max = sqrt(1 - self.radius * self.radius / (self.center - o).squared_length())
            solid_angle = 2 * pi * (1 - cos_theta_max)
            return 1 / solid_angle
        return 0

    def random(self, o):
        direction = self.center - o
        distant_squared = direction.squared_length()
        uvw = ONB()
        uvw.build_from_w(direction)
        return uvw.local(random_to_sphere(self.radius, distant_squared))
        

class MovingSphere(Hitable):
    def __init__(self, center0, center1, time0, time1, radius, material=None):
        self.time0 = time0
        self.time1 = time1
        self.center0 = center0
        self.center1 = center1
        self.radius = radius
        self.material = material

    def center(self, time):
        return self.center0 + ((time - self.time0) / (self.time1 - self.time0)) * (self.center1 - self.center0)

    def hit(self, ray, t_min, t_max):
        oc = ray.origin - self.center(ray.time)
        a = ray.direction.dot(ray.direction)
        b = 2 * oc.dot(ray.direction)
        c = oc.dot(oc) - self.radius*self.radius
        discriminant = b*b - 4*a*c
        if discriminant > 0:
            dis_sqrt = sqrt(discriminant)
            temp = (-b - dis_sqrt) / (2*a)
            if(t_min < temp < t_max):
                t = temp
                p = ray.point_at_parameter(t)
                normal = (p - self.center(ray.time)) / self.radius
                return HitRecord(t, p, normal, self.material)
            temp = (-b + dis_sqrt) / (2*a)
            if t_min < temp < t_max:
                t = temp
                p = ray.point_at_parameter(t)
                normal = (p - self.center(ray.time)) / self.radius
                return HitRecord(t, p, normal, self.material)
        return False
    
    def bounding_box(self, t0, t1, box):
        box0 = AABB(self.center(t0) - Vec3(self.radius, self.radius, self.radius), self.center(t0) + Vec3(self.radius, self.radius, self.radius))
        box1 = AABB(self.center(t1) - Vec3(self.radius, self.radius, self.radius), self.center(t1) + Vec3(self.radius, self.radius, self.radius))
        box = surrounding_box(box0, box1)
        return True
    
class ConstantMedium(Hitable):
    def __init__(self, boundary, density, texture):
        self.boundary = boundary
        self.density = density
        self.material = Isotropic(texture)

    def hit(self, ray, t_min, t_max):
        rec1 = self.boundary.hit(ray, -sys.float_info.max, sys.float_info.max)
        if rec1:
            rec2 = self.boundary.hit(ray, rec1.t + 0.0001, sys.float_info.max)
            if rec2:
                rec1_t = max(rec1.t, t_min)
                rec2_t = min(rec2.t, t_max)
                if rec1_t < 0:
                    return False
                distInsideBoundary = (rec2_t - rec1_t) * ray.direction.length()
                hitDistance = -(1.0 / self.density) * log(random.random())
                if hitDistance < distInsideBoundary:
                    t = rec2_t + hitDistance / ray.direction.length()
                    p = ray.point_at_parameter(t)
                    normal = Vec3(1,0,0)
                    return HitRecord(t, 0, 0, p, normal, self.material)
        return False

    def bounding_box(self, sceneTime0, sceneTime1):
        return self.boundary.bounding_box(sceneTime0, sceneTime1)


