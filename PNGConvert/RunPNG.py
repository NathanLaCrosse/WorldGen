"""----------------------------------------------------------------

This code is the main function, that will take in a png and create sample images. 

This just has the function calls and enviornment setup for the ursina function

Dylan Dudley - 03/27/2026

----------------------------------------------------------------"""

from ursina import *
from PNGConvert.ImagePNG import imageLoad 
from PNGConvert.SampleDisplay import sampleTiles
from PNGConvert.WaveFunc import WaveFunc 
from PNGConvert.ChunkBasedMap import chunkBasedMap

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
def RunPNG(tile_size = 2, rotation = True, grid_size = 15, png_name = "RedDot", chunks = 10, wave = True):
    # Create test
    tile_size = tile_size # For sample tiles
    rotation = rotation # If we want rotations allowed
    grid_size = grid_size # output grid size
    png_name = png_name # Name of the PNG file in the images folder
    chunks = chunks # number of chunks to split the map into for better performance

    tiles, weights = imageLoad(f"PNGConvert/images/{png_name}.png",rotation, tile_size)

    # Single grid generation
    if (wave):
        WaveFunc(tiles, weights, grid_size, tile_size)
    else:
        # Chunk based grid generation, can create large maps, but can fail with more restrictive tile sets
        chunkBasedMap(tiles, weights, grid_size, tile_size,chunks) # Works well with versitile sample tiles, but can fail with more restrictive ones

    return