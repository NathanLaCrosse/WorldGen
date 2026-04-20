from PNGConvert.RunPNG import RunPNG
from Generation_3D.Main_3D import ThreeD_Main, new_3D_main
from ursina import *
import numpy as np

# General parms
grid_size = 15 # output grid size
tile_size = 2 # For sample tiles
rotation = False # If we want rotations allowed
png_name = "cityScape" # Name of the PNG file in the images folder

# 2-D only Parms
wave = True # If true, uses the single grid generation, if false uses the chunk based generation
stride = 1 
chunks = 1 # number of chunks to split the map into for better performance

# Make sure that tile_size = num_images when doing sample only and rotation = false
# 3-D only parms 
num_images = 35 # Number of images to use for the WFC, should be between 1 and 7
sample_only = True # If true, only creates the sample image, if false creates the WFC output (note: if true, it will not create the WFC output, even if wave is true, since it needs the WFC output to create the sample image)
png_folder = "Generation_3D/images_3D/cityScape"  # Mount is 30x30 image with 15 images. CityScape is 35x35x35
rows = 35
cols = 35
Surface_start = 0 #For caves only
gen_size = (15,30,30)

# Could work on adding in a function to fix the base layer to the base layer of the WFC
#fixed_base = False

# Main 3D WFC handler
image = new_3D_main(gen_size, tile_size, stride, num_images, png_folder, png_name, rotation, chunks, rows, cols, Surface_start)

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

#Old 3-D WFC handler, replaced with new one
# ThreeD_Main(
#             tile_size = tile_size, 
#             rotation = rotation,
#             png_folder = png_name, 
#             png_names = png_name,
#             grid_size = grid_size, 
#             num_images = num_images,
#             sample_only = sample_only
#             )

app = Ursina()

# Calculate the true center of the mesh in world space
center_x = grid_size / 2        # gx goes 0 to cols
center_y = grid_size / 2  # gy goes 0 to depth (num_images)
center_z = grid_size / 2        # gz goes 0 to rows

pivot = Entity(x=center_x, y=center_y, z=center_z)
image.parent = pivot
image.x = -center_x
image.y = -center_y
image.z = -center_z

# Lighting
DirectionalLight(x=grid_size/2, y=num_images+3, z=grid_size/2, shadows=True, rotation=(45, -45, 45)).look_at(Vec3(1, -1, -1))
AmbientLight(color=color.rgba(30, 30, 30, 0.5))

camera_spot = grid_size * chunks / 2
camera.position = (camera_spot, camera_spot, -(chunks * grid_size * 2))
camera.look_at(Vec3(grid_size / 2, -5, 0))

mouse.locked = True

# Global rotation state
rot_x = 0
rot_y = 0

def input(key):
    if key == 'q':
        application.quit()
    if key == 'backspace':
        camera.position = (camera_spot, camera_spot, -(chunks * grid_size * 2))
        camera.look_at(Vec3(grid_size / 2, -5, 0))

def update():
    global rot_x, rot_y

    base_speed = 5
    speed_multiplier = 10 if held_keys['shift'] else 1
    speed = base_speed * speed_multiplier * time.dt

    if held_keys['r']:
        # Rotate the pivot, not the image directly
        rot_y += mouse.velocity[0] * 100
        rot_x -= mouse.velocity[1] * 100
        pivot.rotation_x = rot_x
        pivot.rotation_y = rot_y
    else:
        # Only rotate camera when not rotating model
        camera.rotation_y += mouse.velocity[0] * 40
        camera.rotation_x -= mouse.velocity[1] * 40

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

app.run()