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
from PNGConvert.WaveFunc import WaveFunc3D 
from PNGConvert.ChunkBasedMap import chunkBasedMap
from Generation_3D.Sample_3D import create_voxel_mesh

import numpy as np

def ThreeD_Main(tile_size, rotation = False, png_folder="building",png_names="building", grid_size = 5, num_images = 5, sample_only = False):
    png_folder = png_folder # Name of the PNG file in the images folder
    tile_size = tile_size # For sample tiles
    rotation = rotation # If we want rotations allowed
    three_dimensional = []
    three_dimensional_weights = []
    grid_3d = []
    index_to_color_3d = []

    for i in range(num_images):
        png_name = f"{png_names}{i}"
        tiles, weights = imageLoad(f"Generation_3D/images_3D/{png_folder}/{png_name}.png",rotation, tile_size)
        three_dimensional.append((tiles))
        three_dimensional_weights.append(weights)
        if (not sample_only):
            grid_, index_to_color = WaveFunc3D(three_dimensional[i], three_dimensional_weights[i], grid_size, tile_size, stride=1)
            grid_3d.append(grid_)
            index_to_color_3d.append(index_to_color)

    if (not sample_only):
        # Using the png to create grid size image
        create_voxel_mesh(grid_3d, index_to_color_3d)
    else:
        # To print the sample image
        create_voxel_mesh(three_dimensional, None)
    

