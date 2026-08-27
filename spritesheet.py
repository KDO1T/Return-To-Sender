import pygame
import json 

class Spritesheet:
    def __init__(self, spritesheet):
        self.spritesheet = spritesheet
        self.sprite_sheet = pygame.image.load(spritesheet).convert()    #images may have different sizes in comparison to the surface, we use convert() to avoid the math needed to convert the sizing
        self.metadata = self.spritesheet.replace('png','json')  #we replace spritesheet.png to json so we can load it into data when we read our metadata
        with open(self.metadata) as f:
            self.data = json.load(f)
        f.close()
#GET SPRITE FUNCTION
    def get_sprite(self,x,y,w,h):
        sprite = pygame.Surface((w,h))
        sprite.set_colorkey((0,0,0))        #some sprites are "transparent" thus we set a colorkey (alpha)
        sprite.blit(self.sprite_sheet,(0,0),(x,y,w,h))
        return sprite
#PARSING SPRITE TO BE USED
    def parse_sprite(self,name):
        frame_data = self.data['frames'][name]      
        sprite = frame_data['frame']
        x,y,w,h = sprite["x"],sprite["y"],sprite["w"],sprite["h"]
        image = self.get_sprite(x,y,w,h)
        return image