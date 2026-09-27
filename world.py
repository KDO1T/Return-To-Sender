class World_Generation:
    def __init__(self, tile_size, chunk_tiles_x, chunk_tiles_y, noise1d, noise2d):
        self.tile_size = tile_size
        self.chunk_tiles_x = chunk_tiles_x
        self.chunk_tiles_y = chunk_tiles_y
        self.chunk_pixel_w = chunk_tiles_x * tile_size
        self.chunk_pixel_h = chunk_tiles_y * tile_size
        self.noise1d = noise1d
        self.noise2d = noise2d

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