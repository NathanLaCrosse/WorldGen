from PNGConvert.RunPNG import RunPNG
from Generation_3D.Main_3D import ThreeD_Main, new_3D_main
from ursina import *
import numpy as np


# 3-D only parms 
gen_size = (25,25,25)
stride = 1 
chunks = 1 # number of chunks to split the map into for better performance

# -------------------------------------------------------------------------------------------------------------------------------------
#
#3-D parms  Num images,     png foler,                    png name, rotations, tile_size, row, cols, surface_start, gen_size, preset
#
# -------------------------------------------------------------------------------------------------------------------------------------
cityScape_parms = (33, "Generation_3D/images_3D/cityScape","cityScape",False,      2,      35, 35,         1,       gen_size, True)
mount_parms = (    15,     "Generation_3D/images_3D/mount","mount"    ,False,      2,      30, 30,         9,       gen_size, True)
grass = (          5,      "Generation_3D/images_3D/mount","mount"    ,True ,      2,      5,  5,          0,       gen_size, False)
cave = (           7,      "Generation_3D/images_3D/mount","mount"    ,False,      2,      7,  7,          0,       gen_size, False)
richgrass = (      8,      "Generation_3D/images_3D/mount","mount"    ,True ,      2,      8,  8,          0,       gen_size, False)


# Set to what image you want to load
parms = mount_parms

# Main 3D WFC handler
image = new_3D_main(parms[8], parms[4], stride, parms[0], parms[1], parms[2], parms[3], chunks, parms[5], parms[6], parms[7], parms[9])

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
center_x = gen_size[1] / 2        # gx goes 0 to cols
center_y = gen_size[0] / 2  # gy goes 0 to depth (num_images)
center_z = gen_size[2] / 2        # gz goes 0 to rows

pivot = Entity(x=center_x, y=center_y, z=center_z)
image.parent = pivot
image.x = -center_x
image.y = -center_y
image.z = -center_z

# Lighting
DirectionalLight(x=gen_size[1]/2, y=gen_size[0]+3, z=gen_size[2]/2, shadows=True, rotation=(45, -45, 45)).look_at(Vec3(1, -1, -1))
AmbientLight(color=color.rgba(30, 30, 30, 0.5))

camera_spot = gen_size[0] * chunks / 2
camera.position = (camera_spot, camera_spot, -(chunks * gen_size[1] * 2))
camera.look_at(Vec3(gen_size[1] / 2, -5, 0))

mouse.locked = True

# Global rotation state
rot_x = 0
rot_y = 0

def input(key):
    if key == 'q':
        application.quit()
    if key == 'backspace':
        camera.position = (camera_spot, camera_spot, -(chunks * gen_size[1] * 2))
        camera.look_at(Vec3(gen_size[1] / 2, -5, 0))

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