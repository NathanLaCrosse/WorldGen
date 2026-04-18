from TileCollection3D import *
from collections import deque

sys.setrecursionlimit(10**6)

directions = ['t','b','n','s','e','w']
dir_steps = [(-1,0,0),(1,0,0),(0,-1,0),(0,1,0),(0,0,1),(0,0,-1)]

def generate_3D_fully_recursive(gen_size, hash_to_num, num_to_hash, tile_set, num_colors, tile_size=2, stride=1):
    num_states = len(tile_set.keys())

    rev_adj = collect_reverse_adjacencies(hash_to_num, tile_set, num_colors, num_states, tile_size=tile_size, stride=stride)

    # Stuff for sampling from superpositions
    weights = np.array(list(tile_set.values()))
    args = np.arange(num_states)

    # Calculate dimensions of the cell space
    space_size = (gen_size - tile_size)//stride + 1

    # Initialize space
    cell_space = np.ones((space_size, space_size, space_size, num_states), dtype=bool)
    state_space = np.ones((space_size, space_size, space_size), dtype=np.int64) * -1

    # Intialize entropy grid - all the same since equal superposition
    entropy_grid = np.ones((space_size, space_size, space_size), dtype=np.uint64) * num_states

    # Call recursive method to solve for the entire space
    res = recursive_generation(cell_space, state_space, entropy_grid, args, weights, num_to_hash, hash_to_num, rev_adj, num_states, 0, space_size)

    return build_grid_from_cell_space(state_space, gen_size, space_size, tile_size, num_colors, stride), res

def recursive_generation(cell_space, state_space, entropy_grid, args, weights, num_to_hash, hash_to_num, rev_adj, 
                         num_states, collapse_count, space_size):
    
    if collapse_count == space_size**3:
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
        cell_space[depth, row, col] = np.zeros(num_states, dtype=bool)
        cell_space[depth, row, col, index] = True
        state_space[depth, row, col] = num_to_hash[index]
        entropy_grid[depth, row, col] = 100000

        # Propagate outward
        for i in range(len(directions)):
            step = dir_steps[i]

            # Skip over out-of-bounds nodes
            if (depth + step[0] < 0 or depth + step[0] > space_size-1 or row + step[1] < 0 or row + step[1] > space_size-1
                        or col + step[2] < 0 or col + step[2] > space_size-1):
                continue

            adj = build_allowed_superposition(cell_space, rev_adj, (depth, row, col), (depth+step[0], row+step[1], col+step[2]), directions[i])
            queue.append((depth+step[0], row+step[1], col+step[2], adj))

        # Perform a BFS until the grid is no longer getting updated
        is_valid = True
        while queue:
            qd, qr, qc, adj = queue.popleft()

            if qd < 0 or qd > space_size-1 or qr < 0 or qr > space_size-1 or qc < 0 or qc > space_size-1:
                continue  # Skip if out-of-bounds
            if state_space[qd, qr, qc] != -1:
                continue  # Skip if state is collapsed

            # update based on given adjacencies
            old_cell = cell_space[qd, qr, qc].copy()
            cell_space[qd,qr,qc] &= adj

            # Check if the old state is different than the new state
            if (old_cell ^ cell_space[qd, qr, qc]).any() > 0:
                if cell_space[qd, qr, qc].sum() == 0:
                    is_valid = False # No valid states left - leave loop
                    break

                # Update entropy grid
                old_entropy = entropy_grid[qd, qr, qc]
                entropy_grid[qd, qr, qc] = cell_space[qd, qr, qc].sum()
                if state_space[qd, qr, qc] != -1:
                    entropy_grid[qd, qr, qc] = 100000

                # Add to backprop queue
                modifications.append((qd, qr, qc, old_cell, old_entropy))

                # Propagate further 
                for i in range(len(directions)):
                    step = dir_steps[i]

                    # Skip over out-of-bounds nodes
                    if (qd + step[0] < 0 or qd + step[0] > space_size-1 or qr + step[1] < 0 or qr + step[1] > space_size-1
                                or qc + step[2] < 0 or qc + step[2] > space_size-1):
                        continue

                    adj = build_allowed_superposition(cell_space, rev_adj, (qd, qr, qc), (qd+step[0], qr+step[1], qc+step[2]), directions[i])
                    queue.append((qd+step[0], qr+step[1], qc+step[2], adj))


        # If we successfully propogate with no contradictions, recurse deeper.
        if is_valid:
            result = recursive_generation(cell_space, state_space, entropy_grid, args, weights, num_to_hash, hash_to_num, 
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

# Unchanged from original wave function collapse except for adjustments to parameters.
def build_allowed_superposition(cell_space, rev_adjacencies, source_pos, sink_pos, direction):
    c_ar = cell_space[source_pos] # This is a binary array

    # Index the adjacency matrix to find allowed states
    allowed_states = rev_adjacencies[direction][c_ar].any(axis=0) 
    
    return allowed_states & cell_space[sink_pos]

# Translate from state space into color index space
def build_grid_from_cell_space(state_space, gen_size, space_size, tile_size, numColors, stride):
    grid = np.zeros((gen_size,gen_size,gen_size), dtype=np.int64)

    for i in range(0, space_size):
        for j in range(0, space_size):
            for k in range(0, space_size):
                d = i*stride
                r = j*stride
                c = k*stride
                grid[d:d+tile_size, r:r+tile_size, c:c+tile_size] = reverse_3D_hash(state_space[i,j,k], numColors, tile_size)

    return grid




if __name__ == "__main__":
    grid_size = 8
    tile_size = 2
    stride = 1

    tilemap, idx_to_color, color_to_idx = construct_3D_tilemap(8,8,8,png_folder="Generation_3D/images_3D/richgrass", png_names="richgrass")

    tiles, weights = collect_3D_tiles(tilemap, 2)

    num_colors = len(idx_to_color.keys())
    num_states = len(tiles)

    hash_to_num, num_to_hash, tile_set = build_3D_tilemap_hashes(tiles, weights, num_colors)

    space, res = generate_3D_fully_recursive(grid_size, hash_to_num, num_to_hash, tile_set, num_colors, tile_size, stride)

    space = space[::-1]

    # create_voxel_mesh(tilemap.tolist(), idx_to_color)
    image = create_voxel_mesh(space.tolist(), idx_to_color)
    # print(res)

    chunks = 1
    app = Ursina()

    # Sets up the Ursina enviornment

    # Lighting
    DirectionalLight().look_at(Vec3(1, -1, -1))
    AmbientLight(color=color.rgba(100, 100, 100, 0.5))

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