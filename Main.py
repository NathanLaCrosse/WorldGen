from PNGConvert.RunPNG import RunPNG
from Generation_3D.Main_3D import ThreeD_Main
from ursina import *
import numpy as np

grid_size = 15 # output grid size
chunks = 1 # number of chunks to split the map into for better performance
tile_size = 5 # For sample tiles
rotation = False # If we want rotations allowed
png_name = "4Color" # Name of the PNG file in the images folder
png_names = "grass" # Name of the PNG file in the images folder for 3D generation
png_folder = "grass" # Name of the PNG file in the images folder for 3D generation
wave = False # If true, uses the single grid generation, if false uses the chunk based generation

#RunPNG(tile_size = tile_size, rotation = rotation, grid_size = grid_size, png_name = png_name, chunks = chunks, wave = wave)

ThreeD_Main(tile_size, rotation, png_folder=png_folder, png_names=png_names)

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

    # Move up
    if held_keys['space']:
        camera.position += Vec3(0, speed * 20 * time.dt, 0)
    # Move down
    if held_keys['control']:
        camera.position -= Vec3(0, speed * 20 * time.dt, 0)

    camera.rotation_y += mouse.velocity[0] * 40
    camera.rotation_x -= mouse.velocity[1] * 40
    camera.rotation_x = clamp(camera.rotation_x, -90, 90)

app.run()


