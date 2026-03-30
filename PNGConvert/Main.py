"""----------------------------------------------------------------

This code is the main function, that will take in a png and create sample images. 

This just has the function calls and enviornment setup for the ursina function

Dylan Dudley - 03/27/2026

----------------------------------------------------------------"""

from ursina import *
from ImagePNG import imageLoad 
from SampleDisplay import sampleTiles

app = Ursina()

#This is where I would put the main wave function call

# Create test
tiles, weights = imageLoad("PNGConvert/Sample.png")

sampleTiles(tiles)


# Lighting
DirectionalLight().look_at(Vec3(1, -1, -1))
AmbientLight(color=color.rgba(100, 100, 100, 0.5))

# Camera
camera.position = (0, 2, -8)
mouse.locked = True

def input(key):
    if key == 'q':
        application.quit()

def update():
    speed = 5 * time.dt

    if held_keys['w']:
        camera.position += camera.forward * speed
    if held_keys['s']:
        camera.position -= camera.forward * speed
    if held_keys['a']:
        camera.position -= camera.right * speed
    if held_keys['d']:
        camera.position += camera.right * speed

    camera.rotation_y += mouse.velocity[0] * 40
    camera.rotation_x -= mouse.velocity[1] * 40
    camera.rotation_x = clamp(camera.rotation_x, -90, 90)

app.run()