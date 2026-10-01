import pygame, sys, random


class Player:
    # *--STATS--*
    #level is the player's level, while exp is what the player gains to increase in level
    #dollars is the money the player gains throughout runs while s_coin (soul coins) is the metacurrency
    def __init__(self, Name,rect,attack_rect,movement,moving_up,moving_down ,moving_right ,moving_left,dash, dashing,dash_dis,dash_counter, 
                 hor_aim_list, holding_up, holding_down, vert_aim_list, aim_up,aim_down, dash_charges,max_dash_buffer,dash_buffer, 
                 max_dash_charges, aim_right, aim_left, press_space,
                  y_momentum,x_momentum, max_air_jumps,jump,jump_height,on_ground,x_flip, all_frames ,current_frames ,frame_index, animation_mode,
                    animation_count,max_HP,i_counter,invulnerable, damaged,base_ATK,attacking, holding_attack, attacked,attack_count,combo_stage, hit_landed, combo_buffer,
                    CRIT_DMG, CRIT_CHANCE, LEVEL, EXP, DOLLARS, S_COIN):
        self.Name = Name
        self.rect = rect
        self.attack_rect = attack_rect #contains hitbox for each attack
        self.movement = movement
        self.moving_up = moving_up
        self.moving_down = moving_down
        self.moving_right = moving_right
        self.moving_left = moving_left
        self.dash = dash
        self.max_dash_charges = max_dash_charges
        self.dash_charges = max_dash_charges
        self.dash_buffer = dash_buffer
        self.max_dash_buffer = max_dash_buffer
        self.dashing = dashing
        self.dash_dis = dash_dis
        self.dash_counter = dash_counter
        self.hor_aim_list = hor_aim_list #holds what horizontal directions the player looked at
        self.vert_aim_list = vert_aim_list #holds what vertical directions the player looked at
        self.holding_up = holding_up
        self.holding_down = holding_down
        self.aim_up = aim_up
        self.aim_down = aim_down
        self.aim_right = aim_right
        self.aim_left = aim_left
        self.press_space = press_space
        self.x_momentum = x_momentum
        self.y_momentum = y_momentum
        self.max_air_jumps = max_air_jumps
        self.air_jump_count = max_air_jumps
        self.jump = jump
        self.jump_height = jump_height
        self.on_ground = on_ground
        self.x_flip = x_flip
        self.all_frames = all_frames
        self.current_frames = current_frames
        self.frame_index = frame_index
        self.animation_mode = animation_mode
        self.animation_count = animation_count
        self.max_HP = max_HP
        self.HP = max_HP
        self.i_counter = i_counter #invincible frames
        self.invulnerable = invulnerable 
        self.damaged = damaged
        self.base_ATK = base_ATK
        self.mom_force = 5 #the momentum the player applies to zombies when knocking them back
        self.attacking = attacking
        self.holding_attack = holding_attack
        self.attacked = attacked
        self.attack_count = attack_count
        self.combo_stage = 1
        self.combo_multipliers = [1.0025,1.002,1.003]
        self.hit_landed = hit_landed 
        self.hit_number = 0
        self.combo_buffer = combo_buffer #time between each slash of the combo
        self.CRIT_DMG = CRIT_DMG
        self.CRIT_CHANCE = CRIT_CHANCE
        self.LEVEL = LEVEL
        self.EXP = EXP 
        self.DOLLARS = DOLLARS
        self.S_COIN = S_COIN

    def update_action (self):
        
        if self.animation_mode == 0: 
            self.current_frames = self.all_frames[0:11]

        if self.animation_mode == 1: 
            self.current_frames = self.all_frames[12:23]

        if self.animation_mode == 2: 
            self.current_frames = self.all_frames[24:35]
        
        if self.animation_mode == 3: 
            self.current_frames = self.all_frames[36:47]

        if self.animation_mode == 4: 
            self.current_frames = self.all_frames[48:51]

        if self.animation_mode == 5: 
            self.current_frames = self.all_frames[52:55]

        if self.animation_mode == 6: 
            self.current_frames = self.all_frames[56:67]

        if self.animation_mode == 7: 
            self.current_frames = self.all_frames[68:79]

        if self.animation_mode == 8: 
            self.current_frames = self.all_frames[80:83]

        if self.animation_mode == 9: 
            self.current_frames = self.all_frames[84:87]

        if self.animation_mode == 10: 
            self.current_frames = self.all_frames[88:91]

        if self.animation_mode == 11: 
            self.current_frames = self.all_frames[92:95]

        if self.animation_mode == 12: 
            self.current_frames = self.all_frames[96:99]

        if self.animation_mode == 13: 
            self.current_frames = self.all_frames[100:103]

        if self.animation_mode == 14: 
            self.current_frames = self.all_frames[104:109]

        if self.animation_mode == 15: 
            self.current_frames = self.all_frames[110:115]

        if self.animation_mode == 16: 
            self.current_frames = self.all_frames[116:119]

        if self.animation_mode == 17: 
            self.current_frames = self.all_frames[120:123]
    
        return self.current_frames

    
    def update_player_frame (self): #math for frame indexing
        self.animation_count += 1

        if self.current_frames == None or self.current_frames == []:
            return self.animation_mode

        if self.animation_mode == 0: 
            self.frame_index = (self.animation_count // 5) % len(self.current_frames)

        if self.animation_mode == 1: 
            self.frame_index = (self.animation_count // 5) % len(self.current_frames)

        if self.animation_mode == 2: 
            if self.attacking:
                self.frame_index = (self.attack_count // 5) % len(self.current_frames)

        if self.animation_mode == 3: 
            if self.attacking:
                self.frame_index = (self.attack_count // 5) % len(self.current_frames)

        if self.animation_mode == 4: 
            self.frame_index = (self.animation_count // 15) % len(self.current_frames)

        if self.animation_mode == 5: 
            self.frame_index = (self.animation_count // 15) % len(self.current_frames)

        if self.animation_mode == 6: 
            self.frame_index = (self.attack_count // 5) % len(self.current_frames)

        if self.animation_mode == 7: 
            self.frame_index = (self.attack_count // 5) % len(self.current_frames)

        if self.animation_mode == 8: 
            self.frame_index = (self.attack_count // 5) % len(self.current_frames)

        if self.animation_mode == 9: 
            self.frame_index = (self.attack_count // 5) % len(self.current_frames)

        if self.animation_mode == 10: 
            self.frame_index = (self.attack_count // 5) % len(self.current_frames)

        if self.animation_mode == 11: 
            self.frame_index = (self.attack_count // 5) % len(self.current_frames)

        if self.animation_mode == 12: 
            self.frame_index = (self.attack_count // 5) % len(self.current_frames)

        if self.animation_mode == 13: 
            self.frame_index = (self.attack_count // 5) % len(self.current_frames)

        if self.animation_mode == 14: 
            self.frame_index = (self.animation_count // 10) % len(self.current_frames)

        if self.animation_mode == 15: 
            self.frame_index = (self.animation_count // 10) % len(self.current_frames)

        if self.animation_mode == 16: 
            self.frame_index = (self.animation_count // 5) % len(self.current_frames)

        if self.animation_mode == 17: 
            self.frame_index = (self.animation_count // 5) % len(self.current_frames)


    def init_dash(self):

        if self.dash == True: #when you press the button
            if self.dash_charges > 0 and not self.dashing: #if you have a charge and you aren't currenly dashing
                self.dashing = True
                self.dash_charges -= 1
                self.dash_counter = 0

            self.dash = False #lets go of the dash signal basically
        

    def check_cooldown(self):


        #iframes
        if self.dashing is True:
            self.invulnerable == True
        else:
            self.invulnerable == False

        #DASH

        if self.dashing is True:
            self.dash_counter += 1
            if self.dash_counter > 12:
                self.dashing = False
                self.dash_counter = 0

        if self.dash_charges < self.max_dash_charges: 
            self.dash_buffer +=1
            
            if self.dash_buffer > self.max_dash_buffer: #if you wait for the whole cooldown/buffer you receive 1 charge and you have to wait 1 more cycle
                self.dash_charges += 1
                self.dash_buffer = 0




        #ATTACK 
        

        if self.holding_attack is True:
            self.attacking = True

        if self.attacking == True:
            self.attack_count += 1
            self.combo_buffer = 0
        else:#not currently attacking
            if self.attack_count > 0:
                self.combo_buffer += 1 

        #resets combo if takes too long
        if self.combo_buffer > 30:
            self.attack_count = 0
            self.combo_stage = 1
            self.combo_buffer = 0
            self.hit_number = 0
     
        #end cycle 1
        if self.attack_count == 19:
            if not self.holding_attack:
                self.attacking = False
              
         #end cycle 2
        elif self.attack_count == 39:
            if not self.holding_attack:
                self.attacking = False
      
         #end cycle 3
        elif self.attack_count >= 59:
            self.attack_count = 1
            if not self.holding_attack:
                self.attacking = False
                        

        


        #slash 1
        if self.attack_count == 5:
            self.attacked = True
        
            
        #slash 2
        elif self.attack_count == 25:
            self.attacked = True
    

        #slash 3
        elif self.attack_count == 45:
            self.attacked = True



        

        # if self.dashing is True:
        #     self.i_counter += 1*self.dash_counter
        # else:
        #     if self.i_counter < 15:
        #         self.i_counter += 1
        #     else:


        # if self.i_counter > 0:
        #     self.invulnerable = True


   
    def update_attack_hitbox(self):
        # Update attack_rect relative to current direction & frame
        if self.attacking and self.attack_count in (5,25,45):

            face_right = not self.x_flip #if facing right, it will be true

            if self.aim_up:
                if face_right is True:
                    self.attack_rect = pygame.Rect(self.rect.x + 5, self.rect.top - 10, 50, 40)
                else:
                    self.attack_rect = pygame.Rect(self.rect.x - 23, self.rect.top -10, 50, 40)

            elif self.aim_down:
                if face_right is True:
                    self.attack_rect = pygame.Rect(self.rect.x - 20, self.rect.bottom - 15, 68, 36)
                else:
                    self.attack_rect = pygame.Rect(self.rect.x - 10, self.rect.bottom - 15, 68, 36)
            
            else:

                if self.aim_right:
                    self.attack_rect = pygame.Rect(self.rect.right-13, self.rect.y, 40, 32)
                elif self.aim_left:
                    self.attack_rect = pygame.Rect(self.rect.left-27, self.rect.y, 40, 32)
        else:
            self.attack_rect = pygame.Rect(0, 0, 0, 0)
        

    def attack(self,zombie_damaged, zombie_hitbox, player_damage, freeze_frame_counter):
        if self.attack_rect.colliderect(zombie_hitbox) and self.attacked is True:
            print('TAKE THAT')

            self.combo_stage*= self.combo_multipliers[self.hit_number%3] #cycles through the multipliers as the attack goes on
            self.combo_stage = round(self.combo_stage, 3) 
            player_damage = self.base_ATK*(self.combo_stage)
            zombie_damaged = True
            self.attacked = False
            self.hit_landed = True

            if player_damage > self.base_ATK*2: #if damage gets to double what the player is capable of, freeze frame increases
                freeze_frame_counter = 6       
            else:
                freeze_frame_counter = 4

            

        return zombie_damaged, player_damage, freeze_frame_counter


    def calculate_screen_shake(self, player_damage, horizontal_cam_shake, vertical_cam_shake):

        if self.hit_landed is True:

            if self.aim_down is True:
                vertical_cam_shake = (player_damage*2.5)//1.5
            elif self.aim_up is True:
                vertical_cam_shake = -(player_damage*2.5)//1.5

            
            elif self.aim_right is True:
                horizontal_cam_shake = (player_damage*2.5)//1.5
            elif self.aim_left is True:
                horizontal_cam_shake = -(player_damage*2.5)//1.5

            self.hit_landed = False
        else:
            pass

        return horizontal_cam_shake, vertical_cam_shake



    def receive_damage(self, zombie_damage):
            if self.damaged is True:
                if self.invulnerable == False: 
                    self.HP -= zombie_damage
                    self.damaged = False
                    if self.HP > 0:
                        print(f'i have been hit by this filthy zombie for {zombie_damage} and now im {self.HP}. my maxHP is {self.max_HP}')
                    else:
                        print(f'im supposed to be dead')
                else:
                    print('im invulnerable')
                    self.damaged = False
            

    def dead_check(self):
        if self.HP <= 0:
            #death animation/ death screen
            pass
        


            
        
    
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

        x_distance = abs(self.rect.centerx - player_position[0])
        y_distance = abs(self.rect.centery - player_position[1])

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
            self.HP = round(self.HP, 2)
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





