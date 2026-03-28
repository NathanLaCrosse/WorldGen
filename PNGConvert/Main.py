"""----------------------------------------------------------------

This code is the main function, that will take in a png and create sample images. 

This just has the function calls and enviornment setup for the ursina function

Dylan Dudley - 03/27/2026

----------------------------------------------------------------"""

from ursina import *
from ImagePNG import imageLoad 
from SampleDisplay import sampleTiles, waveDisplay
from WaveFunc import waveStart
from FunctsFromCell2 import Cell, collapse_grid
from WorldGrid import build_world_grid
import numpy as np

app = Ursina()

#This is where I would put the main wave function call

# Create test
tiles, weights = imageLoad("PNGConvert/Mount.png",False)

#sampleTiles(tiles)


# Here we are going to start conversion to run WVC
tile_hashes, hash_to_tile, hash_to_weight, adjacencies, color_to_index, index_to_color = waveStart(tiles, weights)

# Create cell grid for generation
grid_size = 12
cell_space = [
    [Cell(i, j, tile_hashes, hash_to_weight, adjacencies) for j in range(grid_size-1)]
    for i in range(grid_size-1)
]

collapse_grid(cell_space, 0, 0)


#use ursina to display world
world_grid = build_world_grid(cell_space, hash_to_tile)
world_grid = world_grid.astype(int)

waveDisplay(world_grid,grid_size,index_to_color)

# Lighting
DirectionalLight().look_at(Vec3(1, -1, -1))
AmbientLight(color=color.rgba(100, 100, 100, 0.5))

# Camera
camera.position = (5, -5, -40)
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