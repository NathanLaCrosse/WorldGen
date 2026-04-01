"""----------------------------------------------------------------

This file will be given the tile set from main, and extracts all 
the colors from the tiles. 

It then goes and creates entities for the sample set and makes sure to space them properly. 

Dylan Dudley - 03/27/2026

----------------------------------------------------------------"""

from ursina import *
from ImagePNG import *
from Blocks import create_block

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
def waveDisplay(world_grid,grid_size,index_to_color):
    x,y,z = 0, 0, 0 
    
    for i in range(grid_size-1):
        for j in range(grid_size-1):
            # Gets the tile color
            colors = index_to_color[world_grid[i][j]]

            r_norm = colors[0] / 255
            g_norm = colors[1] / 255
            b_norm = colors[2] / 255

            tile_color = color.rgb(r_norm, g_norm, b_norm)  # Convert to color

            # Create a 2x2x1 cube
            create_block(
                position=(x,y,z),
                color=tile_color
            )
            x += 1
        y -= 1
        x = 0