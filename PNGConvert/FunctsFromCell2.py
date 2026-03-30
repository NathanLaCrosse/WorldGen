"""----------------------------------------------------------------

THIS IS TEMPORARY, mainly needed to adjust a few things so that the 
cell could handle some inputs as well as a few other dependacies. 

Will remove/change once Cell2 is modified

----------------------------------------------------------------"""

import numpy as np
import matplotlib.pyplot as plt

# Bad intersection code for temporary work...
def intersect(a1, a2):
    dest = []

    for a in a1:
        if a in a2:
            dest.append(a)

    return dest

directions = ['t', 'tr', 'tl', 'r', 'l', 'b', 'br', 'bl']
dir_steps = [(-1, 0), (-1, 1), (-1, -1), (0, 1), (0, -1), (1, 0), (1, 1), (1, -1)]
adjacencies = {}

class Cell:
    def __init__(self, row=0, col=0, tile_hashes=None, hash_to_weight=None, adjacencies=None):
        self.row = row
        self.col = col
        self.superposition = tile_hashes.copy() if tile_hashes is not None else []
        self.weights = [hash_to_weight[h] for h in self.superposition] if hash_to_weight else []
        self.state = -1

        self.adjacencies = adjacencies  # Save reference for collapse()

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
            propagation_queue.append([(self.row + step[0], self.col + step[1]), self.adjacencies[(self.state, directions[i])]])
    
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
        


def is_all_collapsed(cell_space,grid_size):
    for i in range(grid_size-1):
        for j in range(grid_size-1):
            if cell_space[i][j].state == -1:
                return False
    
    return True


def collapse_grid(cell_space, row, col, grid_size):
    cell = cell_space[row][col]

    if is_all_collapsed(cell_space,grid_size):
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
            
            result = collapse_grid(cell_space, new_row, new_col, grid_size)

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