import math
import random
from vec3 import Vec3
#from array import array
#from numpy import zeros

local_random = random.Random(14)

def trilinear_interp(c, u, v, w):
    u = u*u*(3-2*u)
    v = v*v*(3-2*v)
    w = w*w*(3-2*w)
    accum = 0
    for i in range(2):
        for j in range(2):
            for k in range(2):
                accum += (i*u + (1-i)+(1-u))*(j*v + (1-j)*(1-v))*(k*w + (1-k)*(1-w))*c[i][j][k]
    return accum

class Perlin:
    def noise(p):
        u = p.x - math.floor(p.x)
        v = p.y - math.floor(p.y)
        w = p.z - math.floor(p.z)
##        i = int(4*p.x) & 255
##        j = int(4*p.y) & 255
##        k = int(4*p.z) & 255
        i = math.floor(p.x)
        j = math.floor(p.y)
        k = math.floor(p.z)
        c = [[[0,0],[0, 0]],[[0, 0],[0, 0]]]
        #c = numpy.zeros((2,2,2))
        for di in range(2):
            for dj in range(2):
                for dk in range(2):
                    c[di][dj][dk] = ranfloat[perm_x[(i+di) & 255] ^ perm_y[(j+dj) & 255] ^ perm_z[(k+dk) & 255]]
        return trilinear_interp(c, u, v, w)
        #return ranfloat[perm_x[i] ^ perm_y[j] ^ perm_z[k]]

#@staticmethod
def perlin_generate():
    p = []
    for i in range(256):
        p.append(local_random.random())
        #p.append(Vec3(-1 + 2*local_random.random(), -1 + 2*local_random.random(), -1 + 2*local_random.random()).unit())
    return p

def permute(p, n):
    for i in range(n-1, 0, -1):
        target = int(local_random.random()*(i+1))
        tmp = p[i]
        p[i] = p[target]
        p[target] = tmp
    return p

#@staticmethod
def perlin_generate_perm():
    p = []
    for i in range(256):
        p.append(i)
    p = permute(p, 256)
    return p

perm_x = perlin_generate_perm()
perm_y = perlin_generate_perm()
perm_z = perlin_generate_perm()
ranfloat = perlin_generate()
ranvec = perlin_generate()

##def smoothstep(t):
##    return t * t * (3. - 2. * t)
##
##
##def lerp(t, a, b):
##    return a + t * (b - a)

