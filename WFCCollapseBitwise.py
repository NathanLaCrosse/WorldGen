from WaveCell import *
import random

def build_grid_from_cell_space(cell_space, gen_size, tile_size=2):
    grid = np.zeros((gen_size,gen_size))

    space_size = gen_size - tile_size + 1
    for i, j in np.ndindex((space_size, space_size)):
        grid[i:i+tile_size, j:j+tile_size] = reverse_hash(cell_space[i][j].state)

    return grid

# Fully recursive method has unlimited backtracking but greatly extends runtime
# Will guarantee a valid answer
def generate_fully_recursive(tilemap, gen_size, tile_size=2,PNG=False, hash_to_num={},num_to_hash={},tile_set={}):
    if(not PNG):
        map_size = len(tilemap)

        hash_to_num, num_to_hash, tile_set = collect_bitwise_tileset(tilemap, map_size, tile_size)
    else:
        map_size = tilemap

    adjacencies = collect_adjacencies_bitwise(hash_to_num, tile_set)

    print(hash_to_num, "\n\n\n", num_to_hash, "\n\n\n", tile_set, "\n\n\n", adjacencies)

    space_size = gen_size - tile_size + 1
    cell_space = [ [Cell(tile_set, hash_to_num, num_to_hash, adjacencies, i, j) 
                    for j in range(space_size)] for i in range(space_size)]
    
    # start_row = random.randint(0, space_size-1)
    # start_col = random.randint(0, space_size-1)

    collapse_grid_fully_recursive(cell_space, 0, space_size, tile_size)

    return build_grid_from_cell_space(cell_space, gen_size, tile_size)


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
    # if cell.superposition == 0:
    #     # We ran out of available states before reaching this cell...
    #     return False
    
    original_superposition = cell.superposition

    # Check to see if we can collapse into a valid state 
    while cell.superposition > 0:
        queue = []
        cell.collapse(queue)

        is_valid = True
        for q in queue:
            pos = q[0]

            if pos[0] < 0 or pos[0] > space_size-1 or pos[1] < 0 or pos[1] > space_size-1:
                continue  # Skip if out-of-bounds

            possibilities = q[1]
            cell_space[pos[0]][pos[1]].narrow(possibilities)

            if cell_space[pos[0]][pos[1]].superposition == 0:
                is_valid = False # This cell has no legal states
        
        # If valid, recurse deeper.
        if is_valid:
            

            # Choose the cell with minimum entropy
            # new_row, new_col = np.unravel_index(np.argmin(entropy_grid), entropy_grid.shape)
            
            result = collapse_grid_fully_recursive(cell_space, collapse_count+1, space_size, tile_size)

            if result:
                return True
            # If false, keep looping
        
        # If invalid, reverse everything and continue (revert collapse)
        queue = []
        cell.reverse_collapse(queue) # Note - removes current state from superposition

        for q in queue:
            pos = q

            if pos[0] < 0 or pos[0] > space_size-1 or pos[1] < 0 or pos[1] > space_size-1:
                continue  # Skip if out-of-bounds

            cell_space[pos[0]][pos[1]].reverse_narrow()
        
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

    grid = generate_fully_recursive(tilemap, 7, 2)
    show_im(grid, get_colors())
    # print(result)
    plt.show()