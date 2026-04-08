from TileCollection import *
from collections import deque
import sys

sys.setrecursionlimit(10**6)

directions = ['t', 'r', 'b', 'l']
dir_steps = [(-1,0), (0,1), (1,0), (0,-1)]
op_directions = ['b', 'l', 't', 'r']

t1_comparisons = [[0,1], [1,3], [0,2], [2,3]]
t2_comparisons = [[2,3], [0,2], [1,3], [0,1]]


def gen_entropy_grid(cell_space, state_space, num_states):
    entropy_grid = np.zeros_like(state_space)
    entropy_grid[state_space != -1] = 100000

    entropy_grid += cell_space.sum(-1)

    return entropy_grid


def build_allowed_superposition(cell_space, index_to_hash, rev_adjacencies, num_states, source_pos, sink_pos, direction):
    c_ar = cell_space[source_pos] # This is a binary array

    # Index the adjacency matrix to find allowed states
    allowed_states = rev_adjacencies[direction][c_ar].any(axis=0) 
    
    return allowed_states & cell_space[sink_pos]

def build_grid_from_cell_space(state_space, gen_size, space_size, tile_size, numColors, stride):
    grid = np.zeros((gen_size,gen_size), dtype=np.int64)

    # space_size = gen_size - tile_size + 1
    # for i, j in np.ndindex((space_size, space_size)):
    #     grid[i:i+tile_size, j:j+tile_size] = reverse_hash(state_space[i,j], numColors, tile_size)

    for i in range(0, space_size):
        for j in range(0, space_size):
            r = i*stride
            c = j*stride
            grid[r:r+tile_size, c:c+tile_size] = reverse_hash(state_space[i,j], numColors, tile_size)

    return grid

# Fully recursive method has unlimited backtracking but greatly extends runtime
# Should guarantee a valid answer
def generate_fully_recursive(tilemap, gen_size, tile_size=2,stride=1,PNG=False, hash_to_num={},num_to_hash={},tile_set={},numColors=4):
    assert (gen_size - tile_size) % stride == 0, "Incompatible Tile/Stride/Grid_Size Combination"
    
    if(not PNG):
        map_size = len(tilemap)

        hash_to_num, num_to_hash, tile_set = collect_bitwise_tileset(tilemap, map_size, tile_size)
    else:
        map_size = tilemap
    
    num_states = len(tile_set.keys())

    rev_adjacencies = collect_reverse_adjacencies(hash_to_num, tile_set, numColors, num_states, tile_size=tile_size, stride=stride)
    
    # Stuff for sampling from superpositions
    weights = np.array(list(tile_set.values()))
    args = np.arange(num_states)

    # space_size = gen_size - tile_size + 1
    space_size = (gen_size - tile_size)//stride + 1

    cell_space = np.ones((space_size, space_size, num_states), dtype=bool)
    state_space = np.ones((space_size, space_size), dtype=np.int64) * -1

    res = collapse_grid_fully_recursive(cell_space, state_space, args, weights, num_to_hash, 
        hash_to_num, rev_adjacencies, num_states, 0, space_size)

    # Return the grid and whether or not the generation was successful (certain tilemaps may have no valid solution)
    return build_grid_from_cell_space(state_space, gen_size, space_size, tile_size, numColors, stride), res

def collapse_grid_fully_recursive(cell_space, state_space, args, weights, index_to_hash, hash_to_index, rev_adjacencies, num_states, collapse_count, space_size, entropy_grid = None):
    if collapse_count == space_size*space_size:
        return True # We were successful!
    
    # Find the next available cell via lowest entropy
    if entropy_grid is None:
        entropy_grid = gen_entropy_grid(cell_space, state_space, num_states)

    # If there is a state with zero entropy, it has no options, meaning we've reached an invalid state
    if entropy_grid.min() == 0:
        return False

    w = np.argwhere(entropy_grid == entropy_grid.min())
    row, col = w[np.random.choice(np.arange(w.shape[0]))]

    original_superposition = cell_space[row, col].copy()
    current_superposition = cell_space[row, col]

    while cell_space[row, col].any() > 0:
        queue = deque()
        modifications = deque()

        # Collapse the superposition
        # Gather the probability distribution to sample from
        c = cell_space[row, col]
        p = weights.copy()
        
        p[c == False] = 0 # Zero out invalid weights

        # Choose a random state index - update board accordingly
        index = np.random.choice(args, p=p/p.sum())
        cell_space[row, col] = np.zeros(num_states, dtype=bool)
        cell_space[row, col, index] = True
        state_space[row, col] = index_to_hash[index]
        entropy_grid[row, col] = 1 + 100000

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
            old_cell = cell_space[qr, qc].copy()
            cell_space[qr,qc] &= adj

            # Check if the old state is different than the new state
            if (old_cell ^ cell_space[qr, qc]).any() > 0:
                if cell_space[qr, qc].sum() == 0:
                    is_valid = False
                    break

                # Update entropy grid
                old_entropy = entropy_grid[qr, qc]
                entropy_grid[qr, qc] = cell_space[qr, qc].sum()
                if state_space[qr, qc] != -1:
                    entropy_grid[qr, qc] += 100000

                # Add to backprop queue
                modifications.append((qr, qc, old_cell, old_entropy))

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
                index_to_hash, hash_to_index, rev_adjacencies,  num_states, 
                collapse_count + 1, space_size, entropy_grid=entropy_grid)

            if result:
                return True
            
        # If invalid, revert changes
        # If not valid, revert 
        for r, c, old_superposition, old_entropy in reversed(modifications):
            cell_space[r, c] = old_superposition
            entropy_grid[r, c] = old_entropy

        mask = np.ones_like(current_superposition)
        mask[index] = 0
        cell_space[row, col] = current_superposition & mask
        current_superposition = cell_space[row, col]
        state_space[row, col] = -1
    
    # There are no possible states that we choose - all end up with an invalid grid
    # We need to backtrack, so revert this state back to where it was.
    cell_space[row, col] = original_superposition
    state_space[row, col] = -1
    entropy_grid[row, col] = original_superposition.sum()

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

    # grid, result = generate_fully_recursive(tilemap, 4, 2)
    grid, result = generate_fully_recursive(tilemap, 32, 2)
    show_im(grid, get_colors())
    print(result)
    plt.show()