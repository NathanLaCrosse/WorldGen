from WaveCell import *

dir_steps = [(-1, 0), (-1, 1), (-1, -1), (0, 1), (0, -1), (1, 0), (1, 1), (1, -1)]
directions = ['t', 'tr', 'tl', 'r', 'l', 'b', 'br', 'bl']
op_directions = ['b', 'bl', 'br', 'l', 'r', 't', 'tl', 'tr']

# directions = ['t', 'r', 'b', 'l']
# dir_steps = [(-1,0), (0,1), (1,0), (0,-1)]
# op_directions = ['b', 'l', 't', 'r']

def build_grid_from_cell_space(cell_space, gen_size, tile_size=2):
    grid = np.zeros((gen_size,gen_size))

    space_size = gen_size - tile_size + 1
    for i, j in np.ndindex((space_size, space_size)):
        grid[i:i+tile_size, j:j+tile_size] = reverse_hash(cell_space[i][j].state)

    return grid

# Fully recursive method has unlimited backtracking but greatly extends runtime
# Will guarantee a valid answer
def generate_fully_recursive(tilemap, gen_size, tile_size=2):
    map_size = len(tilemap)

    hash_to_num, num_to_hash, tile_set = collect_bitwise_tileset(tilemap, map_size, tile_size)

    adjacencies = collect_adjacencies_bitwise(hash_to_num, tile_set)

    space_size = gen_size - tile_size + 1

    # reverse_adjacencies = {}

    # for (tile, direction), bitmask in adjacencies.items():
    #     for i in range(len(hash_to_num)):
    #         if bitmask & (1 << i):
    #             neighbor_tile = num_to_hash[i]
    #             key = (neighbor_tile, direction)

    #             if key not in reverse_adjacencies:
    #                 reverse_adjacencies[key] = 0

    #             reverse_adjacencies[key] |= (1 << hash_to_num[tile])

    res = False
    while not res:
        cell_space = [ [Cell(tile_set, hash_to_num, num_to_hash, adjacencies, i, j) 
                    for j in range(space_size)] for i in range(space_size)]
        res = collapse_grid_fully_recursive(cell_space, 0, space_size, tile_size)
        print('uh')

    plt.axis('off')
    fig, ax = plt.subplots(space_size, space_size)
    for i, j in np.ndindex(space_size, space_size):
        show_im(reverse_hash(cell_space[i][j].state), get_colors(), ax[i,j])
    # plt.show()

    # return build_grid_from_cell_space(cell_space, gen_size, tile_size), res


def collapse_grid_fully_recursive(cell_space, collapse_count, space_size, tile_size):
    if collapse_count == space_size*space_size:
        return True # We were successful!
    
    # Find the next available cell via lowest entropy
    entropy_grid = np.zeros((space_size, space_size))
    for i, j in np.ndindex(space_size, space_size):
        entropy_grid[i,j] = cell_space[i][j].entropy()

    # If there is a state with zero entropy, it has no options, meaning we've reached an invalid state
    if entropy_grid.min() == 0:
        return False
    
    w = np.argwhere(entropy_grid == entropy_grid.min())
    row, col = w[np.random.choice(np.arange(w.shape[0]))]

    cell = cell_space[row][col]
    original_superposition = cell.superposition

    # Check to see if we can collapse into a valid state 
    while cell.superposition > 0:
        queue = []
        cell.collapse(queue)

        queue = deque(queue)

        modifications = deque()

        # Perform a BFS to thin out states across the entire space
        is_valid = True
        while len(queue) > 0:
            pos = queue.popleft()

            if pos[0] < 0 or pos[0] > space_size-1 or pos[1] < 0 or pos[1] > space_size-1:
                continue  # Skip if out-of-bounds

            prop_cell = cell_space[pos[0]][pos[1]]

            old_superposition = prop_cell.superposition
            new_superposition = prop_cell.superposition

            # Use all neighbors to update the cell
            for d in range(len(directions)):
                step = dir_steps[d]

                # NOTE - We actually want to travel in the opposite direction, as the neighbor is being compared to the current cell
                neighbor_pos = (pos[0] - step[0], pos[1] - step[1])

                if neighbor_pos[0] < 0 or neighbor_pos[0] > space_size-1 or neighbor_pos[1] < 0 or neighbor_pos[1] > space_size-1:
                    continue
                
                # new_superposition &= prop_cell.advanced_narrow(cell_space[neighbor_pos[0]][neighbor_pos[1]].superposition, directions[d])

                neighbor = cell_space[neighbor_pos[0]][neighbor_pos[1]]
                c = neighbor.superposition
                combined_possibilities = 0 

                for i in range(neighbor.num_states):
                    index_present = c & 1
                    
                    if index_present:
                        combined_possibilities |= neighbor.adjacencies[(neighbor.index_to_hash[i], directions[d])]
                    c = c >> 1
                
                new_superposition &= combined_possibilities

            # Grab new superposition
            if new_superposition != old_superposition:
                if new_superposition == 0:
                    is_valid = False
                    break

                modifications.append((prop_cell, old_superposition))
                prop_cell.superposition = new_superposition
                
                # Continue BFS
                for i in range(len(directions)):
                    step = dir_steps[i]
                    queue.append((pos[0] + step[0], pos[1] + step[1]))


        
        # If valid, recurse deeper.
        if is_valid:
            result = collapse_grid_fully_recursive(cell_space, collapse_count+1, space_size, tile_size)

            if result:
                return True
            # If false, keep looping
        
        # If not valid, revert 
        for c, old_superposition in reversed(modifications):
            c.superposition = old_superposition
        cell.superposition &= ~(2**cell.hash_to_index[cell.state])
        cell.state = -1

    if collapse_count == 0:
        pass

    # There are no possible states that we choose - all end up with an invalid grid
    # We need to backtrack, so revert this state back to where it was.
    cell.superposition = original_superposition
    cell.state = -1

    return False


# Iterative method attempts 
def generate_fully_iterative(tilemap, gen_size, tile_size=2, num_attemps=100):
    map_size = len(tilemap)

    hash_to_num, num_to_hash, tile_set = collect_bitwise_tileset(tilemap, map_size, tile_size)

    adjacencies = collect_adjacencies_bitwise(hash_to_num, tile_set)

    space_size = gen_size - tile_size + 1

    it = 0
    while it < num_attemps:
        # Attempt to generate a map, reroll the whole grid if we run into an invalid
        # tile.
        cell_space = [ [Cell(tile_set, hash_to_num, num_to_hash, adjacencies, i, j) 
                    for j in range(space_size)] for i in range(space_size)]
        
        num_collapsed = 0

        # Try to collapse the whole grid. This while loop is break early if failed
        while num_collapsed < space_size**2:
            entropy_grid = np.zeros((space_size, space_size))

            for i, j in np.ndindex(space_size, space_size):
                entropy_grid[i,j] = cell_space[i][j].entropy()

            # End early if there is an invalid tile.
            if entropy_grid.min() == 0:
                break  

            # Select a cell with minimum entropy
            w = np.argwhere(entropy_grid == entropy_grid.min())
            row, col = w[np.random.choice(np.arange(w.shape[0]))]

            # Collapse the cell
            cell = cell_space[row][col]
            queue = []
            cell.collapse(queue)

            # Update neighbors
            for q in queue:
                pos = q[0]

                if pos[0] < 0 or pos[0] > space_size-1 or pos[1] < 0 or pos[1] > space_size-1:
                    continue  # Skip if out-of-bounds

                possibilities = q[1]
                cell_space[pos[0]][pos[1]].narrow(possibilities)
            
            # Increment collapse counter
            num_collapsed += 1
        
        # At this point, we've either collapsed the whole grid or failed to do so.
        if num_collapsed == space_size**2:
            return build_grid_from_cell_space(cell_space, gen_size), True
        else:
            it += 1 # Start over
    
    # At this point, we've ran out of attempts to generate sucessfully, so return a
    # partial answer
    return build_grid_from_cell_space(cell_space, gen_size), False
            





if __name__ == '__main__':
    tilemap = np.ones((10,10))

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
    generate_fully_recursive(tilemap, 4, 2)
    # show_im(grid, get_colors())
    # print(result)
    plt.show()