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

from WFCCollapseBitwise import generate_fully_recursive
from MeshGrid import startMesh

# ------------------------------------------------------------------------
#
# Hash based on number of colors
#
# ------------------------------------------------------------------------
def hash_tile(tile,numColors):
    flat = [pixel for row in tile for pixel in row]
    hash = 0
    for i in range(len(flat)):
        hash += flat[i] * (numColors ** i)
    return hash

# To create a table that has the tiles and weights
def build_tile_lookup(tiles, weights, numColors):
    tile_set  = {}

    for i in range(len(tiles)):
        h = hash_tile(tiles[i],numColors)
        tile_set [h] = weights[i]

    hash_to_num = {}
    num_to_hash = {}

    for i, h in enumerate(tile_set.keys()):
        hash_to_num[h] = i
        num_to_hash[i] = h

    return hash_to_num, num_to_hash, tile_set

# ------------------------------------------------------------------------
#
# main handler
#
# ------------------------------------------------------------------------
def WaveFunc(tiles, weights, grid_size, tile_size):

    hash_to_num, num_to_hash, tile_set, index_to_color, colors = tileToColor(tiles, weights)

    PNG=True
    
    grid = generate_fully_recursive(grid_size, grid_size, tile_size, PNG, hash_to_num, num_to_hash, tile_set)
    
    startMesh(grid, index_to_color)

    return 

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


    return hash_to_num, num_to_hash, tile_set, index_to_color, colors
    