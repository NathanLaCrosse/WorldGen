"""----------------------------------------------------------------

Within this function, we take in a sample PNG image, and 
subscript it into 2x2 sample blocks. 
 
It then sends out a tile list with the RGB values stored as
[[[-,-,-][-,-,-][-,-,-],[-,-,-]],[[-,-,-][-,-,-][-,-,-],[-,-,-]]]
for each tile. 

It then will also keep track of the weight, based on if rotations are allowed
 
For with NO rotations, as we go through the tiles it determines 
which ones are unique and increments the weights list. 

When we have rotations, it will instead compare each tile with the other 
rotations of itself to ensure that if we already have a rotation of that tile
we won't add it. The weight of all rotated tiles are the same, and tiles with all
4 same colors have 4x the original weight

Tiles[i] == Weights[i]

Dylan Dudley - 03/27/2026

----------------------------------------------------------------"""

from PIL import Image


# This starts by converting the image into RGB Format
def load_image(path):
    img = Image.open(path).convert("RGB")
    return img

# ------------------------------------------------------------------------
#
# Checks if the tile already exists and will update the weight accordingly
#
# Returns TRUE if tile is not unique
# Else false, and updates the weight of where it was found by 1
#
# ------------------------------------------------------------------------

def uniqueTile(targetTile, tiles, Weight,rotate):
    rotations = []
    for i, tile in enumerate(tiles):
        # This is only when we allow rotations
        if(rotate):
            #Checks each orientation
            current = tile
            for _ in range(4):
                rotations.append(current)
                current = rotate_90(current)
        else:
            rotations = [tile]

        # Checks if target tile is same as the rotated tile
        for j in range(len(rotations)):
            if rotations[j] == targetTile:
                #Already exists
                Weight[i] += 1
                return False
    return True

# ------------------------------------------------------------------------
#
# Creates a list of all colors and ensures that only unique are added to list
#
# Has flag for rotation, so depending on if tiles can be rotated it will
# also do rotations
#
# Returns our tileset and the weights of each tile
#
# ------------------------------------------------------------------------
def extract_tiles(img,rotate, tile_size=2):
    # So we have the right amount of tiles based on sample image
    width, height = img.size

    # Gives direct access to the pixels in RGB form
    pixels = img.load()

    tiles = []
    Weights = []
    # now, we need to create a scanner that will go through the whole image and check each
    # section of 2x2 tiles. 
    for y in range(height - tile_size + 1):
        for x in range(width - tile_size + 1):

            # This handles dynamic tile size
            tile = [
                [pixels[x + dx, y + dy] for dx in range(tile_size)]
                for dy in range(tile_size)
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

# ------------------------------------------------------------------------
#
# This is a helper function to rotate the tile 90 degrees clockwise
#
# ------------------------------------------------------------------------
def rotate_90(tile):
    return [list(reversed(col)) for col in zip(*tile)]

# ------------------------------------------------------------------------
#
# Used to rotate tiles for all orientations
#
# This also updates weights accordingly - with 4x weight when all colors the same
# and each rotation with equal weight
#
# ------------------------------------------------------------------------
def rotateTile(tiles, Weights):
    tileLength = len(tiles)
    for i in range(tileLength):
        tile = tiles[i]

        #This is to check if all tiles are the same (Like all blue) by removing duplicates

        # Need to convert from [[A, B],[C, D]] to [A, B, C, D] to check if all colors are the same
        flat = [pixel for row in tile for pixel in row]

        if len(set(flat)) == 1:
            Weights[i] *= 4
            continue
        
        current = tile

        for j in range(3):
            current = rotate_90(current)
            # this adds each rotation to the list and the proper weight to each rotation
            tiles.append(current)
            Weights.append(Weights[i])

    return 

# ------------------------------------------------------------------------
#
# This is the main handler that is called from Main
#
# ------------------------------------------------------------------------
def imageLoad(path,rotate, tile_size=2):
    img = load_image(path)
    tiles, Weights = extract_tiles(img,rotate, tile_size)

    #print(f"Total tiles: {len(tiles)}\n")
    #for i in range(0,len(tiles)):
        #print(i," tile:", tiles[i], "\n")
        #print(i," Weight:", Weights[i], "\n")

    return tiles, Weights

