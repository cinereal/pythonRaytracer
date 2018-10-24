class Ray:
    def __init__(self, origin, direction, time=0):
        self.origin = origin
        self.direction = direction
        self.time = time

    def __call__(self, t):
        return self.origin + t * self.direction

    def point_at_parameter(self, t):
        return self.origin + t * self.direction
