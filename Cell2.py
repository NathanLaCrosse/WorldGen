import numpy as np
import matplotlib.pyplot as plt

# First, let's define four colors to work with (which will be stored numerically as an index)
colors = [0, 10, 60, 90]

# Method for displaying an image after converting color indices to colors.
def show_im(im, ax=None):
    temp_im = np.array(im, dtype=np.uint8)
    for i in range(len(colors)):
        temp_im[temp_im == i] = colors[i]
    if ax == None:
        plt.imshow(temp_im, cmap='terrain', vmin=0, vmax=255)
    else:
        ax.imshow(temp_im, cmap='terrain', vmin=0, vmax=255)

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

# Collect tiles
tilemap_size = 10
n = 2

tiles = np.zeros((tilemap_size - n + 1, tilemap_size - n + 1, n, n))

for i in range(tilemap_size - n + 1):
    for j in range(tilemap_size - n + 1):
        tiles[i, j] = tilemap[i:i+n, j:j+n]

def hash_tile(tile):
    return int(tile[0,0] + 4 * tile[0, 1] + 16 * tile[1, 0] + 64 * tile[1,1])

def reverse_hash(num):
    tile = np.zeros(4)
    n = num
    for i in range(len(tile)):
        tile[i] = n % 4
        n = n // 4
    return tile.reshape((2,2))
    

# Gather unique tiles and record frequency (frequency will be weight the superposition collapse)
tile_set = {}
l = tilemap_size - n + 1

for i in range(l):
    for j in range(l):
        val = hash_tile(tiles[i,j])

        if val not in tile_set.keys():
            tile_set[val] = 1
        else:
            tile_set[val] += 1

def compare_hashes(h1, h2, t1_border, t2_border):
    assert len(t1_border) == len(t2_border), "Border Sizes Must Match"

    for i in range(len(t1_border)):
        if (h1 // 4**t1_border[i]) % 4 != (h2 // 4**t2_border[i]) % 4:
            return False
    return True

# Now let's make adjacency rules!
# Each adjacency is designated by a (tile hash, direction) key
# So (850, 'tr') stores pieces that can connect with the top right of 850
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
        if t == target:
            continue # Avoid checking adjacencies against yourself

        for d in range(len(directions)):
            if compare_hashes(t, target, t1_comparisons[d], t2_comparisons[d]) and target not in adjacencies[(t, directions[d])]:
                adjacencies[(t, directions[d])].append(target)

# max_tile_weight = sum(tile_set.values())
# tile_weights = np.array(tile_set.values())

# Bad intersection code for temporary work...
def intersect(a1, a2):
    dest = []

    for a in a1:
        if a in a2:
            dest.append(a)

    return dest

directions = ['t', 'tr', 'tl', 'r', 'l', 'b', 'br', 'bl']
dir_steps = [(-1, 0), (-1, 1), (-1, -1), (0, 1), (0, -1), (1, 0), (1, 1), (1, -1)]

class Cell:

    def __init__(self, row=0, col=0):
        self.superposition = list(tile_set.keys())
        self.weights = list(tile_set.values())
        self.state = -1

        self.row = row
        self.col = col

        # Data for backtracking
        self.previous_superpositions = []
        self.previous_weights = []
    
    def collapse(self, propagation_queue):
        total_weight = sum(self.weights)

        choice = np.random.choice(int(len(self.superposition)), p=np.array(self.weights)/total_weight)

        self.state = self.superposition[choice]

        for i in range(len(directions)):
            step = dir_steps[i]

            # To the propagation queue, we add the cell's location and then its allowed states based on
            # what the cell collapsed to.
            propagation_queue.append([(self.row + step[0], self.col + step[1]), adjacencies[(self.state, directions[i])]])
    
    def reverse_collapse(self, propagation_queue):
        invalid_dex = -1

        # Save old states for backtracking
        # self.previous_superpositions.append((self.superposition.copy(), 'c')) # The string 'c' denotes a narrowing via collapse
        # self.previous_weights.append(self.weights.copy())

        # Superposition was unchanged by the collapsing process, we just need to remove the incorrect state
        for i in range(len(self.superposition)):
            if self.superposition[i] == self.state:
                invalid_dex = i
                break
        
        self.superposition.remove(self.superposition[invalid_dex])
        self.weights.remove(self.weights[invalid_dex])

        # Add to the propogation queue cells we need to unnarrow
        for i in range(len(directions)):
            step = dir_steps[i]

            propagation_queue.append((self.row + step[0], self.col + step[1]))
        
        # Revert state back into uncertainty
        self.state = -1
    
    def narrow(self, possibilities):
        if self.state != -1:
            # We have already collapsed the superposition...
            return

        # Save old states for backtracking
        self.previous_superpositions.append((self.superposition.copy(), 'n')) # The string 'n' denotes a narrowing
        self.previous_weights.append(self.weights.copy())

        new_superposition = intersect(self.superposition, possibilities)
        new_weights = []

        # Intersect weights as well as states
        for i in range(len(new_superposition)):
            for j in range(len(self.superposition)):
                if new_superposition[i] == self.superposition[j]:
                    new_weights.append(self.weights[j])

        self.superposition = new_superposition
        self.weights = new_weights
    
    def reverse_narrow(self):
        if self.state != -1 or len(self.previous_superpositions) == 0:
            # We have already collapsed.
            return

        # For part of the backtracking algorithm. Revert to a previous superposition.
        self.superposition = self.previous_superpositions[-1][0]
        self.weights = self.previous_weights[-1]

        # Slice the reverted changes out of the start
        self.previous_superpositions = self.previous_superpositions[:-1]
        self.previous_weights = self.previous_weights[:-1]
    
    def entropy(self):
        if self.state != -1:
            return 100000
        else:
            return len(self.superposition)
        

print('hi')
# Let's attempt generation of a small grid\
grid_size = 12


cell_space = [ [Cell(i, j) for j in range (grid_size-1)] for i in range(grid_size-1)]
entropy_grid = np.zeros((grid_size-1,grid_size-1))

update_tracker = []

for i in range(grid_size-1):
    for j in range(grid_size-1):
        entropy_grid[i,j] = cell_space[i][j].entropy()

def is_all_collapsed(cell_space):
    for i in range(grid_size-1):
        for j in range(grid_size-1):
            if cell_space[i][j].state == -1:
                return False
    
    return True

def collapse_grid(cell_space, row, col):
    cell = cell_space[row][col]

    if is_all_collapsed(cell_space):
        return True
    elif len(cell.superposition) == 0:
        return False
    
    original_superposition = cell.superposition.copy()
    original_weights = cell.weights.copy()

    # Try to collapse in every way
    while len(cell.superposition) > 0:
        queue = []
        cell.collapse(queue)

        is_valid = True
        for q in queue:
            pos = q[0]

            if pos[0] < 0 or pos[0] > grid_size-2 or pos[1] < 0 or pos[1] > grid_size-2:
                continue  # Skip if out-of-bounds

            possibilities = q[1]
            cell_space[pos[0]][pos[1]].narrow(possibilities)

            if len(cell_space[pos[0]][pos[1]].superposition) == 0:
                is_valid = False
        
        # If valid, recurse deeper.
        if is_valid:
            entropy_grid = np.zeros((grid_size-1,grid_size-1))

            for i in range(grid_size-1):
                for j in range(grid_size-1):
                    entropy_grid[i,j] = cell_space[i][j].entropy()

            # Choose the cell with minimum entropy
            new_row, new_col = np.unravel_index(np.argmin(entropy_grid), entropy_grid.shape)
            
            result = collapse_grid(cell_space, new_row, new_col)

            if result:
                return True
            # If false, continue keep looping

        # If invalid, reverse everything and continue (revert collapse)
        queue = []
        cell.reverse_collapse(queue) # Note - removes current state from superposition

        for q in queue:
            pos = q

            if pos[0] < 0 or pos[0] > grid_size-2 or pos[1] < 0 or pos[1] > grid_size-2:
                continue  # Skip if out-of-bounds

            cell_space[pos[0]][pos[1]].reverse_narrow()
    
    # There are no possible states that we choose - all end up with an invalid grid
    # We need to backtrack, so revert this state back to where it was.
    cell.superposition = original_superposition
    cell.weights = original_weights
    cell.state = -1

    return False





# Time to build the grid with the cell states

cell_space = [ [Cell(i, j) for j in range (grid_size-1)] for i in range(grid_size-1)]
collapse_grid(cell_space, 0, 0)

grid = np.zeros((grid_size,grid_size))

for i in range(grid_size//2):
    for j in range(grid_size//2):
        grid[i*2:(i+1)*2, j*2:(j+1)*2] = reverse_hash(cell_space[2*i][2*j].state)
show_im(grid)

# fig, ax = plt.subplots(5, 5)
# for t in range(5):
#     for v in range(5):
#         cell_space = [ [Cell(i, j) for j in range (grid_size-1)] for i in range(grid_size-1)]
#         collapse_grid(cell_space, 0, 0)

#         grid = np.zeros((grid_size,grid_size))

#         for i in range(grid_size//2):
#             for j in range(grid_size//2):
#                 grid[i*2:(i+1)*2, j*2:(j+1)*2] = reverse_hash(cell_space[2*i][2*j].state)
#         show_im(grid, ax[t,v])
#         ax[t,v].axis('off')

plt.show()