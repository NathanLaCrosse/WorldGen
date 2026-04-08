"""----------------------------------------------------------------

This file will be given the tile set from main, and extracts all 
the colors from the tiles. 

It then goes and creates entities for the sample set and makes sure to space them properly. 

Dylan Dudley - 03/27/2026

----------------------------------------------------------------"""

from ursina import *
from ImagePNG import *
from Blocks import create_block
from MeshGrid import startMesh
import numpy as np

# ------------------------------------------------------------------------
#
# This displays our sample tile set
# Replaced by mesh. Keeping for reference if needed
#
# ------------------------------------------------------------------------
def sampleTiles(tiles, tile_size=2):
    # displays them below our WFC set
    x,y,z = 0, -5, 0 
    x_offset = 0

    for i, tile in enumerate(tiles):
        # This converts each tile into the respective color
        for row in range(tile_size):
            for col in range(tile_size):
                # Gets the tile color
                r_norm = tile[row][col][0] / 255
                g_norm = tile[row][col][1] / 255
                b_norm = tile[row][col][2] / 255

                tile_color = color.rgb(r_norm, g_norm, b_norm)  # Convert to color

                # Create a 2x2x1 cube
                create_block(
                    position=((x_offset + col),(y-row),z),
                    color=tile_color
                )

        x_offset += tile_size + 1  # Move to the next position for the next tile

        # this just means after 8 moves, we move down and back to the start for cleaner display
        if (i % 8 == 7):
            x_offset = x
            y -= tile_size + 2

# Creates a mesh for the sample tiles, this is for better performance when we have a large number of tiles
def sample_mesh(tiles, color_to_index, index_to_color, tile_size=2, tiles_per_row=8):
    num_tiles = len(tiles)
    rows = (num_tiles + tiles_per_row - 1) // tiles_per_row

    grid_height = rows * (tile_size + 1)
    grid_width = tiles_per_row * (tile_size + 1)

    sample_grid = np.full((grid_height, grid_width), -1)

    for idx, tile in enumerate(tiles):
        tile_row = idx // tiles_per_row
        tile_col = idx % tiles_per_row

        # Add spacing of 1 between tiles
        y_offset = tile_row * (tile_size + 1)
        x_offset = tile_col * (tile_size + 1)

        for dy in range(tile_size):
            for dx in range(tile_size):
                y = y_offset + dy
                x = x_offset + dx

                sample_grid[y, x] = color_to_index[tile[dy][dx]]

    startMesh(sample_grid, index_to_color, x_offset=0, y_offset=-grid_height-5)
    return sample_grid
            