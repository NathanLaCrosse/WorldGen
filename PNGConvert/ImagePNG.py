"""----------------------------------------------------------------

Within this function, we take in a sample PNG image, and 
subscript it into 4x4 sample images. 
 
It then sends out a tile element with the RGB values
 
Dylan Dudley - 03/27/2026

----------------------------------------------------------------"""

from PIL import Image


# This starts by converting the image into RGB Format
def load_image(path):
    img = Image.open(path).convert("RGB")
    return img

# Checks if the tile already exists and will update the weight accordingly
def uniqueTile(targetTile, tiles, Weight):
    for i, tile in enumerate(tiles):
        if tile == targetTile:
            #Already exists
            Weight[i] += 1
            return False
    return True


def extract_tiles(img):
    # So we have the right amount of tiles based on sample image
    width, height = img.size

    # Gives direct access to the pixels in RGB form
    pixels = img.load()

    tiles = []
    Weights = []
    # now, we need to create a scanner that will go through the whole image and check each
    # section of 2x2 tiles. 
    for y in range(height - 1):
        for x in range(width - 1):

            tile = [
                    pixels[x, y],         # top-left
                    pixels[x+1, y],       # top-right
                    pixels[x, y+1],       # bottom-left
                    pixels[x+1, y+1]      # bottom-right
                ]
            
            # Check if tile already exists
            if(uniqueTile(tile, tiles, Weights)):
                tiles.append(tile)
                Weights.append(1)

    return tiles, Weights


def imageLoad(path):
    img = load_image(path)
    tiles, Weights = extract_tiles(img)

    print(f"Total tiles: {len(tiles)}\n")
    for i in range(0,len(tiles)):
        print(i," tile:", tiles[i], "\n")
        print(i," Weight:", Weights[i], "\n")

    return tiles, Weights

