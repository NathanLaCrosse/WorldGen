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
from Generation_3D.Sample_3D import create_voxel_mesh

import numpy as np

def ThreeD_Main():
    png_folder = "grass" # Name of the PNG file in the images folder
    tile_size = 5 # For sample tiles
    rotation = False # If we want rotations allowed
    three_dimensional = []
    three_dimensional_weights = []

    for i in range(5):
        png_name = f"grass{i}"
        tiles, weights = imageLoad(f"Generation_3D/images_3D/{png_folder}/{png_name}.png",rotation, tile_size)
        three_dimensional.append((tiles))
        three_dimensional_weights.append(weights)
    print(three_dimensional[0][0][0],"\n\n")
    print(three_dimensional[0][0],"\n\n")
    
    create_voxel_mesh(three_dimensional)
    # SampleTiles - displays the sample dataset