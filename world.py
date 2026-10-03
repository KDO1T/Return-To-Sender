import random
import pygame
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
        self.last_obstacle_col = -999
        self.obstacle_spritesheet  = Spritesheet('asset/obstacle_spritesheet.png')  #change this.
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
        #platform generation

        if random.random() < 0.33:    
            platform_length = 3 
            placed = False

            start_x = random.randint(0, self.chunk_tiles_x - platform_length)

            surface_row = None
            for y in range(1,len(grid)):
                if grid[y][start_x] != '-1' and grid[y-1][start_x] == '-1':
                    surface_row = y
                    break

            if surface_row is not None and surface_row >= 8:
                platform_y = surface_row - random.randint(3,4)

                can_place = True
                for platformx in range(start_x, start_x + platform_length):
                    if grid[platform_y][platformx] != '-1' or grid[platform_y +1][platformx] != '-1':
                        can_place = False
                        break

                if can_place:
                    for platformx in range(start_x, start_x + platform_length):
                        grid[platform_y][platformx] = '1'
                        grid[platform_y + 1][platformx] = '-1'
                        placed = True
            
        return grid

    def generate_chunk_obstacles(self, chunk_x, chunk_y, tile_grid, last_global_col):
        chunk_obstacles = []
        chunk_world_min_x = chunk_x * self.chunk_pixel_w

        num_rows = len(tile_grid)
        if num_rows == 0:
            return chunk_obstacles, last_global_col
        num_columns = len(tile_grid[0])

        min_obstacle_spacing = 5
        chunk_start_col = chunk_x * num_columns

        for column in range(num_columns):
            global_col = chunk_start_col + column
            
            if global_col - last_global_col < min_obstacle_spacing:
                continue

            surface_row = None
            for row in range(num_rows):
                tile_id = tile_grid[row][column]
                if tile_id != '-1' and row >0 and tile_grid[row-1][column] == '-1':

                    is_above_surface = True
                    for row_above in range(0, row):
                        if tile_grid[row_above][column] != '-1':
                            is_above_surface = False
                            break

                    if is_above_surface:
                        surface_row = row
                        break
                    

            if surface_row is not None:
                if random.random() < 0.15:
                    obstacle_info = random.choice(self.obstacle_types)

                    obstacle_w = obstacle_info.get('w',32)  #calculates the width of one obstacle
                    tiles_needed = (obstacle_w// self.tile_size) + 1

                    if column + tiles_needed <= num_columns:
                        #Flat ground check
                        is_flat = True

                        for column_offset in range(tiles_needed):
                            check_col = column + column_offset

                            adjacent_ground = tile_grid[surface_row][check_col] != '-1'
                            adjacent_air = tile_grid[surface_row-1][check_col] == '-1'
                            if not (adjacent_air and adjacent_ground):
                                is_flat = False
                                break

                        if is_flat:    #15% of spawning an obstacle
                            #obstacle spawn coords
                            obstacle_x = chunk_world_min_x + (column*self.tile_size)
                            obstacle_y = chunk_y*self.chunk_pixel_h + random.randint(0,64)

                            obstacle = Obstacle(
                                sprite_name= obstacle_info['sprite'],
                                x= obstacle_x,
                                y= obstacle_y,
                                spritesheet= self.obstacle_spritesheet,
                                solid=obstacle_info['solid'],
                                width = obstacle_w,
                                height = obstacle_info.get('h',32)
                            )
                            chunk_obstacles.append(obstacle)
                            last_global_col = global_col + tiles_needed + min_obstacle_spacing

        return chunk_obstacles, last_global_col

class ParallaxBackground:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.layers = []

    def add_layer(self, image_path, scroll_factor):
        image = pygame.image.load(image_path).convert_alpha() #removes alpha channel from image
        image = pygame.transform.scale(image, (self.screen_width,self.screen_height))
        self.layers.append({
            'surface': image,
            'factor': scroll_factor,
            'width': image.get_width()
        })

    def draw(self,surface,camera_x,camera_y=0):
        for layer in self.layers:
            img = layer['surface']
            factor = layer['factor']
            width = layer['width']

            x_offset = (camera_x *factor)%width

            draw_x = -x_offset

            surface.blit(img, (draw_x,0))
            if draw_x < 0:
                surface.blit(img,(draw_x + width,0))
            elif draw_x > 0:
                surface.blit(img, (draw_x - width,0))

class StageFade:
    def __init__(self, display_surface):
        self.display = display_surface
        self.fade_surface = pygame.Surface(self.display.get_size()).convert()
        self.fade_surface.fill((0,0,0))
        self.fade_alpha = 255
        self.fade_speed = 5
        self.is_fading_in = True

    def reset_fade(self, display_surface = None):       #reset the fade values
        if display_surface:
            self.display = display_surface
        
        self.fade_alpha = 255
        self.is_fading_in = True

    def update_fade(self):
        if self.is_fading_in:
            self.fade_alpha = max(0, self.fade_alpha - self.fade_speed) 
            if self.fade_alpha == 0:
                self.is_fading_in = False

    def draw_fade(self, surface = None):
        if surface is not None:
            target = surface
        else:
            target = self.display
        if self.fade_alpha > 0:
            self.fade_surface.set_alpha(int(self.fade_alpha))
            target.blit(self.fade_surface, (0,0))