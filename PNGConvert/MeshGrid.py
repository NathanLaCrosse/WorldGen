"""----------------------------------------------------------------

This creates a mesh to display the images

Dylan Dudley - 03/30/2026

----------------------------------------------------------------"""
from ursina import *

# ------------------------------------------------------------------------
#
# This is the main handler, can be modified later on for 3D applications
#
# ------------------------------------------------------------------------

def startMesh(world_grid, index_to_color, x_offset=0, y_offset=0):
    create_mesh(world_grid, index_to_color, x_offset, y_offset)
    return

# ------------------------------------------------------------------------
#
# Here is were we create the mesh - takes in world_grid, size, and index_to_color
# 
# This improves our ability to display the WFC in ursina
#
# ------------------------------------------------------------------------

def create_mesh(world_grid, index_to_color, x_offset=0, y_offset=0, tile_size=1):
    tiles_holder = []
    triangles = []
    colors = []

    # Use actual world_grid size (overlapping)
    rows, cols = world_grid.shape  

    # This creates a grid, based on our world_grid shape
    # This converts to Vec3 which are vector pointers
    for y in range(rows):
        for x in range(cols):
            quad_tile = [
                Vec3(x * tile_size, y * tile_size, 0),
                Vec3((x+1) * tile_size, y * tile_size, 0),
                Vec3((x+1) * tile_size, (y+1) * tile_size, 0),
                Vec3(x * tile_size, (y+1) * tile_size, 0)
            ]
            # This is where we store the quad_tile 
            tiles_holder.extend(quad_tile)
            idx = len(tiles_holder) - 4
            # the Mesh uses triangles, since GPU's can only create triangles
            # Below takes two triangles and puts them together to form a square
            triangles.extend([idx, idx+1, idx+2, idx, idx+2, idx+3])

            # This handler will take in the given location, and return the color from our color index
            colors.extend([get_color(world_grid,x,y,index_to_color)]*4)
    

    # Creates the mesh, then forms as an entity
    mesh = Mesh(vertices=tiles_holder, triangles=triangles, colors=colors, mode='triangle')
    entity = Entity(model=mesh, position=(x_offset, y_offset, 0))
    return


# ------------------------------------------------------------------------
#
# This gets the color from our index_to_color
#
# ------------------------------------------------------------------------
def get_color(world_grid, x, y, index_to_color):
    # Get color from your index-to-color mapping
    colors = index_to_color[world_grid[y][x]]

    # Converts from RGB format to normalized
    r_norm = colors[0] / 255
    g_norm = colors[1] / 255
    b_norm = colors[2] / 255

    tile_color = color.rgb(r_norm, g_norm, b_norm)

    return tile_color