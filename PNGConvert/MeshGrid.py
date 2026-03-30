"""----------------------------------------------------------------

This creates a mesh to display the images

Dylan Dudley - 03/30/2026

----------------------------------------------------------------"""
from ursina import *

def startMesh(world_grid, grid_size, index_to_color):
    create_mesh(world_grid, grid_size,index_to_color)
    return

def create_mesh(world_grid, grid_size, index_to_color, tile_size=1):
    tiles_holder = []
    triangles = []
    colors = []

    # Use actual world_grid size (overlapping)
    rows, cols = world_grid.shape  

    for y in range(rows):
        for x in range(cols):
            quad_tile = [
                Vec3(x * tile_size, y * tile_size, -10),
                Vec3((x+1) * tile_size, y * tile_size, -10),
                Vec3((x+1) * tile_size, (y+1) * tile_size, -10),
                Vec3(x * tile_size, (y+1) * tile_size, -10)
            ]
            tiles_holder.extend(quad_tile)
            idx = len(tiles_holder) - 4
            triangles.extend([idx, idx+1, idx+2, idx, idx+2, idx+3])

            colors.extend([get_color(world_grid,x,y,index_to_color)]*4)
    

    mesh = Mesh(vertices=tiles_holder, triangles=triangles, colors=colors, mode='triangle')
    entity = Entity(model=mesh)
    return entity, mesh


def get_color(world_grid, x, y, index_to_color):
    # Get color from your index-to-color mapping
    colors = index_to_color[world_grid[y][x]]
    r_norm = colors[0] / 255
    g_norm = colors[1] / 255
    b_norm = colors[2] / 255
    tile_color = color.rgb(r_norm, g_norm, b_norm)

    return tile_color