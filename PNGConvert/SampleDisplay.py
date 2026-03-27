"""----------------------------------------------------------------

This file will be given the tile set from main, and extracts all 
the colors from the tiles. 

It then goes and creates entities for the sample set and makes sure to space them properly. 

Dylan Dudley - 03/27/2026

----------------------------------------------------------------"""

from ursina import *
from ImagePNG import *
from Blocks import create_block

# Tile Colors
def sampleTiles(tiles):
    x,y,z = 0, 0, 0 
    
    for i in range(0,len(tiles)):
        for j in range(0,4):
            # Gets the tile color
            r_norm = tiles[i][j][0] / 255
            g_norm = tiles[i][j][1] / 255
            b_norm = tiles[i][j][2] / 255

            tile_color = color.rgb(r_norm, g_norm, b_norm)  # Convert to color

            # Create a 2x2x1 cube
            create_block(
                position=(x,y,z),
                color=tile_color
            )

            # This does our rotation so we print each block next to one another
            if (j == 0 or j == 2):
                x += 1
            elif (j == 1):
                x -= 1
                y -= 1

        x += 2
        y += 1

        if (i == 4):
            y = -3
            x = 0
