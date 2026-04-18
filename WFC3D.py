from TileCollection3D import *
from collections import deque
import pickle

sys.setrecursionlimit(10**6)

directions = ['t','b','n','s','e','w']
dir_steps = [(-1,0,0),(1,0,0),(0,-1,0),(0,1,0),(0,0,1),(0,0,-1)]

# Gensize (int) -> tuple of ints
def generate_3D_fully_recursive(gen_size, tile_to_dex, dex_to_tile, weights, num_colors, tile_size=2, stride=1, presets=None, rev_adj=None):
    assert (gen_size[0] - tile_size) % stride == 0 and (gen_size[1] - tile_size) % stride == 0 and (gen_size[2] - tile_size) % stride == 0, "Incompatible Tile/Stride/Grid_Size Combination"
    
    num_states = len(dex_to_tile.keys())
    
    if rev_adj is None:
        rev_adj = collect_reverse_adjacencies(dex_to_tile, num_states, tile_size=tile_size, stride=stride)

        print("Adjacencies Built!")

    # Stuff for sampling from superpositions
    weights = np.array(weights)
    args = np.arange(num_states)

    # Calculate dimensions of the cell space
    space_size = ((gen_size[0] - tile_size)//stride + 1, (gen_size[1] - tile_size)//stride + 1, (gen_size[2] - tile_size)//stride + 1)

    # Initialize space
    cell_space = np.ones((space_size[0], space_size[1], space_size[2], num_states), dtype=bool)
    state_space = np.ones((space_size[0], space_size[1], space_size[2]), dtype=np.int64) * -1

    # Intialize entropy grid - all the same since equal superposition
    entropy_grid = np.ones((space_size[0], space_size[1], space_size[2]), dtype=np.uint64) * num_states

    collapsed = 0
    if presets is not None:
        # If presets are passed in, initialized grid with some states
        q = deque()
        m = deque()
        for pos, state_dex in presets:
            enqueue(q, pos, state_dex, cell_space, state_space, entropy_grid, rev_adj, space_size, num_states)
        
        # Propagate changes
        propagate_BFS(q, m, cell_space, state_space, entropy_grid, rev_adj, space_size, num_states)
        collapsed = len(presets)

        print(len(m))

    # Call recursive method to solve for the entire space
    res = recursive_generation(cell_space, state_space, entropy_grid, args, weights, dex_to_tile, tile_to_dex, rev_adj, num_states, collapsed, space_size)

    if res:
        return build_grid_from_cell_space(state_space, gen_size, space_size, tile_size, num_colors, stride, dex_to_tile), res
    else:
        return np.zeros(gen_size), res

def recursive_generation(cell_space, state_space, entropy_grid, args, weights, dex_to_tile, tile_to_dex, rev_adj, 
                         num_states, collapse_count, space_size):
    
    if collapse_count == space_size[0] * space_size[1] * space_size[2]:
        return True # Grid fully generated!
    
    if entropy_grid.min() == 0:
        return False # There is a cell with no valid states!
    
    # use argmin directly
    min_idx = np.argmin(entropy_grid)
    depth, row, col = np.unravel_index(min_idx, entropy_grid.shape)

    original_superposition = cell_space[depth, row, col].copy()
    current_superposition = cell_space[depth, row, col]

    while cell_space[depth, row, col].any() > 0:
        queue = deque()
        modifications = deque()

        # Collapse the superposition
        # Gather the probability distribution to sample from
        c = cell_space[depth, row, col]
        p = weights.copy()

        p[c == False] = 0 # Zero out invalid weights

        # Choose a random state index - update board accordingly
        index = np.random.choice(args, p=p/p.sum())
        enqueue(queue, (depth, row, col), index, cell_space, state_space, entropy_grid, rev_adj, space_size, num_states)

        # Perform a BFS until the grid is no longer getting updated
        is_valid = propagate_BFS(queue, modifications, cell_space, state_space, entropy_grid, rev_adj, space_size, num_states)

        # If we successfully propogate with no contradictions, recurse deeper.
        if is_valid:
            result = recursive_generation(cell_space, state_space, entropy_grid, args, weights, dex_to_tile, tile_to_dex, 
                                          rev_adj, num_states, collapse_count+1, space_size)

            # If we sucessfully recurse, we're done!
            if result:
                return True
        
        # If invalid, revert changes
        # If not valid, revert 
        for d, r, c, old_superposition, old_entropy in reversed(modifications):
            cell_space[d, r, c] = old_superposition
            entropy_grid[d, r, c] = old_entropy
        
        # Remove the state we tried to collapse to from the superposition
        mask = np.ones_like(current_superposition)
        mask[index] = 0
        cell_space[depth, row, col] = current_superposition & mask
        current_superposition = cell_space[depth, row, col]
        state_space[depth, row, col] = -1
    
    # There are no possible states that we choose - all end up with an invalid grid
    # We need to backtrack, so revert this state back to where it was.
    cell_space[depth, row, col] = original_superposition
    state_space[depth, row, col] = -1
    entropy_grid[depth, row, col] = original_superposition.sum()

    return False

def enqueue(queue, pos, state_dex, cell_space, state_space, entropy_grid, rev_adj, space_size, num_states):
    # Only collapse if given a valid state_dex
    if state_dex != -1:
        cell_space[pos] = np.zeros(num_states, dtype=bool)
        cell_space[pos[0], pos[1], pos[2], state_dex] = True
        state_space[pos] = state_dex
        entropy_grid[pos] = 100000

    for i in range(len(directions)):
        step = dir_steps[i]

        # Skip over out-of-bounds nodes
        if (pos[0] + step[0] < 0 or pos[0] + step[0] > space_size[0]-1 or pos[1] + step[1] < 0 or pos[1] + step[1] > space_size[1]-1
                    or pos[2] + step[2] < 0 or pos[2] + step[2] > space_size[2]-1):
            continue
        
        neighbor_pos = (pos[0] + step[0], pos[1] + step[1], pos[2] + step[2])

        adj = build_allowed_superposition(cell_space, rev_adj, pos, neighbor_pos, directions[i])
        queue.append((neighbor_pos[0], neighbor_pos[1], neighbor_pos[2], adj))

def propagate_BFS(queue, modifications, cell_space, state_space, entropy_grid, rev_adj, space_size, num_states):
    # Loop until queue is empty or we finish early
    while queue:
        qd, qr, qc, adj = queue.popleft()

        if qd < 0 or qd > space_size[0]-1 or qr < 0 or qr > space_size[1]-1 or qc < 0 or qc > space_size[2]-1:
            continue  # Skip if out-of-bounds
        elif state_space[qd, qr, qc] != -1:
            continue  # Skip if already collapsed

        # update based on given adjacencies
        old_cell = cell_space[qd, qr, qc].copy()
        cell_space[qd, qr, qc] &= adj

        # Check if the old state is different than the new state
        if (old_cell ^ cell_space[qd, qr, qc]).any() > 0:
            if cell_space[qd, qr, qc].sum() == 0:
                return False # No valid states left - leave loop

            # Update entropy grid
            old_entropy = entropy_grid[qd, qr, qc]
            entropy_grid[qd, qr, qc] = cell_space[qd, qr, qc].sum()
            if state_space[qd, qr, qc] != -1:
                entropy_grid[qd, qr, qc] = 100000

            # Add to backprop queue
            modifications.append((qd, qr, qc, old_cell, old_entropy))

            # Propagate further 
            enqueue(queue, (qd, qr, qc), -1, cell_space, state_space, entropy_grid, rev_adj, space_size, num_states)

    return True

# Unchanged from original wave function collapse except for adjustments to parameters.
def build_allowed_superposition(cell_space, rev_adjacencies, source_pos, sink_pos, direction):
    c_ar = cell_space[source_pos] # This is a binary array

    # Index the adjacency matrix to find allowed states
    allowed_states = rev_adjacencies[direction][c_ar].any(axis=0) 
    
    return allowed_states & cell_space[sink_pos]

# Translate from state space into color index space
def build_grid_from_cell_space(state_space, gen_size, space_size, tile_size, numColors, stride, dex_to_tile):
    grid = np.zeros((gen_size[0],gen_size[1],gen_size[2]), dtype=np.int64)

    for i in range(0, space_size[0]):
        for j in range(0, space_size[1]):
            for k in range(0, space_size[2]):
                d = i*stride
                r = j*stride
                c = k*stride
                grid[d:d+tile_size, r:r+tile_size, c:c+tile_size] = dex_to_tile[state_space[i,j,k]]

    return grid

if __name__ == "__main__":
    gen_size = (6,8,8)
    # gen_size = (2,2,2)
    tile_size = 2
    stride = 1

    mode = "load"
    load_tilemap = True

    rev_adj = None
    if mode == "save":
        tilemap, idx_to_color, color_to_idx = construct_3D_tilemap(7,32,32,png_folder="Generation_3D/images_3D/terraintest", png_names="terrain")

        tiles, weights = collect_3D_tiles(tilemap, tile_size, rotation=True)
        print("Tiles Collected!")

        num_colors = len(idx_to_color.keys())
        num_states = len(tiles)

        tile_to_dex, dex_to_tile = build_3D_tile_hashes(tiles)
        print("Hash Tables Completed!")

        rev_adj = collect_reverse_adjacencies(dex_to_tile, num_states, tile_size=tile_size, stride=stride)
        print("Adjacencies Built!")

        with open("Saved_Data/data.pkl", "wb") as file:
            pickle.dump([tilemap, idx_to_color, color_to_idx, tiles, weights, tile_to_dex, dex_to_tile, rev_adj], file)
        print("Data Saved!")
    
    else:
        with open("Saved_Data/data.pkl", "rb") as file:
            tilemap, idx_to_color, color_to_idx, tiles, weights, tile_to_dex, dex_to_tile, rev_adj = pickle.load(file)
        
        num_colors = len(idx_to_color.keys())
        num_states = len(tiles)

    if not load_tilemap:
        # Set the first layer to stone
        presets = []
        space_size = ((gen_size[0] - tile_size)//stride + 1, (gen_size[1] - tile_size)//stride + 1, (gen_size[2] - tile_size)//stride + 1)
        for i in range(space_size[1]//2):
            for j in range(space_size[2]//2):
                presets.append(((0, i, j), 0))

        space, res = generate_3D_fully_recursive(gen_size, tile_to_dex, dex_to_tile, weights, num_colors, tile_size, stride, presets, rev_adj=rev_adj)
        print("Was space generated correctly?", res)

        if mode == "save" and res:
            with open("Saved_Data/space.pkl", "wb") as file:
                pickle.dump(space, file)
    else:
        space_size = ((gen_size[0] - tile_size)//stride + 1, (gen_size[1] - tile_size)//stride + 1, (gen_size[2] - tile_size)//stride + 1)
        with open("Saved_Data/space.pkl", "rb") as file:
            space = pickle.load(file)
        
        

    # space = space[::-1]

    # create_voxel_mesh(tiles[0], idx_to_color)
    create_voxel_mesh(space.tolist(), idx_to_color)

    chunks = 1
    grid_size = gen_size[0]
    app = Ursina()

    # Sets up the Ursina enviornment

    # Lighting
    # DirectionalLight().look_at(Vec3(1, -1, -1))
    # AmbientLight(color=color.rgba(100, 100, 100, 0.5))

    DirectionalLight(x=grid_size/2,y=1+3, z=grid_size/2, shadows=True, rotation=(45, -45, 45)).look_at(Vec3(1, -1, -1))
    AmbientLight(color=color.rgba(30, 30, 30, 1))

    grid_size = gen_size[0]
    camera_spot = grid_size * chunks / 2

    # Camera
    camera.position = (camera_spot, camera_spot, -(chunks*grid_size*2))
    # camera.position = (0,0,0)
    camera.look_at(Vec3(grid_size/2, -5, 0))


    mouse.locked = True

    def input(key):
        if key == 'q':
            application.quit()
        if key == 'backspace':
            camera.position = (camera_spot, camera_spot, -(chunks * grid_size * 2))
            camera.look_at(Vec3(grid_size/2, -5, 0))

    def update():
        base_speed = 5
        speed_multiplier = 10 if held_keys['shift'] else 1
        speed = base_speed * speed_multiplier * time.dt

        if held_keys['w']:
            camera.position += camera.forward * speed
        if held_keys['s']:
            camera.position -= camera.forward * speed
        if held_keys['a']:
            camera.position -= camera.right * speed
        if held_keys['d']:
            camera.position += camera.right * speed

        # Move up
        if held_keys['space']:
            camera.position += Vec3(0, speed * 20 * time.dt, 0)
        # Move down
        if held_keys['control']:
            camera.position -= Vec3(0, speed * 20 * time.dt, 0)

        camera.rotation_y += mouse.velocity[0] * 40
        camera.rotation_x -= mouse.velocity[1] * 40
        camera.rotation_x = clamp(camera.rotation_x, -90, 90)

    app.run()