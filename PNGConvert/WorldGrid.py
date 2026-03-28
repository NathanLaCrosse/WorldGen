import numpy as np


def build_world_grid(cell_space, hash_to_tile, grid_n=2):
    """
    Build a 2D array representing the full world from the collapsed cell grid.

    Parameters:
        cell_space: 2D list of Cell objects (collapsed)
        hash_to_tile: dict mapping tile hashes to tile pixel arrays
        grid_n: size of each tile (number of small blocks per tile side)
    
    Returns:
        world_grid: 2D NumPy array of color indices
    """
    num_cells_row = len(cell_space)
    num_cells_col = len(cell_space[0])
    
    world_rows = num_cells_row * grid_n
    world_cols = num_cells_col * grid_n
    
    world_grid = np.zeros((world_rows, world_cols), dtype=int)
    
    for i, row in enumerate(cell_space):
        for j, cell in enumerate(row):
            tile = hash_to_tile[cell.state]  # should be a list of length grid_n*grid_n
            
            for dx in range(grid_n):
                for dz in range(grid_n):
                    world_row = i*grid_n + dz
                    world_col = j*grid_n + dx
                    idx = dz*grid_n + dx
                    world_grid[world_row, world_col] = tile[idx]
    
    return world_grid

