import pygame
import json 

class Spritesheet:
    def __init__(self, spritesheet):
        self.spritesheet = spritesheet
        self.sprite_sheet = pygame.image.load(spritesheet).convert()
        self.metadata = self.spritesheet.replace('png','json')
        with open(self.metadata) as f:
            self.data = json.load(f)
        f.close()
#GET SPRITE FUNCTION
    def get_sprite(self,x,y,w,h):
        sprite = pygame.Surface((w,h))
        sprite.set_colorkey((0,0,0))
        sprite.blit(self.sprite_sheet,(0,0),(x,y,w,h))
        return sprite
#PARSING SPRITE TO BE USED
    def parse_sprite(self,name):
        sprite = self.data['frames'][name]['frame']
        x,y,w,h = sprite["x"],sprite["y"],sprite["w"],sprite["h"]
        image = self.get_sprite(x,y,w,h)
        return image