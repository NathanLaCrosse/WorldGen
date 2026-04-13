"""----------------------------------------------------------------

This is our main wave function handler

Has hash table lookups, and builders for the use later on. 
re-indexes the colors and determines adjacency rules

Dylan Dudley - 03/28/2026

----------------------------------------------------------------"""
import sys
import os

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from WFC import generate_fully_recursive
from PNGConvert.MeshGrid import startMesh
from PNGConvert.SampleDisplay import sample_mesh
from TileCollection import hash_tile, build_tile_lookup

# ------------------------------------------------------------------------
#
# main handler
#
# ------------------------------------------------------------------------
def WaveFunc(tiles, weights, grid_size, tile_size, stride):

    hash_to_num, num_to_hash, tile_set, index_to_color, color_to_index, numColors = tileToColor(tiles, weights)

    PNG=True
    
    grid = generate_fully_recursive(None, grid_size, tile_size,stride,  PNG, hash_to_num, num_to_hash, tile_set, numColors)

    startMesh(grid[0], index_to_color)

    # TODO: Fix this
    sample_mesh(tiles, color_to_index, index_to_color, tile_size)
    

    return 

def WaveFunc3D(tiles, weights, grid_size, tile_size, stride):

    hash_to_num, num_to_hash, tile_set, index_to_color, color_to_index, numColors = tileToColor(tiles, weights)

    PNG=True
    
    grid, res = generate_fully_recursive(None, grid_size, tile_size,stride,  PNG, hash_to_num, num_to_hash, tile_set, numColors)

    return grid, index_to_color

# ------------------------------------------------------------------------
#
# This will convert the tiles list into color indexes
#
# ------------------------------------------------------------------------
def tileToColor(tiles, weights):
    colors = []
    color_to_index = {}
    index_to_color = {}
    next_index = 0

    #convert to numeric indices
    def get_color_index(rgb):
        nonlocal next_index
        if rgb not in color_to_index:
            color_to_index[rgb] = next_index
            index_to_color[next_index] = rgb
            next_index += 1

        return color_to_index[rgb]

    # This will convert all tiles into color indexes (0,1,2,3....)
    # Iterate over all tiles
    for tile in tiles:
        tile_indices = []
        # Each tile can have any number of rows
        for row in tile:
            # Each row can have any number of columns
            row_indices = [get_color_index(pixel) for pixel in row]
            tile_indices.append(row_indices)
        colors.append(tile_indices)
    
    # Gather unique colors
    numColors = len(color_to_index)

    # Hash the tiles 
    hash_to_num, num_to_hash, tile_set = build_tile_lookup(colors, weights, numColors)


    return hash_to_num, num_to_hash, tile_set, index_to_color,color_to_index, numColors
    