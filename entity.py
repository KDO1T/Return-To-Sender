import pygame, sys, random


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



    
    
zombies = []
#stores each zombie's attributes within the Zombie class

class Zombie:

    def __init__(self, rect, movement, y_momentum, x_flip, render_pos, on_ground, idle_move, chase_player, attack_count, HP, ATK):
        self.rect = rect
        self.movement = movement
        self.y_momentum = y_momentum
        self.x_flip = x_flip
        self.render_pos = render_pos
        self.on_ground = on_ground
        self.idle_move = idle_move
        self.chase_player = chase_player
        self.attack_count = attack_count
        self.HP = HP
        self.ATK = ATK



    def generate_rect(self, i, player_current_chunk_x):
        self.rect = pygame.Rect(((player_current_chunk_x + 640) + (i*30)), 50, 20,32)

    def aggro_player(self, player_position):

        x_distance = abs(self.render_pos[0] - player_position[0])
        y_distance = abs(self.render_pos[1] - player_position[1])

        if x_distance <= 90 and y_distance <= 90:
            self.chase_player = True 
        else:
            self.chase_player = False


            
    def touch_player(self, player_hitbox):
        if self.rect.colliderect(player_hitbox):
            self.attack_count += 1
        
           

       

    def attack_player(self): #add player hp in paranthesis
        if self.attack_count >= 60:         
            print('i touched you')
            self.attack_count = 0


        #checks if it is in x distance from the player
        #returns boolean to change the zombie behaviour in movement





