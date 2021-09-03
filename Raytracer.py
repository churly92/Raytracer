from gl import Raytracer, V3, _color
from obj import Obj, Texture

from figures import Sphere, Material

width = 512
height = 512

brick = Material(diffuse = _color(0.8,0.25,0.25))
stone = Material(diffuse = _color(0.4,0.4,0.4))
grass = Material(diffuse = _color(0.4,1,0))
wood = Material(diffuse = _color(0.5,0.5,0.1))



rtx = Raytracer(width,height)

rtx.scene.append( Sphere(V3(3,0,-10), 2, brick) )
rtx.scene.append( Sphere(V3(0,0,-14), 4, stone) )
rtx.scene.append( Sphere(V3(3,-2,-8), 0.5, grass) )
rtx.scene.append( Sphere(V3(-4,-2,-6), 1, wood) )


rtx.glRender()

rtx.glFinish('output.bmp')



