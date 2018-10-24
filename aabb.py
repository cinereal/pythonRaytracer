from ray import Ray

class AABB():
##    axis aligned bounding boxes
    def __init__(self, min_hit, max_hit):
        self.min_hit = min_hit
        self.max_hit = max_hit

    def ffmin(self, a, b):
        if a < b:
            return a
        return b

    def ffmax(self, a, b):
        if a > b:
            return a
        else:
            return b

##    def hit(self, ray, t_min, t_max):
##        for a in range(0, 3):
##            t0 = self.ffmin(())
        
    def hit(self, ray, t_min, t_max):
        for a in range(0, 3):
            invD = 1 / ray.direction[a]
            t0 = (self.min_hit[a] - ray.origin[a]) * invD
            t1 = (self.max_hit[a] - ray.origin[a]) * invD
            if invD < 0:
                t0, t1 = t1, t0
            if t0 > t_min:
                t_min = t0
            if t1 < t_max:
                t_max = t1
            if tmax <= tmin:
                return False
        return True


    def surrounding_box(self, box0, box1):
        small = Vec3( self.ffmin(box0.min().x, box1.min().x),
                      self.ffmin(box0.min().y, box1.min().y),
                      self.ffmin(box0.min().z, box1.min().z)
               )
        big = Vec3( self.ffmax(box0.max().x, box1.max().x),
                    self.ffmax(box0.max().y, box1.max().y),
                    self.ffmax(box0.max().z, box1.max().z)
               )
        return aabb(small,big)
