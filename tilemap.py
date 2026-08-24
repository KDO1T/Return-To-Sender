import pygame, csv, os

class Tile(pygame.sprite.Sprite):
    def __init__(self, sprite_name,x,y,spritesheet):
        pygame.sprite.Sprite.__init__(self)
        self.image = spritesheet.parse_sprite(sprite_name)
        #CREATE A RECT FOR COLLISION
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    #FUNCTION FOR DRAWING TILES
    def draw(self, surface):                #draws a surface(tile) with a rectangle box of the image
        surface.blit(self.image,(self.rect.x,self.rect.y))

class TileMap():
    def __init__(self, test_level, spritesheet):
        self.spritesheet = spritesheet
        self.tile_size = 32
        self.start_x = 0
        self.start_y = 0
        self.map_data = self.read_csv(test_level)   #takes the values in the test_level.csv file and assigns it to map_data
        self.map_w = len(self.map_data[0])*self.tile_size   #calculates the number of columns in one row and multiplies it with the tile size (32)
        self.map_h = len(self.map_data)*self.tile_size  #same but with rows
        self.map_surface = pygame.Surface((self.map_w, self.map_h)) #creates a surface that is mimics the size of each column and row but sized to the correct tile size
        self.map_surface.set_colorkey((0,0,0))
        self.tiles = self.load_tiles(test_level)
        self.load_map() #loads the map

    def draw_map(self, surface):
        surface.blit(self.map_surface, (0,0)) #draws the map surface
        
    def load_map(self):
        for tile in self.tiles:
            tile.draw(self.map_surface) #draws all the tiles (after loading the tile function) onto the map surface

    #READ CSV TO PARSE
    def read_csv(self, test_level):
        map = []
        with open(test_level) as data:
            data = csv.reader(data, delimiter=",")  #reads the data by separating it from each comma
            for row in data:
                map.append(list(row)) #appends one row as one list into a bigger list (map[])
        return map

    #LOAD TILES INTO THE CSV INDEX
    def load_tiles(self, test_level):
        tiles = []
        map = self.read_csv(test_level)
        y= 0
        for row in map:
            x=0
            for tile in row:
                tile_id = tile
                #AVOID -1 
                if tile_id != '-1':
                    map_x = x*self.tile_size
                    map_y = y*self.tile_size

                    tile_num = int(tile_id)+1
                    sprite_name = f"tile{tile_num:02d}"

                    tiles.append(Tile(sprite_name, map_x, map_y, self.spritesheet))
                x+=1
            y+=1

        return tiles