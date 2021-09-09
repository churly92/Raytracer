import numpy as np
from gl import WHITE, V3

class DirectionalLight(object):
    def __init__(self, direction = V3(0,-1,0), intensity = 1, color = WHITE):
        self.direction = direction / np.linalg.norm(direction)
        self.intensity = intensity
        self.color = color

class AmbientLight(object):
    def __init__(self, strength = 0, color = WHITE):
        self.strength = strength
        self.color = color

class PointLight(object):
    # Luz con punto de origen que va en todas direcciones
    def __init__(self, position = V3(0,0,0), intensity = 1, color = WHITE):
        self.position = position
        self.intensity = intensity
        self.color = color

class Material(object):
    def __init__(self, diffuse = WHITE, spec = 1):
        self.diffuse = diffuse
        self.spec = spec


class Intersect(object):
    def __init__(self, distance, point, normal, sceneObject):
        self.distance = distance
        self.point = point
        self.normal = normal
        self.sceneObject = sceneObject

class Sphere(object):
    def __init__(self, center, radius, material = Material()):
        self.center = center
        self.radius = radius
        self.material = material

    def ray_intersect(self, orig, dir):

        L = np.subtract(self.center, orig)
        l = np.linalg.norm(L)

        tca = np.dot(L, dir)

        d = (l**2 - tca**2)
        if d > self.radius ** 2:
            return None

        thc = (self.radius**2 - d) ** 0.5
        t0 = tca - thc
        t1 = tca + thc

        if t0 < 0:
            t0 = t1

        if t0 < 0:
            return None

        # P = O + t * D
        hit = np.add(orig, t0 * np.array(dir) )
        normal = np.subtract( hit, self.center )
        normal = normal / np.linalg.norm(normal) #la normalizo

        return Intersect( distance = t0,
                          point = hit,
                          normal = normal,
                          sceneObject = self)





        