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
    def draw(self, surface):
        surface.blit(self.image,(self.rect.x,self.rect.y))

class TileMap():
    def __init__(self, test_level, spritesheet):
        self.spritesheet = spritesheet
        self.tile_size = 32
        self.start_x = 0
        self.start_y = 0
        self.map_data = self.read_csv(test_level)
        self.map_w = len(self.map_data[0])*self.tile_size
        self.map_h = len(self.map_data)*self.tile_size
        self.map_surface = pygame.Surface((self.map_w, self.map_h))
        self.map_surface.set_colorkey((0,0,0))
        self.tiles = self.load_tiles(test_level)
        self.load_map()

    def draw_map(self, surface):
        surface.blit(self.map_surface, (0,0))
        
    def load_map(self):
        for tile in self.tiles:
            tile.draw(self.map_surface)

    #READ CSV TO PARSE
    def read_csv(self, test_level):
        map = []
        with open(os.path.join(test_level)) as data:
            data = csv.reader(data, delimiter=",")
            for row in data:
                map.append(list(row))
        return map

    #LOAD TILES INTO THE CSV INDEX
    def load_tiles(self, test_level):
        tiles = []
        map = self.read_csv(test_level)
        y= 0
        for row in map:
            x=0
            for tile in row:
                tile_id = tile.strip()

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