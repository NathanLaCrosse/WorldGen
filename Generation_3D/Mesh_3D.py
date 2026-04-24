from ursina import *
from PNGConvert.MeshGrid import get_color
from ursina.shaders import lit_with_shadows_shader


def neighbor_check(world, x, y ,z):
    if z < 0 or z >= len(world):
        return True
    if y < 0 or y >= len(world[0]):
        return True
    if x < 0 or x >= len(world[0][0]):
        return True

    return world[z][y][x] == 0  # adjust if your "empty" value differs

def create_voxel_mesh(world_3d, index_to_color_3d):
    vertices = []
    triangles = []
    colors = []
    index_offset = 0
    depth = len(world_3d)

    cube_tris = [
                    0,1,2, 0,2,3,
                    5,4,7, 5,7,6,
                    4,0,3, 4,3,7,
                    1,5,6, 1,6,2,
                    3,2,6, 3,6,7,
                    4,5,1, 4,1,0
                ]
    
    # For how many layers we have in our 3D world
    for z in range(depth):
        layer = world_3d[z]
        rows = len(layer)


        cols = len(layer[0])

        for y in range(rows):
            for x in range(cols):

                gx = float(x)
                gy = float(z)
                gz = float(y)

                color = get_color(world_3d, x, y, z, index_to_color_3d)

                if (color[0] == 0 and color[1] == 0 and color[2] == 0):
                    continue

                colors.extend([color] * 8)

                # Sets up the cubes
                cube_verts = [
                    (gx, gy, gz),
                    (gx+1, gy, gz),
                    (gx+1, gy+1, gz),
                    (gx, gy+1, gz),
                    (gx, gy, gz+1),
                    (gx+1, gy, gz+1),
                    (gx+1, gy+1, gz+1),
                    (gx, gy+1, gz+1),
                ]

                vertices.extend(cube_verts)

                triangles.extend([i + index_offset for i in cube_tris])

                index_offset += 8

    mesh = Mesh(vertices=vertices, triangles=triangles, colors=colors, mode='triangle')
    mesh.generate_normals()

    return Entity(model=mesh, double_sided=True, shader=lit_with_shadows_shader)
