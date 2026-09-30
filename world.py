import random
from tilemap import Obstacle
from spritesheet import Spritesheet

class World_Generation:
    def __init__(self, tile_size, chunk_tiles_x, chunk_tiles_y, noise1d, noise2d):
        self.tile_size = tile_size
        self.chunk_tiles_x = chunk_tiles_x
        self.chunk_tiles_y = chunk_tiles_y
        self.chunk_pixel_w = chunk_tiles_x * tile_size
        self.chunk_pixel_h = chunk_tiles_y * tile_size
        self.noise1d = noise1d
        self.noise2d = noise2d
        self.obstacle_spritesheet  = Spritesheet('obstacle_spritesheet.png')  #change this.
        self.obstacle_types = []
        for sprite_name, frame_data in self.obstacle_spritesheet.data['frames'].items():
            is_solid = not sprite_name.startswith('bush')   #checks if sprite is a solid state

            self.obstacle_types.append({
                'sprite': sprite_name,
                'solid': is_solid,
                'w': frame_data['frame']['w'],
                'h': frame_data['frame']['h'],
            })

    def world_to_chunk(self,world_x,world_y):
        chunk_x, chunk_y = int(world_x//self.chunk_pixel_w), int(world_y//self.chunk_pixel_h)
        return chunk_x, chunk_y

    def generate_chunk_data(self, chunk_x, chunk_y):
        grid = []
        surface_scale = 0.02
        cave_scale = 0.04
        base_height = 7
        amplitude = 10

        for y in range(-1,self.chunk_tiles_y):
            row = []
            world_tile_y = chunk_y*self.chunk_tiles_y + y
            for x in range(self.chunk_tiles_x):
                world_tile_x = chunk_x*self.chunk_tiles_x + x

                noise_volume = self.noise1d([world_tile_x*surface_scale])
                surface_y = base_height + int(noise_volume*amplitude)

                cave_volume = self.noise2d([world_tile_x * cave_scale , world_tile_y * cave_scale])

                depth = world_tile_y - surface_y

                #the depth determines how deep the caves should go
                if depth < 0:
                    row.append('-1')
                #surface Layer
                elif depth == 0:
                    if cave_volume <= -0.25:
                        row.append('-1')
                    else:
                        row.append('1')
                elif depth <4:
                    if cave_volume <= -0.22:
                        row.append('-1')
                    else:
                        row.append('11')
                #underground Caves
                else:
                    cave_threshold = -0.01 + min(0.15, (depth-4)*0.01)

                    if depth >20:
                        cave_threshold -= (depth-20)*0.02

                    if cave_volume <= cave_threshold:
                        row.append('-1')
                    else:
                        row.append('11')         
            grid.append(row)

        #adjacency checker
            for y in range(len(grid)):
                if y < len(grid):
                    col = len(grid[y])
                else:
                    col = 0
                for x in range(col):

                    if grid[y][x] == '11':      #dirt tile

                        if y>0 and (y+1) < len(grid):           #checks if there is a row above and below
                                
                            if x < len(grid[y-1]) and x < len(grid[y+1]):  #checks if there is a row beside the column
                                tile_above = grid[y-1][x]
                                tile_below = grid[y+1][x]

                                if tile_above == '-1' and tile_below == '11':
                                    grid[y][x] = '1'            #grass tile

            for x in range(len(grid[0])):
                for y in range(len(grid)):

                    if grid[y][x] == '11':

    
                            if y>0:  #checks if there is a row beside the column
                                tile_above = grid[y-1][x]

                                if tile_above == '-1':
                                    grid[y][x] = '1'
        return grid

    def generate_chunk_obstacles(self, chunk_x, chunk_y, tile_grid):
        chunk_obstacles = []
        chunk_world_min_x = chunk_x * self.chunk_pixel_w

        num_rows = len(tile_grid)
        if num_rows >0:
            num_columns = len(tile_grid[0])
        else:
            num_columns = 0

        min_obstacle_spacing = 3
        last_spawned_column = -min_obstacle_spacing


        for column in range(num_columns):

            if column - last_spawned_column < min_obstacle_spacing:
                continue
            
            for row in range(num_rows):
                tile_id = tile_grid[row][column]

                if tile_id != '-1' and row >0 and tile_grid[row-1][column] == '-1':

                    #Flat ground check
                    is_flat = False
                    if column + 1 < num_columns:
                        adjacent_ground = tile_grid[row][column + 1] != '-1'
                        adjacent_air = tile_grid[row-1][column+1] == '-1'
                        if adjacent_air and adjacent_ground:
                            is_flat = True

                    if is_flat and random.random() < 0.15:    #15% of spawning an obstacle
                        obstacle_info = random.choice(self.obstacle_types)

                        #obstacle spawn coords
                        obstacle_x = chunk_world_min_x + (column*self.tile_size)
                        obstacle_y = chunk_y*self.chunk_pixel_h + random.randint(0,64)

                        obstacle = Obstacle(
                            sprite_name= obstacle_info['sprite'],
                            x= obstacle_x,
                            y= obstacle_y,
                            spritesheet= self.obstacle_spritesheet,
                            solid=obstacle_info['solid'],
                            width = obstacle_info.get('w',32),
                            height = obstacle_info.get('h',32)
                        )
                        chunk_obstacles.append(obstacle)
                        last_spawned_column = column
                    break #stop finding once object is placed

        return chunk_obstacles

