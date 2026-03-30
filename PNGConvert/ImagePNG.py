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
def uniqueTile(targetTile, tiles, Weight,rotate):

    for i, tile in enumerate(tiles):
        if(rotate):
            rotations = [
                tile,                                  # 0°
                [tile[2], tile[0], tile[3], tile[1]], # 90°
                [tile[3], tile[2], tile[1], tile[0]], # 180°
                [tile[1], tile[3], tile[0], tile[2]]  # 270°
            ]
        else:
            rotations = [tile]

        # Checks if target tile is same as the rotated tile
        for j in range(len(rotations)):
            if rotations[j] == targetTile:
                #Already exists
                Weight[i] += 1
                return False
    return True


# Creates a list of all colors and ensures that only unique are added to list
def extract_tiles(img,rotate):
    # So we have the right amount of tiles based on sample image
    width, height = img.size

    # Gives direct access to the pixels in RGB form
    pixels = img.load()

    tiles = []
    rotations = []
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
            
            # Check if tile already exists and if not, add it
            if(uniqueTile(tile, tiles, Weights,rotate)):
                tiles.append(tile)
                Weights.append(1)
                #When we can rotate tiles

    #For the rotations
    if(rotate):
        #To rotate tiles and add weights accordingly
        rotateTile(tiles, Weights)

    return tiles, Weights

# Used to rotate tiles for all orientations
def rotateTile(tiles, Weights):
    tileLength = len(tiles)
    for i in range(tileLength):
        tile = tiles[i]
        x,y,z,t = 2,0,3,1
        temp = 0  

        #This is to check if all tiles are the same (Like all blue) by removing duplicates
        if len(set(tile)) == 1:
            continue

        for j in range(3):

            tile = [
                    tile[x],       # top-left
                    tile[y],       # top-right
                    tile[z],       # bottom-left
                    tile[t]        # bottom-right
                ]
                
            # This is our rotation
            temp = x
            x = z
            z = t
            t = y
            y = temp

            tiles.append(tile)
            Weights.append(Weights[i])

    return 

def imageLoad(path,rotate):
    img = load_image(path)
    tiles, Weights = extract_tiles(img,rotate)

    #print(f"Total tiles: {len(tiles)}\n")
    #for i in range(0,len(tiles)):
        #print(i," tile:", tiles[i], "\n")
        #print(i," Weight:", Weights[i], "\n")

    return tiles, Weights

