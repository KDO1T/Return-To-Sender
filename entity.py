import pygame, sys, random


class Player:
    # *--STATS--*
    #level is the player's level, while exp is what the player gains to increase in level
    #dollars is the money the player gains throughout runs while s_coin (soul coins) is the metacurrency
    def __init__(self, Name,rect,movement,moving_up,moving_down ,moving_right ,moving_left, press_space, y_momentum,max_air_jumps,jump,on_ground,x_flip,
                 all_frames ,current_frames ,frame_index, animation_mode, animation_count,max_HP, damaged,base_ATK,attacking,attack_dir, first_hit_count,
                 combo_tick,combo_stage, combo_cooldown, combo_window, max_combo_window, first_hit_cooldown, attacked, CRIT_DMG, CRIT_CHANCE, LEVEL, EXP, DOLLARS, S_COIN):
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
        self.max_HP = max_HP
        self.HP = max_HP
        self.damaged = damaged
        self.base_ATK = base_ATK
        self.attack_dir = attack_dir
        self.first_hit_count = first_hit_count #the time starting from when the player isnt attacking anything
        self.combo_tick = combo_tick #the time between each hit and use this to check if you should continue the combo or not
        self.combo_stage = combo_stage #which hit the player is in their combo
        self.first_hit_cooldown = first_hit_cooldown #self explanatory
        self.combo_cooldown = combo_cooldown # <-- This should always be less than the first_hit_cooldown to incentivize the player to not spam and hold the button
        self.combo_window = combo_window #the time between each hit of a combo
        self.max_combo_window = max_combo_window 
        self.mom_force = 5 #the momentum the player applies to zombies when knocking them back
        self.attacking = attacking
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



    def check_cooldown(self):


        if self.combo_window > 0: #if player hasn't executed the next move in the combo, it will minus 1 from the frames in the 'window' of the move
            self.combo_window -= 1 
            if self.combo_window == 0:
                self.combo_stage = 0
                print('combo expired bru')


        if self.attacking is True and self.attacked is False: #if this is the player first hit 
            if self.combo_tick < self.combo_cooldown:
                self.combo_tick = self.combo_cooldown #makes sure the first hit is instant
                self.combo_tick += 1
                
            print('first hit')

        elif self.attacking is True and self.attacked is True: #if player is attacking and has already attacked previously, just add do the counter normally
            self.combo_tick += 1

        if self.attacked is True and self.attacking is False: #resets first hit cooldown when they have previously attacked 
            self.first_hit_count += 1                         #and they are not currently attacking
            if self.first_hit_count >= self.first_hit_cooldown:
                self.attacked = False
                self.first_hit_count = 0
                self.combo_stage = 0
            else:
                self.first_hit_count += 1


    def attack(self,zombie_damaged, zombie_hitbox, player_damage):
        if self.combo_tick >= self.combo_cooldown:
            if self.rect.colliderect(zombie_hitbox):
                print('TAKE THAT')

                if self.combo_stage < 5: #if it isn't the 5th stage, add one more stage to the combo
                    self.combo_stage += 1
                else:
                    self.combo_stage = 1 #if it's more than 5 than revert back to stage 1

                player_damage = self.base_ATK*(self.combo_stage/5)
                print(f'damaged for {player_damage}!')
                zombie_damaged = True
                self.attacked = True
                self.combo_tick = 0

                self.combo_window = self.max_combo_window
            

        return zombie_damaged, player_damage


    def receive_damage(self, zombie_damage):
        if self.damaged is True:
            self.HP -= zombie_damage
            self.damaged = False

            print(f'i have been hit by this filthy zombie for {zombie_damage} and now im {self.HP}. my maxHP is {self.max_HP}')


        


            
        
    
zombies = []
#stores each zombie's attributes within the Zombie class

class Zombie:

    def __init__(self, rect, movement, x_push_momentum, y_push_momentum, y_momentum, x_flip, render_pos, on_ground, idle_move, chase_player, chase_speed ,
                 attack_count, knocked, damaged, staggered,stag_count,max_stag_count, HP, ATK):
        self.rect = rect
        self.movement = movement
        self.x_push_momentum = x_push_momentum
        self.y_push_momentum = y_push_momentum
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

        if x_distance <=256 and y_distance <= 128:
            self.chase_player = True 
        else:
            self.chase_player = False


            
    def touch_player(self, player_hitbox):
        if self.rect.colliderect(player_hitbox):
            self.attack_count += 1

    def attack_player(self, player_damaged): #add player hp in paranthesis
        if self.attack_count >= 60:         
            player_damaged = True
            self.attack_count = 0

            return player_damaged



    def receive_damage(self, player_damage):
        if self.damaged == True:
            self.HP -= player_damage
            print(f'you hurt me bruh, im now {self.HP}')
            self.damaged = False
            self.staggered = True
            self.knocked = True

    def dead_check(self, zomb_index):
        if self.HP <= 0:
            return zomb_index



    def calculate_knockback(self, player_force, player_direction, player_rect ):
        if self.knocked == True:
            if player_direction == False: #facing right
                self.rect.left = player_rect.right
                self.x_push_momentum += player_force//3
                self.y_push_momentum += -player_force//5

            if player_direction == True: #facing left
                self.rect.right = player_rect.left
                self.x_push_momentum -= player_force//3
                self.y_push_momentum += -player_force//5

            self.knocked = False



        pass

    
        # if self.knocked == True:
    
        #     if player_direction == False: #facing right
        #         self.rect.left = player_rect.right
        #         self.x_momentum += player_force//2
        #         self.y_momentum += -player_force//10

        #     if player_direction == True: #facing left
        #         self.rect.right = player_rect.left
        #         self.x_momentum -= player_force//2
        #         self.y_momentum += -player_force//10

            
            
        #     self.knocked = False #put this into Y knockback code
        #     print('i got knocked')

    def check_staggered(self):
        if self.staggered is True:
            self.stag_count += 1

        if self.stag_count >= self.max_stag_count: #staggered for how long the zombie should be staggered for (base duration is 45 aka 3/4 sec)
            self.staggered = False
            self.stag_count = 0
    




        #checks if it is in x distance from the player
        #returns boolean to change the zombie behaviour in movement





