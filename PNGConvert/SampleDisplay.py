"""----------------------------------------------------------------

This file will be given the tile set from main, and extracts all 
the colors from the tiles. 

It then goes and creates entities for the sample set and makes sure to space them properly. 

Dylan Dudley - 03/27/2026

----------------------------------------------------------------"""

from ursina import *
from PNGConvert.ImagePNG import *
from PNGConvert.Blocks import create_block
import numpy as np

# ------------------------------------------------------------------------
#
# This displays our sample tile set
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

# Replaced by mesh. Keeping for reference if needed
def sample_mesh(tiles, color_to_index, tile_size=2):
    tile_length = len(tiles)
    sample_grid = np.full((grid_size, grid_size), -1)

    current_x = 0
    for tile in tiles:
        # tile is tile_size x tile_size
        for dy in range(tile_size):
            for dx in range(tile_size):
                # make sure we don't go out of bounds
                if dy < grid_size and current_x + dx < grid_size:
                    sample_grid[dy][current_x + dx] = color_to_index[tile[dy][dx]]
        # move to next tile horizontally
        current_x += tile_size

    print(sample_grid)
    return sample_grid
            