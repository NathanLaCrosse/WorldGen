import sys
import os
import numpy as np
from PIL import Image
from ursina import *
from Generation_3D.Mesh_3D import create_voxel_mesh

# Convert a series of images into a 3D tilemap
def construct_3D_tilemap(layers=5, rows=5, cols=5, png_folder="Generation_3D/images_3D/grass", png_names="grass"):
    tilemap = np.zeros((layers, rows, cols))
    
    # Two hashtables for translating between color & index space
    idx_to_color = {}
    color_to_idx = {}

    dex = 0
    for i in range(layers):
        png_name = f"{png_names}{i}"

        # Load the image into a numpy array
        img = Image.open(f"{png_folder}/{png_name}.png").convert("RGB")
        pixel_ar = np.array(img)

        for j, k in np.ndindex((pixel_ar.shape[0], pixel_ar.shape[1])):
            # Convert the slice of the image's color channels to a tuple index
            color_tuple = tuple(pixel_ar[j, k, :].tolist())

            if color_tuple not in color_to_idx.keys():
                color_to_idx[color_tuple] = dex
                idx_to_color[dex] = color_tuple

                dex += 1
            
            tilemap[i, j, k] = color_to_idx[color_tuple]
    
    # Returns:
    # tilemap - 3d numpy array of color indices
    # idx_to_color - hash table for mapping an int into a tuple of colors
    # color_to_idx - hash table for mapping a tuple of colors into an int
    return tilemap, idx_to_color, color_to_idx

# Collect cubes from the sample tilemap
def collect_3D_tiles(tilemap, tile_size, rotation=False):
    # Get dimensions of the tilemap
    depth, height, width = tilemap.shape

    tile_table = {} # For keeping track of 
    tiles = []
    weights = []

    dex = 0

    # Traverse through the tilemap (based on tile_size) & collect tiles
    for i in range(depth - tile_size + 1):
        for j in range(depth - tile_size + 1):
            for k in range(depth - tile_size + 1):
                tile = tilemap[i:i+tile_size, j:j+tile_size, k:k+tile_size]

                tile_tuple = tuple(tile.flatten().tolist()) # For comparisons - collapse to tuple

                if tile_tuple not in tile_table.keys():
                    tiles.append(tile.copy()) # Add slice to tiles
                    weights.append(1)
                    tile_table[tile_tuple] = dex
                    dex += 1
                else:
                    weights[tile_table[tile_tuple]] += 1
    
    # Returns:
    # tiles - list of all tiles found in the tilemap, stored as 3d numpy arrays
    # weights - list of the weights (frequency) of each of the tiles
    return tiles, weights


def hash_3D_tile(tile, num_colors):
    flat = tile.flatten()

    hash = 0
    for i in range(len(flat)):
        hash += flat[i] * num_colors**i

    return hash

def reverse_3D_hash(num, num_colors, tile_size):
    tile = np.zeros(tile_size * tile_size * tile_size, dtype=np.int64)
    n = num

    for i in range(len(tile)):
        tile[i] = n % num_colors
        n = n // num_colors

    return tile.reshape((tile_size, tile_size, tile_size))


def build_3D_tilemap_hashes(tiles, num_colors):
    tile_set = {}
    hash_to_num = {}
    num_to_hash = {}

    for i in range(len(tiles)):
        h = hash_3D_tile(tiles[i], num_colors)

        tile_set[h] = weights[i]

        hash_to_num[h] = i
        num_to_hash[i] = h
    
    return hash_to_num, num_to_hash, tile_set

# Currently the exact same as tile_collection... 
# Could be speed up by mapping back to numpy arrays and slicing...
def compare_3D_hashes(h1, h2, t1_border, t2_border,num_colors):
    assert len(t1_border) == len(t2_border), "Border Sizes Must Match"

    for i in range(len(t1_border)):
        if (h1 // num_colors**t1_border[i]) % num_colors != (h2 // num_colors**t2_border[i]) % num_colors:
            return False
    return True

def collect_reverse_adjacencies(hash_to_num, tile_set, num_colors, num_states, 
        directions=['t','b','n','s','e','w'], tile_size=2, stride=1):

    args = np.arange(tile_size**3).reshape((tile_size, tile_size, tile_size)) # What areas need to be compared in our comparison function

    top = args[:-stride].flatten()
    bottom = args[stride:].flatten()

    north = args[:,:-stride].flatten()
    south = args[:,stride:].flatten()

    east = args[:,:,:-stride].flatten()
    west = args[:,:,stride:].flatten()

    t1_comparisons = [top, bottom, north, south, east, west]
    t2_comparisons = [bottom, top, south, north, west, east]

    # Encode an adjacency matrix 
    rev_adjacencies = {}

    # Intialize matrices
    for d in directions:
        rev_adjacencies[d] = np.zeros((num_states, num_states), dtype=bool)
    
    # Detect adjacencies
    for source in tile_set.keys():
        for sink in tile_set.keys():

            for d in range(len(directions)):
                if compare_3D_hashes(source, sink, t1_comparisons[d], t2_comparisons[d], num_colors):
                    # State i allows neighboring state j
                    i = hash_to_num[source]
                    j = hash_to_num[sink]
                    rev_adjacencies[directions[d]][i, j] = 1

    return rev_adjacencies

# if __name__ == "__main__":
tilemap, idx_to_color, color_to_idx = construct_3D_tilemap()

tiles, weights = collect_3D_tiles(tilemap, 2)

num_colors = len(idx_to_color.keys())
num_states = len(tiles)

hash_to_num, num_to_hash, tile_set = build_3D_tilemap_hashes(tiles, num_colors)
rev_adj = collect_reverse_adjacencies(hash_to_num, tile_set, num_colors, num_states)

create_voxel_mesh(tilemap.tolist(), idx_to_color)






grid_size = 25
tile_size = 2
stride = 1 
chunks = 1
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


