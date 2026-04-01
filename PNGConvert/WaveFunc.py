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

from FunctsFromCell2 import Cell, collapse_grid
from WorldGrid import build_world_grid
from SampleDisplay import waveDisplay
from TileCollection import collect_adjacencies
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
    hash_to_tile = {}
    hash_to_weight = {}

    for i in range(len(tiles)):
        h = hash_tile(tiles[i],numColors)
        hash_to_tile[h] = tiles[i]
        hash_to_weight[h] = weights[i]

    return hash_to_tile, hash_to_weight

# ------------------------------------------------------------------------
#
# main handler
#
# ------------------------------------------------------------------------
def WaveFunc(tiles, weights, grid_size):

    # Here we are going to start conversion to run WVC
    tile_hashes, hash_to_tile, hash_to_weight, adjacencies, color_to_index, index_to_color = waveStart(tiles, weights)

    # Create cell grid for generation
    
    cell_space = [
        [Cell(i, j, tile_hashes, hash_to_weight, adjacencies) for j in range(grid_size-1)]
        for i in range(grid_size-1)
    ]

    collapse_grid(cell_space, 0, 0,grid_size)
    
    #use ursina to display world
    world_grid = build_world_grid(cell_space, hash_to_tile)
    world_grid = world_grid.astype(int)
    

    # Now create a mesh to display everything
    startMesh(world_grid, grid_size, index_to_color)

    # Old display
    # waveDisplay(world_grid,grid_size,index_to_color)

    return 

# ------------------------------------------------------------------------
#
# This works with our cell function to get adjacency for our tileset
#
# ------------------------------------------------------------------------
def waveStart(tiles, weights):
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
    tile_hashes = [hash_tile(tile, numColors) for tile in colors]
    hash_to_tile, hash_to_weight = build_tile_lookup(colors, weights, numColors)

    # Directions for adjacency (must match Cell class)
    adjacencies = collect_adjacencies(hash_to_tile)

    return tile_hashes, hash_to_tile, hash_to_weight, adjacencies, color_to_index, index_to_color
    