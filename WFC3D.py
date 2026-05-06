from TileCollection3D import *
from collections import deque
import pickle

sys.setrecursionlimit(10**6)

directions = ['t','b','n','s','e','w']
dir_steps = [(-1,0,0),(1,0,0),(0,-1,0),(0,1,0),(0,0,1),(0,0,-1)]

def generate_3D_chunks(gen_size, chunk_size, tile_to_dex, dex_to_tile, weights, num_colors, tile_size=2, stride=1, seeding_presets=None, rev_adj=None, attemps_per_chunk=3, seed_bottom=False):
    if rev_adj is None:
        rev_adj = collect_reverse_adjacencies(dex_to_tile, num_states, tile_size=tile_size, stride=stride)

        print("Adjacencies Built!")

    # Calculate dimensions of the cell space inside a chunk
    space_size = ((chunk_size[0] - tile_size)//stride + 1, (chunk_size[1] - tile_size)//stride + 1, (chunk_size[2] - tile_size)//stride + 1)
    
    # intialize full grid in state space, which will later be converted into voxels
    full_state_space = -1 * np.ones((gen_size[0]*space_size[0], gen_size[1]*space_size[1], gen_size[2]*space_size[2]), dtype=np.int64)
    # full_state_space = np.zeros((gen_size[0]*space_size[0], gen_size[1]*space_size[1], gen_size[2]*space_size[2]), dtype=np.uint8)

    for i in range(gen_size[0]):
        for j in range(gen_size[1]):
            for k in range(gen_size[2]):
                presets = []
                boundary_conditions = []

                # If this is the first chunk, use seeding presets
                if i == j == k == 0:
                    presets = seeding_presets
                elif i == 0 and seed_bottom:
                    presets = seeding_presets

                # If there is a generated chunk to the left, add its boundary conditions
                # Working in column space
                if k > 0:
                    for m,n in np.ndindex((space_size[0],space_size[1])):
                        boundary_conditions.append(((m,n,0), full_state_space[i*space_size[0]+m, j*space_size[1]+n, k*space_size[2]-1], 'e'))
                
                # If there is a generated chunk to the south, add its boundary conditions
                # Working in row space
                if j > 0:
                    for m,n in np.ndindex((space_size[0], space_size[2])):
                        boundary_conditions.append(((m,0,n), full_state_space[i*space_size[0]+m, j*space_size[1]-1, k*space_size[2]+n], 's'))

                # If there is a generated chunk below, add its boundary conditions
                # Working in depth space
                if i > 0:
                    for m,n in np.ndindex((space_size[1], space_size[2])):
                        boundary_conditions.append(((0,m,n), full_state_space[i*space_size[0]-1, j*space_size[1]+m, k*space_size[2]+n], 'b'))
                
                # Attempt to generate a chunk
                for l in range(attemps_per_chunk):
                    state_space, res = generate_3D_fully_recursive(chunk_size, tile_to_dex, dex_to_tile, weights, num_colors, tile_size, stride, presets, 
                                        rev_adj=rev_adj, return_state_space=True, boundary_conditions=boundary_conditions, prints=False)

                    # If successful, leave
                    if res:
                        break
                    elif l == attemps_per_chunk-1:
                        print("Critical Error! At", i, j, k)
                        return np.zeros((gen_size[0]*chunk_size[0],gen_size[1]*chunk_size[1],gen_size[2]*chunk_size[2])), False
                
                # Now that we have our chunk, we can add it to the global state space
                full_state_space[i*space_size[0]:(i+1)*space_size[0], j*space_size[1]:(j+1)*space_size[1], 
                                 k*space_size[2]:(k+1)*space_size[2]] = state_space
                
                # full_state_space = state_space
                
                print("Completed Chunk", i, j, k)

    # After this point, all chunks have been loaded, so we return the space
    voxel_grid_size = (gen_size[0]*chunk_size[0], gen_size[1]*chunk_size[1], gen_size[2]*chunk_size[2])
    space = build_grid_from_cell_space(full_state_space, voxel_grid_size, full_state_space.shape, tile_size, num_colors, stride, dex_to_tile)
    return space, True


# Gensize (int) -> tuple of ints
def generate_3D_fully_recursive(gen_size, tile_to_dex, dex_to_tile, weights, num_colors, tile_size=2, stride=1, presets=None, rev_adj=None, return_state_space=False, boundary_conditions=None, prints=True):
    assert (gen_size[0] - tile_size) % stride == 0 and (gen_size[1] - tile_size) % stride == 0 and (gen_size[2] - tile_size) % stride == 0, "Incompatible Tile/Stride/Grid_Size Combination"
    
    num_states = len(dex_to_tile.keys())
    
    if rev_adj is None:
        rev_adj = collect_reverse_adjacencies(dex_to_tile, num_states, tile_size=tile_size, stride=stride)

        if prints: print("Adjacencies Built!")

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

    if boundary_conditions is not None:
        if prints: print("Applying Boundary Constraints...")

        q = deque()
        m = deque()

        res = apply_boundary_constraints(cell_space, state_space, entropy_grid, q, m, rev_adj, space_size, num_states, boundary_conditions)

    collapsed = 0
    one_done = True
    if presets is not None:
        for pos, state_dex in presets:
            # If presets are passed in, initialized grid with some states
            q = deque()
            m = deque()

            enqueue(q, pos, state_dex, cell_space, state_space, entropy_grid, rev_adj, space_size, num_states)
            
            # Propagate changes
            propagate_BFS(q, m, cell_space, state_space, entropy_grid, rev_adj, space_size, num_states)

            if one_done:
                if prints: print("One-Preset Propagated!")
                one_done = False
        
        collapsed = len(presets)
        if prints: print("Preset-Tiles Finished!")
    
    if prints: print("Starting Generation...")

    # Call recursive method to solve for the entire space
    res = recursive_generation(cell_space, state_space, entropy_grid, args, weights, dex_to_tile, tile_to_dex, rev_adj, num_states, collapsed, space_size)

    if not return_state_space:
        space = np.zeros(gen_size)

        if res:
            space = build_grid_from_cell_space(state_space, gen_size, space_size, tile_size, num_colors, stride, dex_to_tile)

        return space, res
    else:
        return state_space, res
    

def apply_boundary_constraints(cell_space, state_space, entropy_grid, queue, modifications, rev_adj, space_size, 
                               num_states, boundary_conditions):
    # Enforce boundary conditions between chunks
    for (d,r,c), neighbor_state, direction in boundary_conditions:
        if state_space[d,r,c] != -1:
            continue # Already collapsed

        old_cell = cell_space[d, r, c].copy()
        old_entropy = entropy_grid[d, r, c]

        # Apply constraint from known neighbor
        allowed = rev_adj[direction][neighbor_state]
        cell_space[d, r, c] &= allowed
        entropy_grid[d, r, c] = cell_space[d, r, c].sum()

        if entropy_grid[d, r, c].sum() == 0:
            return False # Reached invalid state

        # Track modification for backtracking
        modifications.append((d, r, c, old_cell, old_entropy))

        # Add changes to propagation queue
        enqueue(queue, (d, r, c), -1, cell_space, state_space, entropy_grid, rev_adj, space_size, num_states)
    
    # Once boundary conditions have been enqueued, perform BFS
    return propagate_BFS(queue, modifications, cell_space, state_space, entropy_grid, rev_adj, space_size, num_states)

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
    current_superposition = cell_space[depth, row, col].copy()

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
        current_superposition = cell_space[depth, row, col].copy()
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

        # adj = build_allowed_superposition(cell_space, rev_adj, pos, neighbor_pos, directions[i])
        # queue.append((neighbor_pos[0], neighbor_pos[1], neighbor_pos[2], adj))
        queue.append((neighbor_pos, pos, directions[i]))

def propagate_BFS(queue, modifications, cell_space, state_space, entropy_grid, rev_adj, space_size, num_states):
    # Loop until queue is empty or we finish early
    while queue:
        # qd, qr, qc, adj = queue.popleft()
        neighbor_pos, source_pos, direction = queue.popleft()
        qd, qr, qc = neighbor_pos

        if qd < 0 or qd > space_size[0]-1 or qr < 0 or qr > space_size[1]-1 or qc < 0 or qc > space_size[2]-1:
            continue  # Skip if out-of-bounds

        adj = build_allowed_superposition(cell_space, rev_adj, source_pos, neighbor_pos, direction)

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

def gather_tilemap_data(png_depth, png_rows, png_cols, png_folder, png_names, tile_size=2, stride=1, rotate=False, save_dir=None, load_dir=None, filename=None):
    if load_dir is None:
        tilemap, idx_to_color, color_to_idx = construct_3D_tilemap(png_depth,png_rows,png_cols,png_folder=png_folder, png_names=png_names)

        tiles, weights = collect_3D_tiles(tilemap, tile_size, rotation=rotate)
        print("Tiles Collected!")
        
        num_colors = len(idx_to_color.keys())
        num_states = len(tiles)

        tile_to_dex, dex_to_tile = build_3D_tile_hashes(tiles)
        print("Hash Tables Completed!")

        print("Num States:", num_states)

        rev_adj = collect_reverse_adjacencies(dex_to_tile, num_states, tile_size=tile_size, stride=stride)
        print("Adjacencies Built!")

        if save_dir is not None:
            with open(f"{save_dir}/{filename}.pkl", "wb") as file:
                pickle.dump([tilemap, idx_to_color, color_to_idx, tiles, weights, tile_to_dex, dex_to_tile, rev_adj], file)
            print("Data Saved!")
        
        return tilemap, idx_to_color, color_to_idx, tiles, weights, tile_to_dex, dex_to_tile, rev_adj, num_colors, num_states
    else:
        with open(f"{load_dir}/{filename}.pkl", "rb") as file:
            tilemap, idx_to_color, color_to_idx, tiles, weights, tile_to_dex, dex_to_tile, rev_adj = pickle.load(file)
        
        num_colors = len(idx_to_color.keys())
        num_states = len(tiles)

        print("Data Loaded!")

        return tilemap, idx_to_color, color_to_idx, tiles, weights, tile_to_dex, dex_to_tile, rev_adj, num_colors, num_states
    
def generate_world(tile_data_tuple, tile_size=2, stride=1, gen_size=(2,2,2), chunk_size=(8,8,8), presets=None, save_dir=None, load_dir=None, filename=None):
    # Grab all tilemap data from the tuple 
    tilemap, idx_to_color, color_to_idx, tiles, weights, tile_to_dex, dex_to_tile, rev_adj, num_colors, num_states = tile_data_tuple

    if load_dir is None:
        while True:
            space, res = generate_3D_chunks(gen_size, chunk_size, tile_to_dex, dex_to_tile, weights, num_colors, 
                tile_size, stride, seeding_presets=presets, rev_adj=rev_adj, attemps_per_chunk=3, seed_bottom=False)
            
            if res:
                break
            else:
                print("Invalid Point Reached, Restarting Generation")
                
        if save_dir is not None:
            with open(f"{save_dir}/{filename}.pkl", "wb") as file:
                pickle.dump(space, file)
        
        return space
    else:
        with open(f"{load_dir}/{filename}.pkl", "rb") as file:
            space = pickle.load(file)
        
        return space

if __name__ == "__main__":
    # Generation settings

    # Loading settings are as follows:
    #          load_adj, load_tilemap, rotate, folder_name, file_prefix, depth, rows, cols, save_name
    # settings = (False, True, True, "AnotherMountain", "amount", 14, 32, 32, "diaorama2")
    # settings = (False, True, True, "AnotherMountain", "amount", 14, 32, 32, "diaorama1")
    # settings = (False, True, True, "SmolMountain", "mountain", 19, 32, 32, "diaorama3") # Fastest running example
    # settings = (False, True, True, "OceanMountain3d", "omount", 9, 48, 48, "diaorama4")
    # settings = (False, False, True, "OceanMountain3d", "omount", 9, 48, 48, "diaorama5")
    # settings = (False, True, True, "AnotherOceanMountain", "omount", 9, 32, 32, "diaorama6")
    # settings = (False, True, True, "AnotherOceanMountain", "omount", 9, 32, 32, "diaorama7") # Nice mini diaorama
    # settings = (False, True, True, "AnotherOceanMountain", "omount", 9, 32, 32, "diaorama8") # Another nice small one
    # settings = (False, False, True, "AnotherOceanMountain", "omount", 9, 32, 32, "diaorama9")

    # Settings are as follows:
    #            load_tiledat, load_world, tiledat_save_name, world_save_name, tileset_folder_name, tileset_prefix, tileset_depth, row, cols, rotate
    # settings =   (True,       True,       "oceandat",         "diorama9",      "AnotherOceanMountain", "omount",     9,             32,  32,   True)
    # settings =   (False,      True,        None,              "diaorama7",      "AnotherOceanMountain", "omount",     9,             32,  32,   True)
    # settings =   (False,      True,        None,              "diaorama3",      "SmolMountain",         "mountain",   19,            32,  32,   True)
    settings =   (True,       False,       "oceandat",         "diaorama10",      "AnotherOceanMountain", "omount",     9,             32,  32,   True)
    
    gen_size = (2,4,4)
    chunk_size = (8,8,8)
    tile_size = 2
    stride = 1

    load_tiledat, load_world, tiledat_save_name, world_save_name, tileset_folder_name, tileset_prefix, png_depth, png_rows, png_cols, r = settings

    tileset_folder_name = "Generation_3D/images_3D/" + tileset_folder_name

    presets = []
    space_size = ((chunk_size[0] - tile_size)//stride + 1, (chunk_size[1] - tile_size)//stride + 1, (chunk_size[2] - tile_size)//stride + 1)

    # Presets are specified here - 
    presets.append(((0,0,0),0))

    if load_tiledat:
        data_tuple = gather_tilemap_data(png_depth, png_rows, png_cols, tileset_folder_name, tileset_prefix, tile_size, stride, r, None, "Saved_Data", tiledat_save_name)
    else:
        if tiledat_save_name is not None:
            tiledat_save_dir = "Saved_Data"
        else:
            tiledat_save_dir = None

        data_tuple = gather_tilemap_data(png_depth, png_rows, png_cols, tileset_folder_name, tileset_prefix, tile_size, stride, r, tiledat_save_dir, None, tiledat_save_name)

    tilemap, idx_to_color, color_to_idx, tiles, weights, tile_to_dex, dex_to_tile, rev_adj, num_colors, num_states = data_tuple

    if load_world:
        space = generate_world(data_tuple, tile_size, stride, gen_size, chunk_size, presets, None, "Saved_Data", world_save_name)
    else:
        if world_save_name is not None:
            world_save_dir = "Saved_Data"
        else:
            world_save_dir = None
        
        space = generate_world(data_tuple, tile_size, stride, gen_size, chunk_size, presets, world_save_dir, None, world_save_name)

    print("Starting Mesh!")
    create_voxel_mesh(space.tolist(), idx_to_color)
    print("Ending Mesh!")

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