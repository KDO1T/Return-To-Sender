import pygame, sys, random


class Player:
    # *--STATS--*
    #level is the player's level, while exp is what the player gains to increase in level
    #dollars is the money the player gains throughout runs while s_coin (soul coins) is the metacurrency
    def __init__(self, Name,rect,movement,moving_up,moving_down ,moving_right ,moving_left, press_space, y_momentum,max_air_jumps,jump,on_ground,x_flip,
                 all_frames ,current_frames ,frame_index, animation_mode, animation_count, HP, ATK,attacked, CRIT_DMG, CRIT_CHANCE, LEVEL, EXP, DOLLARS, S_COIN):
        self.Name = Name
        self.rect = rect
        self.movement = movement
        self.moving_up = moving_up
        self.moving_down = moving_down
        self.moving_right = moving_right
        self.moving_left = moving_left
        self.press_space = press_space
        self.y_momentum = y_momentum
        self.max_air_jumps = max_air_jumps
        self.air_jump_count = max_air_jumps
        self.jump = jump
        self.on_ground = on_ground
        self.x_flip = x_flip
        self.all_frames = all_frames
        self.current_frames = current_frames
        self.frame_index = frame_index
        self.animation_mode = animation_mode
        self.animation_count = animation_count
        self.HP = HP
        self.ATK = ATK
        self.mom_force = ATK*5 #the momentum the player applies to zombies when knocking them back
        self.attacked = attacked
        self.CRIT_DMG = CRIT_DMG
        self.CRIT_CHANCE = CRIT_CHANCE
        self.LEVEL = LEVEL
        self.EXP = EXP 
        self.DOLLARS = DOLLARS
        self.S_COIN = S_COIN

    def update_action (self):

        if self.animation_mode == 0: #idle
           self.current_frames = self.all_frames[0:5]

        if self.animation_mode == 1: #walk
            self.current_frames = self.all_frames[6:10]

        if self.animation_mode == 2: #jump
            self.current_frames = self.all_frames[11:14]

        if self.animation_mode == 3: #fall
            self.current_frames = self.all_frames[15:17]

        return self.current_frames

    def update_player_frame (self): #math for frame indexing
        self.animation_count += 1

        if self.animation_count == 60:
            self.animation_count = 0

        if self.animation_mode == 0: #idling
            self.frame_index = (self.animation_count // 10) % len(self.current_frames)

        if self.animation_mode == 1: #walking
            self.frame_index = (self.animation_count // 12) % len(self.current_frames)
            
        if self.animation_mode == 2: #jumping
            self.frame_index = (self.animation_count // 15) % len(self.current_frames)
            
        if self.animation_mode == 3: #falling
            self.frame_index = (self.animation_count // 20) % len(self.current_frames)

        return self.animation_count, self.frame_index

    def attack(self, zombie_hitbox,zombie_damaged):
        if self.attacked == True:
            if self.rect.colliderect(zombie_hitbox):
                zombie_damaged = True
        
            return zombie_damaged
        
    
zombies = []
#stores each zombie's attributes within the Zombie class

class Zombie:

    def __init__(self, rect, movement, x_momentum, y_momentum, x_flip, render_pos, on_ground, idle_move, chase_player, chase_speed ,
                 attack_count, knocked, damaged, staggered,stag_count,max_stag_count, HP, ATK):
        self.rect = rect
        self.movement = movement
        self.x_momentum = x_momentum
        self.y_momentum = y_momentum
        self.x_flip = x_flip
        self.render_pos = render_pos
        self.on_ground = on_ground
        self.idle_move = idle_move
        self.chase_player = chase_player
        self.chase_speed = chase_speed
        self.attack_count = attack_count
        self.knocked = knocked
        self.damaged = damaged
        self.staggered = staggered
        self.stag_count = stag_count
        self.max_stag_count = max_stag_count
        self.HP = HP
        self.ATK = ATK



    def generate_rect(self, i, player_current_chunk_x):
        self.rect = pygame.Rect(((player_current_chunk_x + 640) + (i*30)), 50, 20,32)

    def aggro_player(self, player_position):

        x_distance = abs(self.render_pos[0] - player_position[0])
        y_distance = abs(self.render_pos[1] - player_position[1])

        if x_distance <=128 and y_distance <= 128:
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




    def receive_damage(self, player_damage):
        if self.damaged == True:
            self.HP -= player_damage
            self.damaged = False
            self.staggered = True
            self.knocked = True
            print(self.HP)


    def receive_knockback(self, player_force, player_direction):
        if self.knocked == True:

            if player_direction == False: #facing right
                self.x_momentum += player_force
                self.y_momentum += -player_force//10

            if player_direction == True: #facing left
                self.x_momentum -= player_force
                self.y_momentum += -player_force//10

            self.knocked = False
            print('i got knocked')

    def check_staggered(self):
        if self.staggered is True:
            self.stag_count += 1

        if self.stag_count == self.max_stag_count: #staggered for how long the zombie should be staggered for (base duration is 30 aka 0.5 sec)
            self.staggered = False
            self.stag_count = 0
    




        #checks if it is in x distance from the player
        #returns boolean to change the zombie behaviour in movement





