"""----------------------------------------------------------------

This code is the main function, that will take in a png and create sample images. 

This just has the function calls and enviornment setup for the ursina function

Dylan Dudley - 03/27/2026

----------------------------------------------------------------"""

from ursina import *
from ImagePNG import imageLoad 
from SampleDisplay import sampleTiles
from WaveFunc import WaveFunc 
from ChunkBasedMap import chunkBasedMap

import numpy as np

# ------------------------------------------------------------------------
#
# This is the main handler
# imageLoad - modify the /XXXX.png for given sample image
#           - This is for when you want to rotate True for rotate
#
# SampleTiles - displays the sample dataset
#
# grid_size - adjust to grid_size 30 x 30
# WaveFunc - takes in the tiles and weight list as well as grid_size
#
# The rest is setting up our ursina enviornment
#
# ------------------------------------------------------------------------

# Create test
tile_size = 2 # For sample tiles
rotation = True # If we want rotations allowed
grid_size = 10 # output grid size
png_name = "4Color" # Name of the PNG file in the images folder
chunks = 15 # number of chunks to split the map into for better performance

tiles, weights = imageLoad(f"PNGConvert/images/{png_name}.png",rotation, tile_size)

# Single grid generation
#WaveFunc(tiles, weights, grid_size, tile_size)

# Chunk based grid generation, can create large maps, but can fail with more restrictive tile sets
chunkBasedMap(tiles, weights, grid_size, tile_size,chunks) # Works well with versitile sample tiles, but can fail with more restrictive ones

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