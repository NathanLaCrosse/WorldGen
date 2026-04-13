from PNGConvert.RunPNG import RunPNG
from Generation_3D.Main_3D import ThreeD_Main
from ursina import *
import numpy as np

# General parms
grid_size = 25 # output grid size
tile_size = 2 # For sample tiles
rotation = False # If we want rotations allowed
png_name = "grass" # Name of the PNG file in the images folder

# 2-D only Parms
wave = True # If true, uses the single grid generation, if false uses the chunk based generation
stride = 1 
chunks = 1 # number of chunks to split the map into for better performance

# Make sure that tile_size = num_images when doing sample only and rotation = false
# 3-D only parms 
num_images = 5 # Number of images to use for the WFC, should be between 1 and 7
sample_only = True # If true, only creates the sample image, if false creates the WFC output (note: if true, it will not create the WFC output, even if wave is true, since it needs the WFC output to create the sample image)


# 2-D WFC
# RunPNG(
#       tile_size = tile_size, 
#       rotation = rotation, 
#       grid_size = grid_size, 
#       png_name = png_name, 
#       chunks = chunks, 
#       wave = wave, 
#       stride = stride
#       )

# Currently works with 5x5 tile size, and either grass or building for png_name
ThreeD_Main(
            tile_size = tile_size, 
            rotation = rotation,
            png_folder = png_name, 
            png_names = png_name,
            grid_size = grid_size, 
            num_images = num_images,
            sample_only = sample_only
            )

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


