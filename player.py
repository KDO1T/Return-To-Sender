import pygame, sys

class Player:

    # *--STATS--*
    #level is the player's level, while exp is what the player gains to increase in level
    #dollars is the money the player gains throughout runs while s_coin (soul coins) is the metacurrency
    def __init__(self, Name, HP, ATK, CRIT_DMG, CRIT_CHANCE, LEVEL, EXP, DOLLARS, S_COIN):
        self.Name = Name
        self.HP = HP
        self.ATK = ATK
        self.CRIT_DMG = CRIT_DMG
        self.CRIT_CHANCE = CRIT_CHANCE
        self.LEVEL = LEVEL
        self.EXP = EXP 
        self.DOLLARS = DOLLARS
        self.S_COIN = S_COIN




class Player_Sprite(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__()
        self.pos_x = pos_x
        self.pos_y = pos_y


    def load_idle_sprites(self):
        self.sprites = []
        file_name = None
        for i in range(8): #there are 7 sprites but we skip index 0 so it goes from 1 --> 7
            if i == 0:
                continue
            else:
                file_name = 'idle_' + f'{i}' + '.png'
                self.sprites.append(pygame.image.load(f'animations/idle/{file_name}').convert_alpha()) 

        self.current_sprite = 0 #index
        self.image = self.sprites[self.current_sprite]
    
    def load_walk_sprites(self):
        pass

    def update(self):

        self.current_sprite += 0.2

        if self.current_sprite >= len(self.sprites):
            self.current_sprite = 0

        self.image = self.sprites[int(self.current_sprite)]



        
        























    #dev only, dont keep in final
    def show_stat(self):
        print(f"""
Name: {self.Name}
HP: {self.HP}
ATK: {self.ATK}
CRIT_DMG: {self.CRIT_DMG}
CRIT_CHANCE: {self.CRIT_CHANCE}
LEVEL: {self.LEVEL}
EXP: {self.EXP}
DOLLARS: {self.DOLLARS}
S_COIN: {self.S_COIN}""")


    
    