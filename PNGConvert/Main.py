"""----------------------------------------------------------------

This code is the main function, that will take in a png and create sample images. 

This just has the function calls and enviornment setup for the ursina function

Dylan Dudley - 03/27/2026

----------------------------------------------------------------"""

from ursina import *
from ImagePNG import imageLoad 
from SampleDisplay import sampleTiles
from WaveFunc import WaveFunc 
from MeshGrid import startMesh

import numpy as np

#This is where I would put the main wave function call

# Create test
tiles, weights = imageLoad("PNGConvert/images/4Color.png",True)

app = Ursina()

#sampleTiles(tiles)

# 32 is current max
grid_size = 20
WaveFunc(tiles, weights, grid_size)



# Lighting
DirectionalLight().look_at(Vec3(1, -1, -1))
AmbientLight(color=color.rgba(100, 100, 100, 0.5))

# Camera
camera.position = (grid_size/2, grid_size/2, -(2*grid_size))
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