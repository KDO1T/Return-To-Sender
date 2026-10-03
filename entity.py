import pygame, sys, random


class Player:
    # *--STATS--*
    #level is the player's level, while exp is what the player gains to increase in level
    #dollars is the money the player gains throughout runs while s_coin (soul coins) is the metacurrency
    def __init__(self, Name,rect,attack_rect,critical_rect, movement,moving_up,moving_down ,moving_right ,moving_left,dash, dashing,dash_dis,dash_counter, 
                 hor_aim_list, holding_up, holding_down, vert_aim_list, aim_up,aim_down, dash_charges,max_dash_buffer,dash_buffer, 
                 max_dash_charges, aim_right, aim_left, press_space,y_momentum,x_momentum, max_air_jumps,jump,jump_height,on_ground,x_flip,
                   all_frames ,current_frames ,frame_index, animation_mode,animation_count,max_HP,i_counter,invulnerable, damaged,base_ATK,attacking,
                     holding_attack,attack_count,combo_stage, hit_landed, combo_buffer, zombies_hit, active_perks,
                    CRIT_DMG, CRIT_CHANCE, LEVEL, EXP, DOLLARS, S_COIN):
        self.Name = Name
        self.rect = rect
        self.attack_rect = attack_rect #contains hitbox for each attack
        self.critical_rect = critical_rect #contains smaller hitbox that if the player manages to hit, will boost his damage/knockback
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
        self.mom_force = 10 #the momentum the player applies to zombies when knocking them back
        self.attacking = attacking
        self.holding_attack = holding_attack
        self.attack_count = attack_count
        self.combo_stage = 1
        self.combo_multipliers = [1.0025,1.002,1.003]
        self.hit_landed = hit_landed 
        self.hit_number = 0
        self.zombies_hit = []
        self.combo_buffer = combo_buffer #time between each slash of the combo
        self.active_perks = active_perks
        self.CRIT_DMG = CRIT_DMG
        self.CRIT_CHANCE = CRIT_CHANCE
        self.LEVEL = LEVEL
        self.EXP = EXP 
        self.DOLLARS = DOLLARS
        self.S_COIN = S_COIN

        # *--SKILL TREE--*
        # Filled in by skill_tree.apply_skill_effects(). The defaults below mean "no upgrades".
        self.skill_tree_purchased = []      #ids of purchased skills (saved per save slot)
        self.ranged_unlocked = False        #becomes True when the final boss is defeated
        self.base_move_speed = 4
        self.move_speed = 4                 #pixels per frame, used by main.py
        self.damage_mult = 1.0
        self.crit_chance_bonus = 0.0
        self.crit_dmg_bonus = 0.0
        self.damage_reduction = 0.0
        self.knockback_resist = 0.0         #no player knockback exists yet, ready for when it does
        self.bonus_max_HP = 0               #max HP that comes from the skill tree (not saved as base)

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

        # if self.animation_mode == 18:
        #     self.current_frames = self.all_frames[123:124]

        # if self.animation_mode == 19:
        #     self.current_frames = self.all_frames[124:125]    

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

        # if self.animation_mode == 18:
        #     self.frame_index = 0

        # if self.animation_mode == 19: 
        #     self.frame_index = 0


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
            self.invulnerable = True
        else:
            self.invulnerable = False

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
                        
        # #slash 1
        # if self.attack_count == 5:
        #     self.attacked = True
        
            
        # #slash 2
        # elif self.attack_count == 25:
        #     self.attacked = True
    

        # #slash 3
        # elif self.attack_count == 45:
        #     self.attacked = True

        # ^^ use the hitbox as a better way of timing the attacks instead of using self.attacked



   
    def update_attack_hitbox(self):

        #booleans if for when each swings are playing
        swing_1_active_window = 5 <= self.attack_count <= 10  
        swing_2_active_window = 25 <= self.attack_count <= 30 
        swing_3_active_window = 45 <= self.attack_count <= 50

        # Update attack_rect relative to current direction & frame
        if self.attacking and self.attack_count in (5,25,45):
            self.zombies_hit.clear()

        face_right = not self.x_flip #if facing right, it will be true

        if self.attacking and (swing_1_active_window or swing_2_active_window or swing_3_active_window):
            if self.aim_up:
                if face_right is True:
                    self.attack_rect = pygame.Rect(self.rect.x + 5, self.rect.top - 10, 50, 40)
                else:
                    self.attack_rect = pygame.Rect(self.rect.x - 23, self.rect.top -10, 50, 40)


            elif self.aim_down and not self.on_ground :
                if face_right is True:
                    self.critical_rect = pygame.Rect(self.rect.x +3 , self.rect.bottom + 5, 20,15)
                    self.attack_rect = pygame.Rect(self.rect.x - 20, self.rect.bottom - 15, 68, 36)
                else:
                    self.critical_rect = pygame.Rect(self.rect.x +11, self.rect.bottom + 5, 20,15)
                    self.attack_rect = pygame.Rect(self.rect.x - 10, self.rect.bottom - 15, 68, 36)
            
            else:

                if self.aim_right:
                    self.attack_rect = pygame.Rect(self.rect.right-13, self.rect.y, 40, 32)
                elif self.aim_left:
                    self.attack_rect = pygame.Rect(self.rect.left-27, self.rect.y, 40, 32)
        else:
            self.attack_rect = None
            self.critical_rect = None
        

    def attack(self,zombie_list, freeze_frame_counter):

        if self.attack_rect == None: #if the attack hitbox hasnt been activated then don't run this function
            return 0, freeze_frame_counter#<-- return 0 player_damage

        player_damage = 0 #<-- reset the damage before every attack

        #instead of looping in the main code, we loop through all the zombies within the function itself
        for zombie in zombie_list:
            if self.attack_rect.colliderect(zombie.rect):
                if zombie not in self.zombies_hit: #if the zombies arent in the most recently hit then function normally or else ignore to prevent double damaging

                    #Damage Calculation:

                    #Combo multiplier
                    self.combo_stage*= self.combo_multipliers[self.hit_number%3] #cycles through the multipliers as the attack goes on
                    self.combo_stage = round(self.combo_stage, 3) 

                    #External multiplier
                    print(self.combo_stage)
                    print(self.damage_mult)
                    player_damage =(self.base_ATK or 0) * self.damage_mult * (self.combo_stage)
                    print(player_damage)
                    
                    #Crit multiplier
                    crit_chance = (self.CRIT_CHANCE if self.CRIT_CHANCE is not None else 0.05) + self.crit_chance_bonus
                    crit_damage = (self.CRIT_DMG if self.CRIT_DMG is not None else 1.5) + self.crit_dmg_bonus
                    if random.random() < crit_chance:
                        player_damage *= crit_damage

                    zombie.damaged = True
                    self.hit_landed = True
                    zombie.receive_damage(player_damage)
     
            
                    print(f'damaged for {player_damage}!')
                   

                    zombie.calculate_knockback(self.aim_up,self.aim_down, self.x_flip, self.rect, self.on_ground, self.mom_force, self.attack_count)
                    self.zombies_hit.append(zombie)
                    freeze_frame_counter = 2

                    if self.critical_rect == None:
                        return player_damage, freeze_frame_counter
                    else:
                        if self.critical_rect.colliderect(zombie.head_rect):
                            freeze_frame_counter = 5     
                            self.y_momentum = -3
                        
        
        return player_damage, freeze_frame_counter

        # if self.attack_rect.colliderect(zombie_hitbox) and self.attacked is True:
        #     print('TAKE THAT')

        #     self.combo_stage*= self.combo_multipliers[self.hit_number%3] #cycles through the multipliers as the attack goes on
        #     self.combo_stage = round(self.combo_stage, 3) 
        #     player_damage = self.base_ATK*(self.combo_stage)
        #     zombie_damaged = True
        #     self.attacked = False
        #     self.hit_landed = True

        #     if self.critical_rect.colliderect(zombie_head_hitbox):
        #         freeze_frame_counter = 5     
        #         self.y_momentum = -3
        #     else:
        #         freeze_frame_counter = 3


            

        # return zombie_damaged, player_damage, freeze_frame_counter

        

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



    def receive_damage(self, zombie_damage, freeze_frames):
        if self.damaged is True:
            self.damaged = False
            if self.invulnerable == False: 
                zombie_damage = max(1, round(zombie_damage * (1 - self.damage_reduction)))
                print(zombie_damage)
                print('HP:', self.HP)
                self.HP -= zombie_damage
             
                freeze_frames = 2  
                if self.HP > 0:
                    print(f'i have been hit by this filthy zombie for {zombie_damage} and now im {self.HP}. my maxHP is {self.max_HP}') 
               
                else:
                    print(f'im supposed to be dead')


                

            else:
                print('im invulnerable')
                self.damaged = False

        return freeze_frames
        

    def dead_check(self, stage_position, stage_min_chunk_x, chunk_pixel_w):
        if self.HP <= 0:
            print('you dead')
            # self.DOLLARS = 0
            # self.active_perks = []
            # stage_position = 1
            # self.rect.x = (stage_min_chunk_x + 1)*chunk_pixel_w + 64
            # self.rect.y = 100
            
            # return stage_position
            # #reset map position
        #     #reset dollars
        #     #reset perks
        #     #reset everything except soul coins
        #     #death animation/ death screen
        return stage_position
        
    
zombies = []
#stores each zombie's attributes within the Zombie class

class Zombie:

    def __init__(self, rect,current_frames,animation_mode, frame_index, animation_count, head_rect, movement, x_push_momentum,
                  y_push_momentum, y_momentum, x_flip, render_pos, on_ground, idle_move, chase_player, chase_speed ,
                 attack_count, player_touch_cooldown, touched_player, knocked, damaged, staggered,stag_count,max_stag_count, HP, ATK):
        self.rect = rect
        self.current_frames = current_frames
        self.animation_mode = animation_mode
        self.frame_index = frame_index
        self.animation_count = animation_count
        self.head_rect = head_rect
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
        self.player_touch_cooldown = player_touch_cooldown
        self.touched_player = touched_player
        self.knocked = knocked
        self.damaged = damaged
        self.staggered = staggered
        self.stag_count = stag_count
        self.max_stag_count = max_stag_count
        self.HP = HP
        self.ATK = ATK




    def generate_head_rect(self):
        head_height = int(self.rect.height * 0.10)
        return pygame.Rect(self.rect.x, self.rect.y, 15, head_height)

    def update_head_rect(self):
        self.head_rect.x = self.rect.x + 8
        self.head_rect.y = self.rect.y

    def aggro_player(self, player_position):

        x_distance = abs(self.rect.centerx - player_position[0])
        y_distance = abs(self.rect.centery - player_position[1])

        if x_distance <=256 and y_distance <= 128:
            self.chase_player = True 
        else:
            self.chase_player = False
            
    def touch_player(self, player_hitbox):
        if self.rect.colliderect(player_hitbox):
            self.touched_player = True
        else:
            self.touched_player = False

    def check_cooldown(self):
        if self.touched_player == True:
            self.attack_count += 1
            self.player_touch_cooldown = 0
        else:
            if self.attack_count > 0: #if the zombie was in the process of attacking the player but was interrupted
                self.player_touch_cooldown += 1

        if self.player_touch_cooldown > 30:
            self.attack_count = 0
    
    def attack_player(self, player_damaged): 
        
        if self.attack_count == 37:  #the zombie hits the player at the end of the 4th frame    
            player_damaged = True
            return player_damaged


        if self.attack_count >= 60:         
            self.attack_count = 0
            return True
        return False

    def receive_damage(self, player_damage):
        if self.damaged == True:
            self.HP -= player_damage
            self.HP = round(self.HP, 2)
            print(f'you hurt me bruh, im now {self.HP}')
            if not self.staggered:
                self.attack_count = 0  # Reset attack only once upon being hit
                self.animation_count = 0
            self.damaged = False
            self.staggered = True
            self.knocked = True

    def dead_check(self, zomb_index):
        if self.HP <= 0:
            return zomb_index



    def calculate_knockback(self, up_force,down_force, player_x_direction, player_rect, mid_air, player_force, player_attack_count):

        if self.knocked == True:

            if not mid_air: #air knockback 

                if up_force == True:
                    if player_x_direction == False: #facing right
                        # self.rect.bottomleft = player_rect.topright
                        self.x_push_momentum += player_force//5
                        self.y_push_momentum += -player_force*1.5


                    elif player_x_direction == True: #facing left
                        # self.rect.bottomright = player_rect.topleft
                        self.x_push_momentum -= player_force//5
                        self.y_push_momentum += -player_force*1.5


        
                elif down_force == True:
                    if player_x_direction == False: #facing right
                        # self.rect.topleft = player_rect.bottomright
                        self.x_push_momentum += 0
                        self.y_push_momentum -= player_force//2

                    elif player_x_direction == True: #facing left
                        # self.rect.topright = player_rect.bottomleft
                        self.x_push_momentum += 0
                        self.y_push_momentum -= player_force//2
                    
                    
                else: #horizontal
                    if player_x_direction == False: #facing right
                        # self.rect.bottomleft = player_rect.midright
                        if player_attack_count >= 45: #light up, light side --> light-to-medium up, light side --> little up, a lot of side
                            self.x_push_momentum += player_force*2
                            self.y_push_momentum += -player_force//2

                        elif player_attack_count >= 25:
                            self.x_push_momentum += player_force//6
                            self.y_push_momentum += -player_force//1.2


                        elif player_attack_count >= 5: #light up, light side --> light-to-medium up, light side --> little up, a lot of up
                            self.x_push_momentum += player_force//4
                            self.y_push_momentum += -player_force*1.2



                    elif player_x_direction == True: #facing left
                        # self.rect.bottomright = player_rect.midleft
                        if player_attack_count >= 45: #light up, light side --> light-to-medium up, light side --> little up, a lot of side
                            self.x_push_momentum -= player_force*2
                            self.y_push_momentum += -player_force//2

                        elif player_attack_count >= 25:
                            self.x_push_momentum -= player_force//6
                            self.y_push_momentum += -player_force//1.2


                        elif player_attack_count >= 5: #light up, light side --> light-to-medium up, light side --> little up, a lot of up
                            self.x_push_momentum -= player_force//4
                            self.y_push_momentum += -player_force*1.2
                        
        
            else: #ground knockback
    
                if up_force == True:
                    if player_x_direction == False: #facing right
                        self.rect.bottomleft = player_rect.midright
                        self.x_push_momentum += player_force//4
                        self.y_push_momentum += -player_force


                    elif player_x_direction == True: #facing left
                        self.rect.bottomright = player_rect.midleft
                        self.x_push_momentum -= player_force//4
                        self.y_push_momentum += -player_force

    
                else: #horizontal
                    if player_x_direction == False: #facing right
                        if player_attack_count >= 45: #light up, light side --> light-to-medium up, light side --> little up, a lot of side
                            self.x_push_momentum += player_force*2
                            self.y_push_momentum += -player_force*1.5

                        elif player_attack_count >= 25:
                            self.x_push_momentum += player_force//6
                            self.y_push_momentum += -player_force//1.2


                        elif player_attack_count >= 5: #light up, light side --> light-to-medium up, light side --> little up, a lot of up
                            self.rect.left = player_rect.right
                            self.x_push_momentum += player_force//4
                            self.y_push_momentum += -player_force


                    elif player_x_direction == True: #facing left 
                        if player_attack_count >= 45: #light up, light side --> light-to-medium up, light side --> little up, a lot of side
                            self.x_push_momentum -= player_force*2
                            self.y_push_momentum += -player_force*1.5

                        elif player_attack_count >= 25:
                            self.x_push_momentum -= player_force//6
                            self.y_push_momentum += -player_force//1.2


                        elif player_attack_count >= 5: #light up, light side --> light-to-medium up, light side --> little up, a lot of up
                            self.rect.right = player_rect.left
                            self.x_push_momentum -= player_force//4
                            self.y_push_momentum += -player_force




            self.knocked = False

    def check_staggered(self):
        if self.staggered is True:
            self.stag_count += 1

        if self.stag_count >= self.max_stag_count: #staggered for how long the zombie should be staggered for (base duration is 45 aka 3/4 sec)
            self.staggered = False
            self.stag_count = 0
    


    def update_action (self, all_frames):
        
        if self.animation_mode == 0: 
            self.current_frames = all_frames[0:1]

        if self.animation_mode == 1: 
            self.current_frames = all_frames[1:3]

        if self.animation_mode == 2: 
            self.current_frames = all_frames[4:6]
        
        if self.animation_mode == 3: 
            self.current_frames = all_frames[7:9]

        if self.animation_mode == 4: 
            self.current_frames = all_frames[10:12]

        if self.animation_mode == 5: 
            self.current_frames = all_frames[13:17]

        if self.animation_mode == 6: 
            self.current_frames = all_frames[18:22]


        return self.current_frames

    
    def update_zombie_frame (self): #math for frame indexing
        
        self.animation_count += 1

        if self.current_frames == None or self.current_frames == []:
            return self.animation_mode

        if self.animation_mode == 0: #idle
            self.frame_index = 0

        if self.animation_mode == 1: #walk right 
            self.frame_index = (self.animation_count // 20) % len(self.current_frames)

        if self.animation_mode == 2: #walk left
            self.frame_index = (self.animation_count // 20) % len(self.current_frames)

        if self.animation_mode == 3: #chase right
            self.frame_index = (self.animation_count // 20) % len(self.current_frames)

        if self.animation_mode == 4: #chase left
            self.frame_index = (self.animation_count // 20) % len(self.current_frames)

        if self.animation_mode == 5: #attack right
            self.frame_index = (self.animation_count // 12) % len(self.current_frames)

        if self.animation_mode == 6: #attack left
            self.frame_index = (self.animation_count // 12) % len(self.current_frames)




class Orb:
    def __init__(self, rect, guaranteed=False, chance=0.5):
        self.rect = rect
        self.guaranteed = guaranteed
        self.chance = chance
        self.consumed = False

    def draw(self, surface, camera_x, camera_y, x_camera_delay, y_camera_delay):
        render_x = self.rect.x - camera_x - x_camera_delay
        render_y = self.rect.y - camera_y - y_camera_delay

        # Outer ring
        color = (255, 215, 0) if self.guaranteed else (180, 100, 255)
        pygame.draw.circle(surface, color, (int(render_x + 8), int(render_y + 8)), 10, 2)
        # Inner solid glowing core
        pygame.draw.circle(surface, (255, 255, 255), (int(render_x + 8), int(render_y + 8)), 6)