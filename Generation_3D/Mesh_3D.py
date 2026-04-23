from ursina import *
from PNGConvert.MeshGrid import get_color
from ursina.shaders import lit_with_shadows_shader

def create_voxel_mesh(world_3d, index_to_color_3d):
    depth = len(world_3d)
    rows = len(world_3d[0])
    cols = len(world_3d[0][0])

    cube_tris = [
        0,1,2, 0,2,3,
        5,4,7, 5,7,6,
        4,0,3, 4,3,7,
        1,5,6, 1,6,2,
        3,2,6, 3,6,7,
        4,5,1, 4,1,0
    ]

    vertices = [None] * (depth*rows*cols*8)
    triangles = [None] * (depth*rows*cols*len(cube_tris))
    colors = [None] * (depth*rows*cols*8)
    index_offset = 0

    # For how many layers we have in our 3D world
    for z in range(depth):
        layer = world_3d[z]

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

                # vertices.extend(cube_verts)

                for k in range(8):
                    vertices[(z*rows*cols + y*cols + x)*8 + k] = cube_verts[k]

                # triangles.extend([i + index_offset for i in cube_tris])
                for k in range(len(cube_tris)):
                    triangles[(z*rows*cols + y*cols + x)*len(cube_tris) + k] = cube_tris[k] + index_offset

                # Logic to get the color for the current voxel
                current_colors = None
                if index_to_color_3d is not None:
                    current_colors = [get_color(world_3d, x, y, z, index_to_color_3d)] * 8
                else:
                    # This does the r,g,b to normalized, and also handles the transparent case for sample
                    r,g,b = layer[0][y][x]
                    r = r / 255
                    g = g / 255
                    b = b / 255
                    
                    if r == 0 and g == 0 and b == 0:
                        current_colors = [color.rgba(0, 0, 0, 0)] * 8  # fully transparent
                    else:
                        current_colors = [color.rgb(r, g, b)] * 8

                for k in range(8):
                    colors[(z*rows*cols + y*cols + x)*8 + k] = current_colors[k]

                index_offset += 8

    mesh = Mesh(vertices=vertices, triangles=triangles, colors=colors, mode='triangle')
    mesh.generate_normals()

    return Entity(model=mesh, double_sided=True, shader=lit_with_shadows_shader)
