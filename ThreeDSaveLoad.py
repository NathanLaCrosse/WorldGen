from WFC3D import *

def gather_tilemap_data(png_depth, png_rows, png_cols, png_folder, png_names, tile_size=2, stride=1, rotate=False, save_dir=None, load_dir=None, filename=None):
    # Save/load tilemap data for an input layered png folder
    if load_dir is None:
        tilemap, idx_to_color, color_to_idx = construct_3D_tilemap(png_depth,png_rows,png_cols,png_folder=png_folder, png_names=png_names)

        tiles, weights = collect_3D_tiles(tilemap, tile_size, rotation=rotate)
        print("Tiles Collected!")
        
        num_colors = len(idx_to_color.keys())
        num_states = len(tiles)

        tile_to_dex, dex_to_tile = build_3D_tile_hashes(tiles)
        print("Hash Tables Completed!")

        print("Num States:", num_states)

        rev_adj = collect_reverse_adjacencies(dex_to_tile, num_states, tile_size=tile_size, stride=stride)
        print("Adjacencies Built!")

        if save_dir is not None:
            with open(f"{save_dir}/{filename}.pkl", "wb") as file:
                pickle.dump([tilemap, idx_to_color, color_to_idx, tiles, weights, tile_to_dex, dex_to_tile, rev_adj], file)
            print("Data Saved!")
        
        return tilemap, idx_to_color, color_to_idx, tiles, weights, tile_to_dex, dex_to_tile, rev_adj, num_colors, num_states
    else:
        with open(f"{load_dir}/{filename}.pkl", "rb") as file:
            tilemap, idx_to_color, color_to_idx, tiles, weights, tile_to_dex, dex_to_tile, rev_adj = pickle.load(file)
        
        num_colors = len(idx_to_color.keys())
        num_states = len(tiles)

        print("Data Loaded!")

        return tilemap, idx_to_color, color_to_idx, tiles, weights, tile_to_dex, dex_to_tile, rev_adj, num_colors, num_states
    
def generate_world(tile_data_tuple, tile_size=2, stride=1, gen_size=(2,2,2), chunk_size=(8,8,8), presets=None, save_dir=None, load_dir=None, filename=None):
    # Grab all tilemap data from the tuple 
    tilemap, idx_to_color, color_to_idx, tiles, weights, tile_to_dex, dex_to_tile, rev_adj, num_colors, num_states = tile_data_tuple

    if load_dir is None:
        while True:
            space, res = generate_3D_chunks(gen_size, chunk_size, tile_to_dex, dex_to_tile, weights, num_colors, 
                tile_size, stride, seeding_presets=presets, rev_adj=rev_adj, attemps_per_chunk=3, seed_bottom=False)
            
            if res:
                break
            else:
                print("Invalid Point Reached, Restarting Generation")
                
        if save_dir is not None:
            with open(f"{save_dir}/{filename}.pkl", "wb") as file:
                pickle.dump(space, file)
        
        return space
    else:
        with open(f"{load_dir}/{filename}.pkl", "rb") as file:
            space = pickle.load(file)
        
        return space

if __name__ == "__main__":
    # Generation settings are as follows:
    #            load_tiledat, load_world, tiledat_save_name, world_save_name, tileset_folder_name, tileset_prefix, tileset_depth, row, cols, rotate
    # settings =   (True,       True,       "oceandat",         "diorama9",      "AnotherOceanMountain", "omount",     9,             32,  32,   True)
    # settings =   (False,      True,        None,              "diaorama7",      "AnotherOceanMountain", "omount",     9,             32,  32,   True)
    # settings =   (False,      True,        None,              "diaorama3",      "SmolMountain",         "mountain",   19,            32,  32,   True)
    settings =   (True,       False,       "oceandat",         "diaorama10",      "AnotherOceanMountain", "omount",     9,             32,  32,   True)
    
    gen_size = (2,4,4)
    chunk_size = (8,8,8)
    tile_size = 2
    stride = 1

    load_tiledat, load_world, tiledat_save_name, world_save_name, tileset_folder_name, tileset_prefix, png_depth, png_rows, png_cols, r = settings

    tileset_folder_name = "Generation_3D/images_3D/" + tileset_folder_name

    presets = []
    space_size = ((chunk_size[0] - tile_size)//stride + 1, (chunk_size[1] - tile_size)//stride + 1, (chunk_size[2] - tile_size)//stride + 1)

    # Presets are specified here - 
    presets.append(((0,0,0),0))

    if load_tiledat:
        data_tuple = gather_tilemap_data(png_depth, png_rows, png_cols, tileset_folder_name, tileset_prefix, tile_size, stride, r, None, "Saved_Data", tiledat_save_name)
    else:
        if tiledat_save_name is not None:
            tiledat_save_dir = "Saved_Data"
        else:
            tiledat_save_dir = None

        data_tuple = gather_tilemap_data(png_depth, png_rows, png_cols, tileset_folder_name, tileset_prefix, tile_size, stride, r, tiledat_save_dir, None, tiledat_save_name)

    tilemap, idx_to_color, color_to_idx, tiles, weights, tile_to_dex, dex_to_tile, rev_adj, num_colors, num_states = data_tuple

    if load_world:
        space = generate_world(data_tuple, tile_size, stride, gen_size, chunk_size, presets, None, "Saved_Data", world_save_name)
    else:
        if world_save_name is not None:
            world_save_dir = "Saved_Data"
        else:
            world_save_dir = None
        
        space = generate_world(data_tuple, tile_size, stride, gen_size, chunk_size, presets, world_save_dir, None, world_save_name)

    print("Starting Mesh!")
    create_voxel_mesh(space.tolist(), idx_to_color)
    print("Ending Mesh!")

    chunks = 1
    grid_size = gen_size[0]
    app = Ursina()

    # Sets up the Ursina enviornment
    DirectionalLight(x=grid_size/2,y=1+3, z=grid_size/2, shadows=True, rotation=(45, -45, 45)).look_at(Vec3(1, -1, -1))
    AmbientLight(color=color.rgba(30, 30, 30, 1))

    grid_size = gen_size[0]
    camera_spot = grid_size * chunks / 2

    # Camera
    camera.position = (camera_spot, camera_spot, -(chunks*grid_size*2))
    # camera.position = (0,0,0)
    camera.look_at(Vec3(grid_size/2, -5, 0))


    mouse.locked = True

    def input(key):
        if key == 'q':
            application.quit()
        if key == 'backspace':
            camera.position = (camera_spot, camera_spot, -(chunks * grid_size * 2))
            camera.look_at(Vec3(grid_size/2, -5, 0))

    def update():
        base_speed = 5
        speed_multiplier = 10 if held_keys['shift'] else 1
        speed = base_speed * speed_multiplier * time.dt

        if held_keys['w']:
            camera.position += camera.forward * speed
        if held_keys['s']:
            camera.position -= camera.forward * speed
        if held_keys['a']:
            camera.position -= camera.right * speed
        if held_keys['d']:
            camera.position += camera.right * speed

        # Move up
        if held_keys['space']:
            camera.position += Vec3(0, speed * 20 * time.dt, 0)
        # Move down
        if held_keys['control']:
            camera.position -= Vec3(0, speed * 20 * time.dt, 0)

        camera.rotation_y += mouse.velocity[0] * 40
        camera.rotation_x -= mouse.velocity[1] * 40
        camera.rotation_x = clamp(camera.rotation_x, -90, 90)

    app.run()