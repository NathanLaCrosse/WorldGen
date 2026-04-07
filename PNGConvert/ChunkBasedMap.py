


import sys
import os

# Add parent directory to Python path
from MeshGrid import startMesh
from WaveFunc import tileToColor
from WFC import generate_fully_recursive_chunk
import numpy as np
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def chunkBasedMap(tiles, weights, grid_size, tile_size, numberOfChunks):
    # Get the tile to color mappings
    hash_to_num, num_to_hash, tile_set, index_to_color, color_to_index, numColors = tileToColor(tiles, weights)

    max_attempts_per_chunk = 10
    max_attempts_full_map = 5

    for map_attempt in range(max_attempts_full_map):
        chunk_edges = [[{} for _ in range(numberOfChunks)] for _ in range(numberOfChunks)]
        chunk_grids = [[None for _ in range(numberOfChunks)] for _ in range(numberOfChunks)]
        full_map_success = True

        for i in range(numberOfChunks):
            for j in range(numberOfChunks):
                constraints = {}

                if i > 0 and "bottom" in chunk_edges[i-1][j]:
                    constraints["top"] = chunk_edges[i-1][j]["bottom"]

                if j > 0 and "right" in chunk_edges[i][j-1]:
                    constraints["left"] = chunk_edges[i][j-1]["right"]

                success = False
                for attempt in range(max_attempts_per_chunk):
                    grid, success = generate_fully_recursive_chunk(
                        None,
                        grid_size,
                        tile_size,
                        True,
                        hash_to_num,
                        num_to_hash,
                        tile_set,
                        numColors,
                        constraints
                    )
                    if success:
                        break

                if not success:
                    full_map_success = False
                    break

                chunk_grids[i][j] = grid
                chunk_edges[i][j] = {
                    "top": grid[0, :].copy(),
                    "bottom": grid[-1, :].copy(),
                    "left": grid[:, 0].copy(),
                    "right": grid[:, -1].copy()
                }

            if not full_map_success:
                break

        if full_map_success:
            for i in range(numberOfChunks):
                for j in range(numberOfChunks):
                    x_offset = j * grid_size
                    y_offset = i * grid_size
                    startMesh(chunk_grids[i][j], index_to_color, x_offset, y_offset)
            return

    raise RuntimeError(f"Unable to generate a complete {numberOfChunks}x{numberOfChunks} chunk map after {max_attempts_full_map} attempts") 