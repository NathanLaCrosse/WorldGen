from ursina import *
from PNGConvert.MeshGrid import get_color
from ursina.shaders import lit_with_shadows_shader

def create_voxel_mesh(world_3d, index_to_color_3d):
    vertices = []
    triangles = []
    colors = []
    index_offset = 0
    depth = len(world_3d)

    # For how many layers we have in our 3D world
    for z in range(depth):
        layer = world_3d[z]
        rows = len(layer)

        # Since when we input sample data we have a X by X image, must make sure it is the same
        if index_to_color_3d is None:
             rows = len(layer[0])

        cols = len(layer[0])

        for y in range(rows):
            for x in range(cols):

                gx = x
                gy = z
                gz = y

                # Sets up the cubes
                cube_verts = [
                    Vec3(gx, gy, gz),
                    Vec3(gx+1, gy, gz),
                    Vec3(gx+1, gy+1, gz),
                    Vec3(gx, gy+1, gz),
                    Vec3(gx, gy, gz+1),
                    Vec3(gx+1, gy, gz+1),
                    Vec3(gx+1, gy+1, gz+1),
                    Vec3(gx, gy+1, gz+1),
                ]

                vertices.extend(cube_verts)

                cube_tris = [
                    0,1,2, 0,2,3,
                    5,4,7, 5,7,6,
                    4,0,3, 4,3,7,
                    1,5,6, 1,6,2,
                    3,2,6, 3,6,7,
                    4,5,1, 4,1,0
                ]

                triangles.extend([i + index_offset for i in cube_tris])

                # Logic to get the color for the current voxel
                if index_to_color_3d is not None:
                    colors.extend([get_color(world_3d, x, y, z, index_to_color_3d)] * 8)
                else:
                    # This does the r,g,b to normalized, and also handles the transparent case for sample
                    r,g,b = layer[0][y][x]
                    r = r / 255
                    g = g / 255
                    b = b / 255
                    
                    if r == 0 and g == 0 and b == 0:
                        colors.extend([color.rgba(0, 0, 0, 0)] * 8)  # fully transparent
                    else:
                        colors.extend([color.rgb(r, g, b)] * 8)

                index_offset += 8

    mesh = Mesh(vertices=vertices, triangles=triangles, colors=colors, mode='triangle')
    mesh.generate_normals()

    return Entity(model=mesh, double_sided=True, shader=lit_with_shadows_shader)
