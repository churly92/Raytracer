import struct
from collections import namedtuple

from obj import Obj

import numpy as np
from numpy import sin, cos, tan
import random

STEPS = 1

V2 = namedtuple('Point2', ['x', 'y'])
V3 = namedtuple('Point3', ['x', 'y', 'z'])
V4 = namedtuple('Point4', ['x', 'y', 'z', 'w'])

def char(c):
    # 1 byte
    return struct.pack('=c', c.encode('ascii'))

def word(w):
    #2 bytes
    return struct.pack('=h', w)

def dword(d):
    # 4 bytes
    return struct.pack('=l', d)

def _color(r, g, b):
    # Acepta valores de 0 a 1
    # Se asegura que la información de color se guarda solamente en 3 bytes
    return bytes([ int(b * 255), int(g* 255), int(r* 255)])

def baryCoords(A, B, C, P):
    # u es para A, v es para B, w es para C
    try:
        #PCB/ABC
        u = (((B.y - C.y) * (P.x - C.x) + (C.x - B.x) * (P.y - C.y)) /
            ((B.y - C.y) * (A.x - C.x) + (C.x - B.x) * (A.y - C.y)))

        #PCA/ABC
        v = (((C.y - A.y) * (P.x - C.x) + (A.x - C.x) * (P.y - C.y)) /
            ((B.y - C.y) * (A.x - C.x) + (C.x - B.x) * (A.y - C.y)))

        w = 1 - u - v
    except:
        return -1, -1, -1

    return u, v, w

def reflectVector(normal, dirVector):
    # R = 2 * ( N . L) * N - L
    reflect = 2 * np.dot(normal, dirVector)
    reflect = np.multiply(reflect, normal)
    reflect = np.subtract(reflect, dirVector)
    reflect = reflect / np.linalg.norm(reflect)
    return reflect


BLACK = _color(0,0,0)
WHITE = _color(1,1,1)


class Raytracer(object):
    def __init__(self, width, height):
        #Constructor
        self.curr_color = WHITE
        self.clear_color = BLACK
        self.glCreateWindow(width, height)

        self.camPosition = V3(0,0,0)
        self.fov = 60

        self.background = None

        self.scene = []

        self.pointLights = []
        self.ambLight = None
        self.dirLight = None


    def glFinish(self, filename):
        #Crea un archivo BMP y lo llena con la información dentro de self.pixels
        with open(filename, "wb") as file:
            # Header
            file.write(bytes('B'.encode('ascii')))
            file.write(bytes('M'.encode('ascii')))
            file.write(dword(14 + 40 + (self.width * self.height * 3)))
            file.write(dword(0))
            file.write(dword(14 + 40))

            # InfoHeader
            file.write(dword(40))
            file.write(dword(self.width))
            file.write(dword(self.height))
            file.write(word(1))
            file.write(word(24))
            file.write(dword(0))
            file.write(dword(self.width * self.height * 3))
            file.write(dword(0))
            file.write(dword(0))
            file.write(dword(0))
            file.write(dword(0))

            # Color Table
            for y in range(self.height):
                for x in range(self.width):
                    file.write(self.pixels[x][y])


    def glCreateWindow(self, width, height):
        self.width = width
        self.height = height
        self.glClear()
        self.glViewport(0,0, width, height)


    def glViewport(self, x, y, width, height):
        self.vpX = int(x)
        self.vpY = int(y)
        self.vpWidth = int(width)
        self.vpHeight = int(height)


    def glClearColor(self, r, g, b):
        self.clear_color = color(r, g, b)


    def glClear(self):
        #Crea una lista 2D de pixeles y a cada valor le asigna 3 bytes de color
        self.pixels = [[ self.clear_color for y in range(self.height)]
                         for x in range(self.width)]

    def glClearBackground(self):
        if self.background:
            for x in range(self.vpX, self.vpX + self.vpWidth):
                for y in range(self.vpY, self.vpY + self.vpHeight):

                    tx = (x - self.vpX) / self.vpWidth
                    ty = (y - self.vpY) / self.vpHeight

                    self.glPoint(x,y, self.background.getColor(tx, ty))



    def glViewportClear(self, color = None):
        for x in range(self.vpX, self.vpX + self.vpWidth):
            for y in range(self.vpY, self.vpY + self.vpHeight):
                self.glPoint(x,y, color)


    def glColor(self, r, g, b):
        self.curr_color = color(r,g,b)

    def glPoint(self, x, y, color = None):
        if x < self.vpX or x >= self.vpX + self.vpWidth or y < self.vpY or y >= self.vpY + self.vpHeight:
            return

        if (0 <= x < self.width) and (0 <= y < self.height):
            self.pixels[int(x)][int(y)] = color or self.curr_color


    def glRender(self):

        for y in range(0, self.height, STEPS):
            for x in range(0, self.width , STEPS):
                # pasar de coordenadas de ventana a coordenadas NDC (-1 a 1)
                Px = 2 * ((x + 0.5) / self.width) - 1
                Py = 2 * ((y + 0.5) / self.height) - 1

                # Angulo de vision, asumiendo que el near plane esta a 1 unidad de la camara
                t = tan( (self.fov * np.pi / 180) / 2)
                r = t * self.width / self.height

                Px *= r
                Py *= t

                #La camara siempre esta viendo hacia -Z
                direction = V3(Px, Py, -1)
                direction = direction / np.linalg.norm(direction)

                self.glPoint(x,y, self.cast_ray(self.camPosition, direction))


    def cast_ray(self, orig, dir):
        intersect = self.scene_intersect(orig,dir)

        if intersect == None:
            return self.clear_color

        material = intersect.sceneObject.material


        objectColor = np.array([material.diffuse[2] / 255,
                                material.diffuse[1] / 255,
                                material.diffuse[0] / 255] )
        ambientColor = np.array([0,0,0])
        dirLightColor = np.array([0,0,0])
        pLightColor = np.array([0,0,0])
        finalColor = np.array([0,0,0])

        # Direccion de vista
        view_dir = np.subtract(self.camPosition, intersect.point)
        view_dir = view_dir / np.linalg.norm(view_dir)

        if self.ambLight:
            ambientColor = np.array([self.ambLight.strength * self.ambLight.color[2] / 255,
                                     self.ambLight.strength * self.ambLight.color[1] / 255,
                                     self.ambLight.strength * self.ambLight.color[0] / 255])

        if self.dirLight:
            diffuseColor = np.array([0,0,0])
            specColor = np.array([0,0,0])

            light_dir = np.array( self.dirLight.direction) * -1

            intensity = max(0, np.dot(intersect.normal, light_dir)) * self.dirLight.intensity

            diffuseColor = np.array([intensity * self.dirLight.color[2] / 255,
                                     intensity * self.dirLight.color[1] / 255,
                                     intensity * self.dirLight.color[0] / 255])

            # Iluminacion especular
            reflect = reflectVector(intersect.normal, light_dir)
            spec_intensity = self.dirLight.intensity * max(0,np.dot(view_dir, reflect)) ** material.spec
            specColor = np.array([spec_intensity * self.dirLight.color[2] / 255,
                                  spec_intensity * self.dirLight.color[1] / 255,
                                  spec_intensity * self.dirLight.color[0] / 255])

            dirLightColor = diffuseColor + specColor



        for pointLight in self.pointLights:
            diffuseColor = np.array([0,0,0])
            specColor = np.array([0,0,0])


            light_dir = np.subtract(pointLight.position, intersect.point)
            light_dir = light_dir / np.linalg.norm(light_dir)

            intensity = max(0, np.dot(intersect.normal, light_dir)) * pointLight.intensity

            diffuseColor = np.array([intensity * pointLight.color[2] / 255,
                                     intensity * pointLight.color[1] / 255,
                                     intensity * pointLight.color[0] / 255])

            # Iluminacion especular
            reflect = reflectVector(intersect.normal, light_dir)
            spec_intensity = pointLight.intensity * max(0,np.dot(view_dir, reflect)) ** material.spec
            specColor = np.array([spec_intensity * pointLight.color[2] / 255,
                                  spec_intensity * pointLight.color[1] / 255,
                                  spec_intensity * pointLight.color[0] / 255])

            pLightColor = np.add(pLightColor, diffuseColor + specColor)


        finalColor = pLightColor + ambientColor + dirLightColor

        finalColor = np.array([finalColor[0] * objectColor[0],
                               finalColor[1] * objectColor[1],
                               finalColor[2] * objectColor[2]])

        r = min(1, finalColor[0])
        g = min(1, finalColor[1])
        b = min(1, finalColor[2])
    
        return _color(r,g,b)


    def scene_intersect(self, orig, dir):
        depth = float('inf')
        intersect = None

        for obj in self.scene:
            hit = obj.ray_intersect(orig,dir)
            if hit != None:
                if hit.distance < depth:
                    depth = hit.distance
                    intersect = hit

        return intersect































