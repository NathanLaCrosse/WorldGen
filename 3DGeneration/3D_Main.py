"""----------------------------------------------------------------

This code is the main function, that will take in a png and create sample images. 

This just has the function calls and enviornment setup for the ursina function

Dylan Dudley - 03/27/2026

----------------------------------------------------------------"""

import sys
import os

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ursina import *
from PNGConvert.ImagePNG import imageLoad 
from PNGConvert.SampleDisplay import sampleTiles
from PNGConvert.WaveFunc import WaveFunc 
from PNGConvert.ChunkBasedMap import chunkBasedMap

import numpy as np


# Create test
tile_size = 2 # For sample tiles
rotation = True # If we want rotations allowed
grid_size = 15 # output grid size
png_name = "RedDot" # Name of the PNG file in the images folder

D3D_tiles = []

for i in range(4):
    png_name = f"png_name{i}"
    tiles, weights = imageLoad(f"PNGConvert/images/{png_name}.png",rotation, tile_size)
    D3D_tiles.append(tiles)

print(D3D_tiles)

app = Ursina()

# Sets up the Ursina enviornment

# Lighting
DirectionalLight().look_at(Vec3(1, -1, -1))
AmbientLight(color=color.rgba(100, 100, 100, 0.5))

camera_spot = grid_size * chunks / 2

# Camera
camera.position = (camera_spot, camera_spot, -(chunks*grid_size*2))
camera.look_at(Vec3(grid_size/2, -5, 0))
mouse.locked = True

def input(key):
    if key == 'q':
        application.quit()
    if key == 'backspace':
        camera.position = (camera_spot, camera_spot, -(chunks * grid_size * 2))
        camera.look_at(Vec3(grid_size/2, -5, 0))

def update():
    base_speed = 5
    speed_multiplier = 10 if held_keys['shift'] else 1
    speed = base_speed * speed_multiplier * time.dt

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