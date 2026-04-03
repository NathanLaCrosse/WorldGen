import numpy as np
from TileCollection import *
from collections import deque

directions = ['t', 'tr', 'tl', 'r', 'l', 'b', 'br', 'bl']
dir_steps = [(-1, 0), (-1, 1), (-1, -1), (0, 1), (0, -1), (1, 0), (1, 1), (1, -1)]

class Cell:

    def __init__(self, tileset, hash_to_index, index_to_hash, adjacencies, row=0, col=0):
        self.superposition = 2**len(tileset.keys()) - 1 # len(tileset.keys()) 1's
        self.weights = np.array(list(tileset.values()))[::-1] # Read in reverse order due to least significant bit being index 0
        self.state = -1

        self.row = row
        self.col = col

        self.num_states = len(tileset.keys())
        self.args = np.arange(self.num_states)
        self.tileset = tileset
        self.adjacencies = adjacencies
        self.hash_to_index = hash_to_index
        self.index_to_hash = index_to_hash

        # Data for backtracking
        self.previous_superpositions = deque()
    
    def collapse(self, propagation_queue):
        p = np.zeros(self.num_states)

        # Perform component-wise addition between weights array and superposition arrays
        # note that the superposition "array" is an integer, so we iterate through the bits
        c = self.superposition
        for i in range(self.num_states):
            p[i] = (1 & c) * self.weights[i]
            c = c >> 1
        p = p / p.sum()

        # Choose a random state index
        index = np.random.choice(self.args, p=p/p.sum())
        self.state = self.index_to_hash[index]

        for i in range(len(directions)):
            step = dir_steps[i]

            # To the propagation queue, we add the cell's location and then its allowed states based on
            # what the cell collapsed to.
            propagation_queue.append((self.row + step[0], self.col + step[1]))
    
    def gather_neighbors(self, queue):
        for i in range(len(directions)):
            step = dir_steps[i]

            # To the propagation queue, we add the cell's location and then its allowed states based on
            # what the cell collapsed to.
            queue.append((self.row + step[0], self.col + step[1]))
    
    def reverse_collapse(self, propagation_queue):
        # We want to disclude our current state from the superposition.
        # To do this, we simply obtain the bit flag and XOR it with our superposition
        self.superposition &= ~(2**self.hash_to_index[self.state])

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
        self.previous_superpositions.append(self.superposition)

        # Perform bitwise AND to cancel out illegal possibilities
        new_superposition = self.superposition & possibilities

        self.superposition = new_superposition

    def advanced_narrow(self, other_superposition, direction):
        # Narrow superposition based on another tile's superposition.
        combined_possibilities = 0

        c = other_superposition
        for i in range(self.num_states):
            index_present = c & 1
            
            if index_present:
                combined_possibilities |= self.adjacencies[(self.index_to_hash[i], direction)]
            c = c >> 1
        
        # Perform bitwise AND to cancel out illegal possibilities
        return combined_possibilities
    
    def reverse_narrow(self):
        if self.state != -1 or len(self.previous_superpositions) == 0:
            # We have already collapsed.
            return

        # Pop off the stack since we reverted.
        self.superposition = self.previous_superpositions[-1]
        self.previous_superpositions.pop()
    
    def entropy(self):
        if self.state != -1:
            return 100000
        else:
            s = 0
            c = self.superposition
            for i in range(self.num_states):
                s += 1 & c
                c = c >> 1
            
            return s
            # return len(self.superposition)