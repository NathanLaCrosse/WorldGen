"""----------------------------------------------------------------

This is our main wave function handler

Has hash table lookups, and builders for the use later on. 
re-indexes the colors and determines adjacency rules

Dylan Dudley - 03/28/2026

----------------------------------------------------------------"""


from FunctsFromCell2 import Cell, collapse_grid
from WorldGrid import build_world_grid
from SampleDisplay import waveDisplay


#TODO NEED TO KEEP TRACK OF HOW MANY COLORS
# Note THIS IS TEMP, can change the one in CELL so it can be callable for these types of functions
def hash_tile(tile):
    return tile[0] + 4*tile[1] + 16*tile[2] + 64*tile[3]

# To create a table that has the tiles and weights
def build_tile_lookup(tiles, weights):
    hash_to_tile = {}
    hash_to_weight = {}

    for i in range(len(tiles)):
        h = hash_tile(tiles[i])
        hash_to_tile[h] = tiles[i]
        hash_to_weight[h] = weights[i]

    return hash_to_tile, hash_to_weight


# main handler
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

    waveDisplay(world_grid,grid_size,index_to_color)


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
    for i in range(len(tiles)):
            colors.append([
                        get_color_index(tiles[i][0]),        # top-left
                        get_color_index(tiles[i][1]),        # top-right
                        get_color_index(tiles[i][2]),        # bottom-left
                        get_color_index(tiles[i][3])         # bottom-right
                        ])
    
    # Hash the tiles 
    tile_hashes = [hash_tile(tile) for tile in colors]
    hash_to_tile, hash_to_weight = build_tile_lookup(colors, weights)

    # Directions for adjacency (must match Cell class)
    directions = ['t', 'tr', 'tl', 'r', 'l', 'b', 'br', 'bl']
    t1_comparisons = [[0,1], [1], [0], [1,3], [0,2], [2,3], [3], [2]]
    t2_comparisons = [[2,3], [2], [3], [0,2], [1,3], [0,1], [0], [1]]

    # Build adjacency rules
    adjacencies = {}
    for i, h1 in enumerate(tile_hashes):
        for dir_idx, d in enumerate(directions):
            adjacencies[(h1, d)] = []

            for j, h2 in enumerate(tile_hashes):
                valid = True
                for k in range(len(t1_comparisons[dir_idx])):
                    if colors[i][t1_comparisons[dir_idx][k]] != colors[j][t2_comparisons[dir_idx][k]]:
                        valid = False
                        break
                if valid:
                    adjacencies[(h1, d)].append(h2)

    return tile_hashes, hash_to_tile, hash_to_weight, adjacencies, color_to_index, index_to_color
    