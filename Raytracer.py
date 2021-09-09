from gl import Raytracer, V3, _color
from obj import Obj, Texture

from figures import Sphere, Material, PointLight, AmbientLight, DirectionalLight

width = 512
height = 512

# Materiales
brick = Material(diffuse = _color(0.8,0.25,0.25), spec = 32)
stone = Material(diffuse = _color(0.4,0.4,0.4), spec = 64)
grass = Material(diffuse = _color(0.4,1,0), spec = 128)

rtx = Raytracer(width,height)

rtx.ambLight = AmbientLight(strength = 0.1)
rtx.dirLight = DirectionalLight(direction = V3(1, -1, -2), intensity = 0.5)
rtx.pointLights.append( PointLight(position = V3(-10, 2, 0)))


rtx.scene.append( Sphere(V3(0,0,-8), 2, grass ))
rtx.scene.append( Sphere(V3(-1,1,-5), 0.5, stone ))
rtx.scene.append( Sphere(V3(0.5,0.5,-5), 0.5, brick ))

rtx.glRender()

rtx.glFinish('output.bmp')



