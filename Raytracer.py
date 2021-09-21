from gl import Raytracer, V3
from obj import *
from figures import *

# Dimensiones
width = 1024
height = 1024

# Materiales
stone = Material(diffuse = (0.4,0.4,0.4), spec = 64)
mirror = Material(spec = 128, matType = REFLECTIVE)
gold = Material(diffuse = (1, 0.8, 0 ),spec = 32, matType = REFLECTIVE)

# Inicializacion
rtx = Raytracer(width,height)
rtx.envmap = EnvMap('envmap_parqueo.bmp')

# Luces
rtx.ambLight = AmbientLight(strength = 0.1)
rtx.dirLight = DirectionalLight(direction = V3(1, -1, -2), intensity = 0.5)
rtx.pointLights.append( PointLight(position = V3(0, 2, 0), intensity = 0.5))

# Objetos
rtx.scene.append( Sphere(V3(0,0,-8), 2, stone ))
rtx.scene.append( Sphere(V3(-1,1,-5), 0.5, mirror ))
rtx.scene.append( Sphere(V3(0.5,0.5,-5), 0.5, gold ))

# Terminar
rtx.glRender()
rtx.glFinish('output.bmp')



