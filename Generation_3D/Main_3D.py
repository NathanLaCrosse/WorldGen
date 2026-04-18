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
from PNGConvert.WaveFunc import WaveFunc3D 
from Generation_3D.Mesh_3D import create_voxel_mesh
from TileCollection3D import *
from WFC3D import generate_3D_fully_recursive
import numpy as np

def ThreeD_Main(tile_size, rotation = False, png_folder="building",png_names="building", grid_size = 5, num_images = 5, sample_only = False):
    png_folder = png_folder # Name of the PNG file in the images folder
    tile_size = tile_size # For sample tiles
    rotation = rotation # If we want rotations allowed
    # Sets up our 3D world placeholders
    three_dimensional = []
    three_dimensional_weights = []
    grid_3d = []
    index_to_color_3d = []

    # based on name convention, will loop over each layer of the pngs
    for i in range(num_images):
        png_name = f"{png_names}{i}"
        tiles, weights = imageLoad(f"Generation_3D/images_3D/{png_folder}/{png_name}.png",rotation, tile_size)
        three_dimensional.append((tiles))
        three_dimensional_weights.append(weights)
        # This will do the WFC on a layer by layer scale, no connection between layers

        """
        
        I would recommend commenting this code below out, since won't be needed once you finish the WFC with 2x2x2 samples
        
        """
        if (not sample_only):
            grid_, index_to_color = WaveFunc3D(three_dimensional[i], three_dimensional_weights[i], grid_size, tile_size, stride=1)
            grid_3d.append(grid_)
            index_to_color_3d.append(index_to_color)

    # Determins if we did WFC or just want to print the sample image
    if (not sample_only):
        # Using the png to create grid size image
        image = create_voxel_mesh(grid_3d, index_to_color_3d)
    else:
        # To print the sample image
        image = create_voxel_mesh(three_dimensional, None)

def new_3D_main(grid_size, tile_size, stride, num_layers, png_folder, png_names, rotations, chunks, length, width):
    grid_size = grid_size
    tile_size = tile_size
    stride = stride

    tilemap, idx_to_color, color_to_idx = construct_3D_tilemap(num_layers,length,width,png_folder, png_names)

    tiles, weights = collect_3D_tiles(tilemap, tile_size, rotations)

    num_colors = len(idx_to_color.keys())
    num_states = len(tiles)

    hash_to_num, num_to_hash, tile_set = build_3D_tilemap_hashes(tiles, weights, num_colors)

    space, res = generate_3D_fully_recursive(grid_size, hash_to_num, num_to_hash, tile_set, num_colors, tile_size, stride)

    #space = space[::-1]

    # create_voxel_mesh(tilemap.tolist(), idx_to_color)
    image = create_voxel_mesh(space.tolist(), idx_to_color)
    # print(res)

    chunks = chunks

    return image
    

