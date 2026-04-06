from TileCollection import *
from collections import deque
import sys

sys.setrecursionlimit(10**6)

# dir_steps = [(-1, 0), (-1, 1), (-1, -1), (0, 1), (0, -1), (1, 0), (1, 1), (1, -1)]
# directions = ['t', 'tr', 'tl', 'r', 'l', 'b', 'br', 'bl']
# op_directions = ['b', 'bl', 'br', 'l', 'r', 't', 'tl', 'tr']

# t1_comparisons = [[0,1], [1], [0], [1,3], [0,2], [2,3], [3], [2]]
# t2_comparisons = [[2,3], [2], [3], [0,2], [1,3], [0,1], [0], [1]]

directions = ['t', 'r', 'b', 'l']
dir_steps = [(-1,0), (0,1), (1,0), (0,-1)]
op_directions = ['b', 'l', 't', 'r']

t1_comparisons = [[0,1], [1,3], [0,2], [2,3]]
t2_comparisons = [[2,3], [0,2], [1,3], [0,1]]

def is_tile_possible(cell_space, row, col, tile_index):
    chunk = tile_index // 64
    bit = tile_index % 64
    return (cell_space[row, col, chunk] >> bit) & 1

def set_tile(cell_space, row, col, tile_index):
    """
    Collapse a cell to a single tile
    """
    num_chunks = cell_space.shape[2]
    # Clear all chunks first
    for chunk in range(num_chunks):
        cell_space[row, col, chunk] = 0
    # Set the bit corresponding to tile_index
    chunk = tile_index // 64
    bit = tile_index % 64
    cell_space[row, col, chunk] = 1 << bit

def remove_tile(cell_space, row, col, tile_index):
    """
    Remove a tile from possible states at a cell
    """
    chunk = tile_index // 64
    bit = tile_index % 64
    mask = np.uint64(1) << np.uint64(bit)
    cell_space[row, col, chunk] &= ~mask

def count_possible_tiles(cell_space, row, col):
    """
    Count how many tiles are still possible at a cell
    """
    count = 0
    num_chunks = cell_space.shape[2]
    for chunk in range(num_chunks):
        x = cell_space[row, col, chunk]
        while x:
            count += x & 1
            x >>= 1
    return count

def get_possible_tiles(cell_space, row, col, num_states):
    """
    Return a list of all tile indices possible at a cell
    """
    tiles = []
    for tile_index in range(num_states):
        if is_tile_possible(cell_space, row, col, tile_index):
            tiles.append(tile_index)
    return tiles

def get_superposition(cell_space, pos):
    """
    Return combined int representing all possible tiles at a position
    """
    r, c = pos
    val = 0
    for chunk in range(cell_space.shape[2]):
        val |= int(cell_space[r, c, chunk]) << (chunk * 64)
    return val

def gen_entropy_grid(cell_space, state_space, num_states):
    rows, cols = state_space.shape
    entropy_grid = np.zeros((rows, cols), dtype=np.int64)
    entropy_grid[state_space != -1] = 100000

    for r in range(rows):
        for c in range(cols):
            if state_space[r, c] == -1:
                entropy_grid[r, c] += count_possible_tiles(cell_space, r, c)

    return entropy_grid

def superposition_adjacencies(cell_space, index_to_hash, adjacencies, num_states, direction, row, col):
    allowed_adjacencies = 0

    c = cell_space[row, col]
    for i in range(num_states):
        if c & 1:
            allowed_adjacencies |= adjacencies[(index_to_hash[i], direction)]
        c = c >> 1
    
    return allowed_adjacencies

def build_allowed_superposition(cell_space, index_to_hash, rev_adjacencies, num_states, source_pos, sink_pos, direction):
    allowed_sink = 0

    allowed_sink = 0
    for i in range(num_states):
        if is_tile_possible(cell_space, sink_pos[0], sink_pos[1], i) and \
           rev_adjacencies[(index_to_hash[i], direction)] & get_superposition(cell_space, source_pos) != 0:
            allowed_sink |= (1 << i)

    return allowed_sink

def build_grid_from_cell_space(state_space, gen_size, tile_size, numColors):
    grid = np.zeros((gen_size,gen_size), dtype=np.int64)

    space_size = gen_size - tile_size + 1
    for i, j in np.ndindex((space_size, space_size)):
        grid[i:i+tile_size, j:j+tile_size] = reverse_hash(state_space[i,j], numColors, tile_size)

    return grid

# Fully recursive method has unlimited backtracking but greatly extends runtime
# Should guarantee a valid answer
def generate_fully_recursive(tilemap, gen_size, tile_size=2,PNG=False, hash_to_num={},num_to_hash={},tile_set={},numColors=4):
    if(not PNG):
        map_size = len(tilemap)

        hash_to_num, num_to_hash, tile_set = collect_bitwise_tileset(tilemap, map_size, tile_size)
    else:
        map_size = tilemap
    
    num_states = len(tile_set.keys())

    adjacencies = collect_adjacencies_bitwise(hash_to_num, tile_set, numColors)
    rev_adjacencies = collect_reverse_adjacencies(hash_to_num, tile_set, numColors)
    weights = np.array(list(tile_set.values()))
    args = np.arange(num_states)

    space_size = gen_size - tile_size + 1

    num_chunks = num_states // 64 + 1

    cell_space = np.ones((space_size, space_size, num_chunks), dtype=np.uint64)

    # Fill all bits to 1
    for chunk in range(num_chunks):
        if chunk == num_chunks - 1:
            remaining_bits = num_states % 64 or 64
            cell_space[:, :, chunk] = (1 << remaining_bits) - 1  # this is safe if remaining_bits < 64
        else:
            cell_space[:, :, chunk] = np.uint64(0xFFFFFFFFFFFFFFFF)  # all 64 bits set

    state_space = np.ones((space_size, space_size), dtype=np.int64) * -1

    res = collapse_grid_fully_recursive(cell_space, state_space, args, weights, num_to_hash, 
        hash_to_num, adjacencies, rev_adjacencies, num_states, 0, space_size)
    
    # Return the grid and whether or not the generation was successful (certain tilemaps may have no valid solution)
    return build_grid_from_cell_space(state_space, gen_size, tile_size, numColors), res

def collapse_grid_fully_recursive(cell_space, state_space, args, weights, index_to_hash, hash_to_index, adjacencies, rev_adjacencies, num_states, collapse_count, space_size):
    if collapse_count == space_size*space_size:
        return True # We were successful!
    
    # Find the next available cell via lowest entropy
    entropy_grid = gen_entropy_grid(cell_space, state_space, num_states)

    # If there is a state with zero entropy, it has no options, meaning we've reached an invalid state
    if entropy_grid.min() == 0:
        return False

    w = np.argwhere(entropy_grid == entropy_grid.min())
    row, col = w[np.random.choice(np.arange(w.shape[0]))]

    original_superposition = np.copy(cell_space[row, col, :])

    while np.any(cell_space[row, col]):
        queue = deque()
        modifications = deque()

        # Collapse the superposition
        # Gather the probability distribution to sample from
        possible_tiles = get_possible_tiles(cell_space, row, col, num_states)
        p = np.array([weights[i] for i in possible_tiles], dtype=np.float64)
        p /= p.sum()

        index = np.random.choice(possible_tiles, p=p)
        set_tile(cell_space, row, col, index)  # collapse to a single tile
        state_space[row, col] = index_to_hash[index]

        # Add neighbors to propogation queue
        for i in range(len(directions)):
            step = dir_steps[i]

            if row + step[0] < 0 or row + step[0] > space_size-1 or col + step[1] < 0 or col + step[1] > space_size-1:
                continue

            adj = build_allowed_superposition(cell_space, index_to_hash, rev_adjacencies, 
                num_states, (row, col), (row + step[0], col + step[1]), directions[i])
            queue.append((row + step[0], col + step[1], adj))

        # Perform a BFS
        is_valid = True
        while len(queue) > 0:
            qr, qc, adj = queue.popleft()

            if qr < 0 or qr > space_size-1 or qc < 0 or qc > space_size-1:
                continue  # Skip if out-of-bounds
            if state_space[qr, qc] != -1:
                continue  # Skip if state is collapsed
            
            # update based on given adjacencies
            old_cell = np.copy(cell_space[qr, qc])
            for tile_index in range(num_states):
                if not ((adj >> tile_index) & 1):
                    remove_tile(cell_space, qr, qc, tile_index)

            if not np.array_equal(old_cell, cell_space[qr, qc]):
                if np.all(cell_space[qr, qc] == 0):
                    # No tiles possible at this cell
                    is_valid = False
                    break

                # Add to backprop queue
                modifications.append((qr, qc, old_cell))

                # Propagate further 
                for i in range(len(directions)):
                    step = dir_steps[i]

                    if qr + step[0] < 0 or qr + step[0] > space_size-1 or qc + step[1] < 0 or qc + step[1] > space_size-1:
                        continue

                    adj = build_allowed_superposition(cell_space, index_to_hash, 
                        rev_adjacencies, num_states, (qr, qc), (qr + step[0], qc + step[1]), 
                        directions[i])
                    queue.append((qr + step[0], qc + step[1], adj))
        
        # If valid, recurse deeper.
        if is_valid:
            # Recursive call
            result = collapse_grid_fully_recursive(cell_space, state_space, args, weights, 
                index_to_hash, hash_to_index, adjacencies, rev_adjacencies,  num_states, 
                collapse_count + 1, space_size)

            if result:
                return True
            
        # If invalid, revert changes
        # If not valid, revert 
        for r, c, old_superposition in reversed(modifications):
            cell_space[r, c] = old_superposition
        remove_tile(cell_space, row, col, index)
        state_space[row, col] = -1
    
    # There are no possible states that we choose - all end up with an invalid grid
    # We need to backtrack, so revert this state back to where it was.
    cell_space[row, col] = original_superposition
    state_space[row, col] = -1

    return False



if __name__ == '__main__':
    tilemap = np.ones((11,10))

    tilemap[0:2, :] = 3
    tilemap[2:3, :7] = 3
    tilemap[3:5, :5] = 3
    tilemap[4, 5:7] = 3
    tilemap[5, :3] = 3
    tilemap[2, -1] = 3

    tilemap[1:3, 1:3] = 2
    tilemap[1, 3] = 2
    tilemap[2,4] = 2

    tilemap[7, 4:8] = 0
    tilemap[8:10, 5:8] = 0

    # tilemap = np.ones((5,5)) * 3

    # tilemap[2:5, 2:5] = 2
    # tilemap[1, 2] = 2
    # tilemap[2, 1] = 2

    # grid, result = generate_fully_recursive(tilemap, 4, 2)
    grid = generate_fully_recursive(tilemap, 30, 2)
    show_im(grid, get_colors())
    # print(result)
    plt.show()