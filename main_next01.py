import sys
import math
import random
from time import time
from multiprocessing import Pool
import cProfile
from ray import Ray
from vec3 import Vec3
from hitable import Hitable, HitableList, Sphere, MovingSphere, XYRect, XZRect, YZRect, FlipNormals, Box, Translate, RotateY, ConstantMedium
from camera import Camera, FOVCamera, PosCamera, DofCamera, MoBlurCamera
from material import Lambertian, Metal, Dielectric, DiffuseLight
from texture import ConstantTexture, CheckerTexture, NoiseTexture
from pdf import PDF, CosinePDF, HitablePDF, MixturePDF

#local_random = random.Random()
#local_random.seed(14)

def float_to_int8(value):
    return min(max(int(value * 255), 0), 255)

def color_to_string(color):
    red = float_to_int8(color.x)
    green = float_to_int8(color.y)
    blue = float_to_int8(color.z)
    return '{} {} {}'.format(red, green, blue)

def write_image(name, width, height, colors):
    ppm_header = 'P3\n{} {}\n255\n'.format(width, height)
    ppm_colors = '\n'.join(color_to_string(color) for color in colors)
    with open(name, 'w') as image:
        image.write(ppm_header + ppm_colors + '\n')

def random_scene():
    hit_list = HitableList()
    checker = CheckerTexture(ConstantTexture(Vec3(0.2, 0.3, 0.1)), ConstantTexture(Vec3(0.9, 0.9, 0.9)))
    #constant_color = ConstantTexture(Vec3(0.2, 0.3, 0.1)).value()
    hit_list.append(Sphere(Vec3(0, -1000, 0), 1000, Lambertian(checker)))
    for a in range(-10, 10):
        for b in range(-10, 10):
            choose_mat = random.random()
            center = Vec3(a+0.9*random.random(), 0.2, b+0.9*random.random())
            if (center - Vec3(4, 0.2, 0)).length() > 0.9:
                if choose_mat < 0.8:
                    hit_list.append(MovingSphere(center, center+Vec3(0, 0.5*random.random(), 0), 0, 1, 0.2, Lambertian(ConstantTexture(Vec3(random.random()*random.random(), random.random()*random.random(), random.random()*random.random())))))
                elif choose_mat <0.95:
                    hit_list.append(Sphere(center, 0.2, Metal(Vec3(0.5*(1+random.random()), 0.5*(1+random.random()), 0.5*(1+random.random())), 0.5*random.random())))
                else:
                    hit_list.append(Sphere(center, 0.2, Dielectric(1.5)))
    hit_list.append(Sphere(Vec3(0, 1, 0), 1, Dielectric(1.5)))
    hit_list.append(Sphere(Vec3(-4, 1, 0), 1, Lambertian(ConstantTexture(Vec3(0.4, 0.2, 0.1)))))
    hit_list.append(Sphere(Vec3(4, 1, 0), 1, Metal(Vec3(0.7, 0.6, 0.5), 0)))
    return hit_list

def two_sphere():
    checker = CheckerTexture(ConstantTexture(Vec3(0.2, 0.3, 0.1)), ConstantTexture(Vec3(0.9, 0.9, 0.9)))
    hit_list = HitableList()
    hit_list.append(Sphere(Vec3(0, -10, 0), 10, Lambertian(checker)))
    hit_list.append(Sphere(Vec3(0, 10, 0), 10, Lambertian(checker)))
    return hit_list

def two_perlin_sphere():
    #pertext = CheckerTexture(ConstantTexture(Vec3(0.2, 0.3, 0.1)), ConstantTexture(Vec3(0.9, 0.9, 0.9)))
    pertext = NoiseTexture()
    hit_list = HitableList()
    hit_list.append(Sphere(Vec3(0, -1000, 0), 1000, Lambertian(pertext)))
    hit_list.append(Sphere(Vec3(0, 2, 0), 2, Lambertian(pertext)))
    return hit_list

def simple_light():
    checker = CheckerTexture(ConstantTexture(Vec3(0.2, 0.3, 0.1)), ConstantTexture(Vec3(0.9, 0.9, 0.9)))
    constant_texture = ConstantTexture(Vec3(4, 4, 4))
    hit_list = HitableList()
    hit_list.append(Sphere(Vec3(0, -1000, 0), 1000, Lambertian(checker)))
    hit_list.append(Sphere(Vec3(0, 2, 0), 2, Lambertian(checker)))
    hit_list.append(Sphere(Vec3(0, 7, 0), 2, DiffuseLight(constant_texture)))
    hit_list.append(XYRect(3, 5, 1, 3, -3, DiffuseLight(constant_texture)))
    return hit_list

def cornell_box():
    hit_list = HitableList()
    red = Lambertian(ConstantTexture(Vec3(0.65, 0.05, 0.05)))
    white = Lambertian(ConstantTexture(Vec3(0.73, 0.73, 0.73)))
    green = Lambertian(ConstantTexture(Vec3(0.12, 0.45, 0.15)))
    light = DiffuseLight(ConstantTexture(Vec3(15, 15, 15)))
    #gray = ConstantTexture(Vec3(0.35, 0.35, 0.35))
    hit_list.append(FlipNormals(YZRect(0, 555, 0, 555, 555, green)))
    hit_list.append(YZRect(0, 555, 0, 555, 0, red))
    hit_list.append(FlipNormals(XZRect(213, 343, 227, 332, 554, light)))
    hit_list.append(FlipNormals(XZRect(0, 555, 0, 555, 555, white)))
    hit_list.append(XZRect(0, 555, 0, 555, 0, white))
    hit_list.append(FlipNormals(XYRect(0, 555, 0, 555, 555, white)))
    #hit_list.append(Sphere(Vec3(200, 100, 250), 100, Lambertian(gray)))
    #hit_list.append(Sphere(Vec3(200, 100, 200), 100, Dielectric(1.5)))
    #hit_list.append(Sphere(Vec3(200, 100, 280), 100, Metal(gray, 0)))
    hit_list.append(Translate(RotateY((Box(Vec3(0, 0, 0), Vec3(165, 165, 165), white)), -18), Vec3(130, 0, 65)))
    hit_list.append(Translate(RotateY((Box(Vec3(0, 0, 0), Vec3(165, 330, 165), white)), 15), Vec3(265, 0, 295)))
    return hit_list

def cornell_smoke():
    hit_list = HitableList()
    red = Lambertian(ConstantTexture(Vec3(0.65, 0.05, 0.05)))
    white = Lambertian(ConstantTexture(Vec3(0.73, 0.73, 0.73)))
    green = Lambertian(ConstantTexture(Vec3(0.12, 0.45, 0.15)))
    light = DiffuseLight(ConstantTexture(Vec3(15, 15, 15)))
    gray = ConstantTexture(Vec3(0.35, 0.35, 0.35))
    hit_list.append(FlipNormals(YZRect(0, 555, 0, 555, 555, green)))
    hit_list.append(YZRect(0, 555, 0, 555, 0, red))
    hit_list.append(XZRect(113, 443, 127, 432, 554, light))
    hit_list.append(FlipNormals(XZRect(0, 555, 0, 555, 555, white)))
    hit_list.append(XZRect(0, 555, 0, 555, 0, white))
    hit_list.append(FlipNormals(XYRect(0, 555, 0, 555, 555, white)))
    b1 = Translate(RotateY((Box(Vec3(0, 0, 0), Vec3(165, 165, 165), white)), -18), Vec3(130, 0, 65))
    b2 = Translate(RotateY((Box(Vec3(0, 0, 0), Vec3(165, 330, 165), white)), 15), Vec3(265, 0, 295))
    hit_list.append(ConstantMedium(b1, 0.01, ConstantTexture(Vec3(1, 1, 1))))
    hit_list.append(ConstantMedium(b2, 0.01, ConstantTexture(Vec3(0, 0, 0))))
    return hit_list

##def color(ray, world, depth):
##    rec = world.hit(ray, 0.001, sys.float_info.max)
##    if rec:
##        emitted = rec.material.emitted(rec.u, rec.v, rec.p)
##        scattered = Ray(rec.p, Vec3(0,0,0), ray.time)
##        pdf = 1.0
##        albedo = Vec3()
##        if depth < 8:
##            scatter_rec = rec.material.scatter(ray, rec, albedo, scattered, pdf)
##            if scatter_rec:
##                return emitted +  rec.material.scattering_pdf(ray, rec, scatter_rec.scattered) * scatter_rec.attenuation * color(scatter_rec.scattered, world, depth+1) / pdf
##            else:
##                return emitted
##        else:
##            return Vec3(0, 0, 0)
##    #unit_direction = ray.direction.unit()
##    #t = 0.5 * (unit_direction.y + 1)
##    #return (1-t)*Vec3(1, 1, 1) + t*Vec3(0.5, 0.7, 1.0)
##    return Vec3(0, 0, 0)

##def color(ray, world, depth):
##    rec = world.hit(ray, 0.001, sys.float_info.max)
##    if rec:
##        emitted = rec.material.emitted(ray, rec, rec.u, rec.v, rec.p)
##        scattered = None
##        pdf = 1
##        albedo = Vec3()
##        scatter_rec = rec.material.scatter(ray, rec, albedo, scattered, pdf)
##        if depth < 8 and scatter_rec:
##            on_light = Vec3(213 + random.random() * (343-213), 554, 227 + random.random() * (332-227))
##            to_light = on_light - rec.p
##            distance_squared = to_light.squared_length()
##            to_light.unit()
##            if to_light.dot(rec.normal) < 0:
##                return emitted
##            light_area = (343-213) * (332-227)
##            light_cosine = math.fabs(to_light.y)
##            if light_cosine < 0.000001:
##                return emitted
##            pdf = distance_squared / (light_cosine * light_area)
##            scattered = Ray(rec.p, to_light, ray.time)
##            return emitted + rec.material.scattering_pdf(ray, rec, scattered) * (0.01*scatter_rec.attenuation) * color(scattered, world, depth+1) / pdf
##        else:
##            return emitted
##    return Vec3(0, 0, 0)

def color(ray, world, depth):
    rec = world.hit(ray, 0.001, sys.float_info.max)
    if rec:
        emitted = rec.material.emitted(ray, rec, rec.u, rec.v, rec.p)
        scattered = None
        pdf_val = 1
        albedo = Vec3()
        scatter_rec = rec.material.scatter(ray, rec, albedo, scattered, pdf_val)
        if depth < 8 and scatter_rec:
            light_shape = XZRect(213, 343, 227, 332, 554, 0)
            p0 = HitablePDF(light_shape, rec.p)
            p1 = CosinePDF(rec.normal)
            p = MixturePDF(p0, p1)
            scattered = Ray(rec.p, p.generate(), ray.time)
            pdf_val = p.value(scattered.direction)
            return emitted + rec.material.scattering_pdf(ray, rec, scattered) * scatter_rec.attenuation * color(scattered, world, depth+1) / pdf_val
        else:
            return emitted
    return Vec3(0, 0, 0)

# width
nx = 500
# height
ny = 500
# samples
ns = 200
# cpu threads
threads = 15
# filename
name = 'pdf1.ppm'
# total pixels
pixels=nx*ny
#tile size y
tile_y = 2
left_y = ny%tile_y
tiles_y = int((ny-left_y)/tile_y)

y_tile_list = []
for i in range(tiles_y):
    y_tile_list.append(ny-i*tile_y)

#rowsPerThread = int(ny/threads)
#print("{} rows per thread".format(rowsPerThread))

##list_hit = [
##    Sphere(Vec3(0, 0, -1), 0.5, Lambertian(Vec3(0.1, 0.2, 0.5))),
##    Sphere(Vec3(0, -100.5, -1), 100, Lambertian(Vec3(0.8, 0.8, 0))),
##    Sphere(Vec3(1, 0, -1), 0.5, Metal(Vec3(0.8, 0.6, 0.2), 0.2)),
##    Sphere(Vec3(-1, 0, -1), 0.5, Dielectric(1.5)),
##    Sphere(Vec3(-1, 0, -1), -0.45, Dielectric(1.5))
##]

#world = HitableList(list_hit)
##world = random_scene()

#cam = FOVCamera(90, nx/ny)
##lookfrom = Vec3(13,2,3)
##lookat = Vec3(0,0,0)
##dist_to_focus = 10
##aperture = 0.08

# test scene two_sphere
##world = simple_light()
##lookfrom = Vec3(22,3,3)
##lookat = Vec3(0,2,0)
##dist_to_focus = 10
##aperture = 0.0

# cornell box
world = cornell_box()
lookfrom = Vec3(278,278,-800)
lookat = Vec3(278,278,0)
dist_to_focus = 10
aperture = 0.0
vfov = 40

cam = MoBlurCamera(lookfrom, lookat, Vec3(0,1,0), vfov, nx/ny, aperture, dist_to_focus, 0, 1)

col = []
    
def render_loop(start):
    local_col = []
    for y in range(start, start-tile_y, -1):
        for x in range(nx):
            c = Vec3()
            for s in range(ns):
                u = (x + random.random()) / nx
                v = (y + random.random()) / ny
                r= cam.get_ray(u, v)
                c += color(r, world, 0)
            c /= ns
            c = Vec3(math.sqrt(c.x), math.sqrt(c.y), math.sqrt(c.z))
            local_col.append(c)
    return local_col

print("Hitable Objects: {}".format(len(world)))
print("Total Tiles: {}".format(tiles_y))

if __name__ == '__main__':
    random.seed(14)
    start = time()
    with Pool(threads) as p:
        col.extend(p.map(render_loop, y_tile_list))
##    col.extend(map(render_loop, y_tile_list))
    print("Time taken = {0:.5f}".format(time() - start))
    all_col = []
    for i in col:
        all_col.extend(i)
    write_image(name, nx, ny, all_col)

# cProfile.run('main_loop()')

