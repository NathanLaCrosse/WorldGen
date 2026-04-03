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

# TODO - This has a fixed size
def hash_tile(tile):
    return int(tile[0,0] + 4 * tile[0, 1] + 16 * tile[1, 0] + 64 * tile[1,1])

# TODO - This has a fixed size
def reverse_hash(num):
    tile = np.zeros(4)
    n = num
    for i in range(len(tile)):
        tile[i] = n % 4
        n = n // 4
    return tile.reshape((2,2))

# TODO - This has a fixed size
# This is for matching borders of tiles
def compare_hashes(h1, h2, t1_border, t2_border):
    assert len(t1_border) == len(t2_border), "Border Sizes Must Match"

    for i in range(len(t1_border)):
        if (h1 // 4**t1_border[i]) % 4 != (h2 // 4**t2_border[i]) % 4:
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
            val = hash_tile(tiles[i,j])

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

# TODO - Add bitwise operations, generalize to larger tile sizes
def collect_adjacencies(tile_set):
    directions =     ['t',  'tr', 'tl', 'r', 'l',    'b', 'br', 'bl']
    t1_comparisons = [[0,1], [1], [0], [1,3], [0,2], [2,3], [3], [2]]
    t2_comparisons = [[2,3], [2], [3], [0,2], [1,3], [0,1], [0], [1]]
    adjacencies = {}

    for t in tile_set.keys():
        # t is the current tile to compute adjacencies for
        # adjacencies[(t, 't')] = []
        for d in range(len(directions)):
            adjacencies[(t, directions[d])] = []

        for target in tile_set.keys():
            # if t == target:
            #     continue # Avoid checking adjacencies against yourself

            for d in range(len(directions)):
                if compare_hashes(t, target, t1_comparisons[d], t2_comparisons[d]) and target not in adjacencies[(t, directions[d])]:
                    adjacencies[(t, directions[d])].append(target)
    
    return adjacencies

# TODO - generalize to larger tile sizes
def collect_adjacencies_bitwise(hash_to_num, tile_set):
    directions =     ['t',  'tr', 'tl', 'r', 'l',    'b', 'br', 'bl']
    t1_comparisons = [[0,1], [1], [0], [1,3], [0,2], [2,3], [3], [2]]
    t2_comparisons = [[2,3], [2], [3], [0,2], [1,3], [0,1], [0], [1]]
    adjacencies = {}

    for t in tile_set.keys():
        for d in range(len(directions)):
            s = 0 # This sum keeps track of all states that we could be in (as bit flags)

            for target in tile_set.keys():
                # if t == target:
                #     continue # Avoid checking adjacencies against yourself
            
                if compare_hashes(t, target, t1_comparisons[d], t2_comparisons[d]):
                    s += 2**hash_to_num[target] # Add bit flag to s
            
            adjacencies[(t, directions[d])] = s
    
    return adjacencies

def collect_reverse_adjacencies(hash_to_num, tile_set):
    # Given a state and a direction used to reach it, what did that previous state
    # have to have? (as a bitmask)
    directions =     ['t',  'tr', 'tl', 'r', 'l',    'b', 'br', 'bl']
    t1_comparisons = [[0,1], [1], [0], [1,3], [0,2], [2,3], [3], [2]]
    t2_comparisons = [[2,3], [2], [3], [0,2], [1,3], [0,1], [0], [1]]
    rev_adjacencies = {}

    for t in tile_set.keys():
        for d in range(len(directions)):
            s = 0 # Sum of possible supporting states

            for target in tile_set.keys():
                if compare_hashes(target, t, t1_comparisons[d], t2_comparisons[d]):
                    s += 2**hash_to_num[target]
            
            rev_adjacencies[(t, directions[d])] = s
    
    return rev_adjacencies

