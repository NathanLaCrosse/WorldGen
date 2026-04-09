
from ursina import *

def create_voxel_mesh(world_3d, tile_size=1):
    vertices = []
    triangles = []
    colors = []
    index_offset = 0

    depth = len(world_3d)

    for z in range(depth):
        layer = world_3d[z]

        for s, sample in enumerate(layer):  # this was missing
            rows = len(sample)
            cols = len(sample[0])

            # position each sample in world space
            sample_offset_x = s * cols

            for y in range(rows):
                for x in range(cols):

                    r, g, b = sample[y][x]

                    gx = sample_offset_x + x
                    gy = z
                    gz = y

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

                    col = color.rgb(r/255, g/255, b/255)
                    colors.extend([col]*8)

                    index_offset += 8

    mesh = Mesh(vertices=vertices, triangles=triangles, colors=colors, mode='triangle')
    mesh.generate_normals()

    Entity(model=mesh, double_sided=True)