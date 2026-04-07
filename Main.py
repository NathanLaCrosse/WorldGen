from TileCollection import *
from collections import deque
import sys

from PNGConvert.ImagePNG import imageLoad
from PNGConvert.WaveFunc import tileToColor
from WFC import generate_fully_recursive
import matplotlib.pyplot as plt

sys.setrecursionlimit(10**6)

if __name__ == '__main__':
    gen_size = 64
    tile_size = 3

    tiles, weights = imageLoad(f"testim.png", False, tile_size=tile_size)
    hash_to_num, num_to_hash, tile_set, index_to_color, color_to_index, numColors = tileToColor(tiles, weights)
    PNG=True

    random_hash = 163840
    grid = reverse_hash(random_hash, numColors, tile_size)
    im = np.zeros((3,3,3), dtype=np.uint8)
    for i, j in np.ndindex((3,3)):
        color_tuple = index_to_color[grid[i,j]]

        im[i,j] = np.array(color_tuple)
    
    # grid, result = generate_fully_recursive(None, gen_size, tile_size, PNG, hash_to_num, num_to_hash, tile_set, numColors)

    # im = np.zeros((gen_size, gen_size, 3), dtype=np.uint8)
    # for i, j in np.ndindex((gen_size, gen_size)):
    #     color_tuple = index_to_color[grid[i,j]]

    #     im[i,j] = np.array(color_tuple)

    plt.imshow(im)
    plt.show()

    # tilemap = np.ones((11,10))

    # tilemap[0:2, :] = 3
    # tilemap[2:3, :7] = 3
    # tilemap[3:5, :5] = 3
    # tilemap[4, 5:7] = 3
    # tilemap[5, :3] = 3
    # tilemap[2, -1] = 3

    # tilemap[1:3, 1:3] = 2
    # tilemap[1, 3] = 2
    # tilemap[2,4] = 2

    # tilemap[7, 4:8] = 0
    # tilemap[8:10, 5:8] = 0

    # grid, result = generate_fully_recursive(tilemap, 4, 2)
    # grid, result = generate_fully_recursive(tilemap, 64, 2)
    # show_im(grid, get_colors())
    # print(result)
    # plt.show()