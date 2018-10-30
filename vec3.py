from math import sqrt
import numbers

class Vec3:
    def __init__(self, x=0, y=0, z=0):
        (self.x, self.y, self.z) = (x, y, z)

    def __repr__(self):
        return '{}({}, {}, {})'.format(__class__.__name__, self.x, self.y, self.z)

    # +u
    def __pos__(self):
        return self

    # -u
    def __neg__(self):
        return Vec3(-self.x, -self.y, -self.z)

    # u + v
    def __add__(self, other):
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    # u - v
    def __sub__(self, other):
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    # u * v
    def __mul__(self, other):
        return Vec3(self.x * other.x, self.y * other.y, self.z * other.z)

    # k * u
    def __rmul__(self, other):
        return Vec3(other * self.x, other * self.y, other * self.z)

    # u / k or u / v
    def __truediv__(self, other):
        if isinstance(other, numbers.Real):
            return Vec3(self.x / other, self.y / other, self.z / other)
        return Vec3(self.x / other.x, self.y / other.y, self.z / other.z)

    def length(self):
        return sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def squared_length(self):
        return self.x * self.x + self.y * self.y + self.z * self.z

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        x = self.y * other.z - self.z * other.y
        y = self.z * other.x - self.x * other.z
        z = self.x * other.y - self.y * other.x
        return Vec3(x, y, z)

    def unit(self):
        l = self.length()
        return self / l
