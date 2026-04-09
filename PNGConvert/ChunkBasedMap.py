import sys
import os

# Add parent directory to Python path
from PNGConvert.MeshGrid import startMesh
from PNGConvert.SampleDisplay import sample_mesh
from PNGConvert.WaveFunc import tileToColor
from WFC import generate_fully_recursive_chunk
import numpy as np
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def chunkBasedMap(tiles, weights, grid_size, tile_size, numberOfChunks):
    hash_to_num, num_to_hash, tile_set, index_to_color, color_to_index, numColors = tileToColor(tiles, weights)
    
    sample_mesh(tiles, color_to_index, index_to_color, tile_size)

    final_size = numberOfChunks * (grid_size - 1) + 1

    max_attempts_per_chunk = 1
    max_attempts_full_map = 5

    for map_attempt in range(max_attempts_full_map):

        # Reset per attempt
        full_grid = np.zeros((final_size, final_size), dtype=int)

        chunk_edges = [[{} for _ in range(numberOfChunks)] for _ in range(numberOfChunks)]
        chunk_grids = [[None for _ in range(numberOfChunks)] for _ in range(numberOfChunks)]
        full_map_success = True

        # -----------------------------
        # GENERATE CHUNKS
        # -----------------------------
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

                # if not success:
                #     full_map_success = False
                #     break
                if not success:
                    # Leave chunk as blank (zeros)
                    chunk_grids[i][j] = np.zeros((grid_size, grid_size), dtype=int)
                    chunk_edges[i][j] = {}
                    continue

                chunk_grids[i][j] = grid
                chunk_edges[i][j] = {
                    "top": grid[0, :].copy(),
                    "bottom": grid[-1, :].copy(),
                    "left": grid[:, 0].copy(),
                    "right": grid[:, -1].copy()
                }

            if not full_map_success:
                break

        # If failed, retry whole map
        # if not full_map_success:
        #     continue

        # -----------------------------
        # BUILD FULL GRID
        # -----------------------------
        y_cursor = 0
        for i in range(numberOfChunks):
            x_cursor = 0
            for j in range(numberOfChunks):
                chunk = chunk_grids[i][j]

                if i > 0:
                    chunk = chunk[1:, :]
                if j > 0:
                    chunk = chunk[:, 1:]

                h, w = chunk.shape

                full_grid[y_cursor:y_cursor+h, x_cursor:x_cursor+w] = chunk

                x_cursor += w  
            y_cursor += h   

        startMesh(full_grid, index_to_color)
        return  

    # Only reached if ALL attempts fail
    raise RuntimeError(
        f"Unable to generate a complete {numberOfChunks}x{numberOfChunks} chunk map after {max_attempts_full_map} attempts"
    )