import numpy as np
import matplotlib.pyplot as plt

# TODO - Generalize
def get_colors():
    return [0, 10, 60, 90]

# Method for displaying an image after converting color indices to colors.
def show_im(im, colors, ax=None):
    temp_im = np.array(im, dtype=np.uint8)
    for i in range(len(colors)):
        temp_im[temp_im == i] = colors[i]
    if ax == None:
        plt.imshow(temp_im, cmap='terrain', vmin=0, vmax=255)
    else:
        ax.imshow(temp_im, cmap='terrain', vmin=0, vmax=255)

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

# ------------------------------------------------------------------------
#
# Reverse the Hash based on number of colors
#
# ------------------------------------------------------------------------
def reverse_hash(num, numColors,tile_size):
    tile = np.zeros(tile_size * tile_size, dtype=np.int64)
    n = num

    for i in range(len(tile)):
        tile[i] = n % numColors
        n = n // numColors

    return tile.reshape((tile_size, tile_size))

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

# This is for matching borders of tiles
def compare_hashes(h1, h2, t1_border, t2_border,numColors):
    assert len(t1_border) == len(t2_border), "Border Sizes Must Match"

    for i in range(len(t1_border)):
        if (h1 // numColors**t1_border[i]) % numColors != (h2 // numColors**t2_border[i]) % numColors:
            return False
    return True
    
# Bad intersection code for temporary work...
def intersect(a1, a2):
    dest = []

    for a in a1:
        if a in a2:
            dest.append(a)

    return dest

# TODO - This does not account for stride
def collect_tileset(tilemap, tilemap_size, tile_size):
    l = tilemap_size - tile_size + 1
    tiles = np.zeros((l, l, tile_size, tile_size))

    for i, j in np.ndindex((l, l)):
        tiles[i, j] = tilemap[i:i+tile_size, j:j+tile_size]

    tile_set = {}

    for i in range(l):
        for j in range(l):
            val = hash_tile(tiles[i,j])

            if val not in tile_set.keys():
                tile_set[val] = 1
            else:
                tile_set[val] += 1
    
    return tile_set

# TODO - This does not account for stride
def collect_bitwise_tileset(tilemap, tilemap_size, tile_size):
    l = tilemap_size - tile_size + 1
    tiles = np.zeros((l, l, tile_size, tile_size))

    for i, j in np.ndindex((l, l)):
        tiles[i, j] = tilemap[i:i+tile_size, j:j+tile_size]

    tile_set = {}

    for i in range(l):
        for j in range(l):
            val = hash_tile(tiles[i,j], numColors=4)

            if val not in tile_set.keys():
                tile_set[val] = 1
            else:
                tile_set[val] += 1

    # We need to create a way to convert from the hashes to an index
    hash_to_num = {} # Convert a hash into an index for a bit flag
    num_to_hash = {} # Convert an index for a bit flag into a hash
    for i, val in enumerate(tile_set.keys()):
        hash_to_num[val] = i
        num_to_hash[i] = val
    
    return hash_to_num, num_to_hash, tile_set


def collect_reverse_adjacencies(hash_to_num, tile_set, numColors, num_states, 
    directions=['t','r','b','l'], tile_size=2, stride=1):

    args = np.arange(tile_size**2).reshape((tile_size, tile_size))
    top = args[:-stride].flatten()
    bottom = args[stride:].flatten()
    right = args[:,stride:].flatten()
    left = args[:,:-stride].flatten()

    t1_comparisons = [top, right, bottom, left]
    t2_comparisons = [bottom, left, top, right]

    # Encode an adjacency matrix 
    rev_adjacencies = {}

    # Intialize matrices
    for d in directions:
        rev_adjacencies[d] = np.zeros((num_states, num_states), dtype=bool)

    # Detect adjacencies
    for source in tile_set.keys():
        for sink in tile_set.keys():

            for d in range(len(directions)):
                if compare_hashes(source, sink, t1_comparisons[d], t2_comparisons[d], numColors):
                    # State i allows neighboring state j
                    i = hash_to_num[source]
                    j = hash_to_num[sink]
                    rev_adjacencies[directions[d]][i, j] = 1

    return rev_adjacencies