import pygame, sys
from pygame.locals import *
from spritesheet import Spritesheet
from tilemap import *
from perlin_noise import PerlinNoise
from entity import Player, Zombie, zombies
import random
pygame.init()

#grab resolution for the users monitor
resolution = pygame.display.get_desktop_sizes()
#baseline resolution
base_res_x, base_res_y = 640, 360        

display_w , display_h = resolution[0]   #index 0 for the first monitor   
window_w, window_h = 1280,720
screen_state_w, screen_state_h = window_w, window_h

#camera movement
camera_x=0 #made it the same as the player's coordinates
camera_y=0 #made it the same as the player's coordinates
x_camera_delay = 0
y_camera_delay = 0
camera_speed=5 #will make this the difference in current player coordinates 

#base window status
status = RESIZABLE

#1. initiliaze pygame, 2. names the window, 3. sets the window size and sets its paramaters
pygame.display.set_caption("Return To Sender") 
canvas = pygame.Surface((base_res_x, base_res_y))
screen = pygame.display.set_mode((screen_state_w, screen_state_h), status)


clock = pygame.time.Clock() #assigning the clock function to a variable to use for the fps in the gameloop

# *-- MAP STUFF --*
sprites = Spritesheet('spritesheet.png')

tile_size = 32
#16 tiles / chunk
chunk_tiles_x = 16
chunk_tiles_y = 16

chunk_pixel_w = chunk_tiles_x*tile_size
chunk_pixel_h = chunk_tiles_y*tile_size

render_distance = 2
loaded_chunks = {}
set_seed = 123456

#Surface_Level
noise_1d = PerlinNoise(octaves=2, seed = int(set_seed))
#Caves
noise_2d = PerlinNoise(octaves=3, seed = int(set_seed))


def world_to_chunk(world_x,world_y):
    chunk_coordinate_x, chunk_coordinate_y = int(world_x//chunk_pixel_w), int(world_y//chunk_pixel_h)
    return chunk_coordinate_x, chunk_coordinate_y

def generate_chunk_data(chunk_x, chunk_y):
    grid = []
    surface_scale = 0.02
    cave_scale = 0.04
    base_height = 7
    amplitude = 10

    for y in range(chunk_tiles_y):
        row = []
        world_tile_y = chunk_y*chunk_tiles_y + y
        for x in range(chunk_tiles_x):
            world_tile_x = chunk_x*chunk_tiles_x + x

            noise_volume = noise_1d([world_tile_x*surface_scale])
            surface_y = base_height + int(noise_volume*amplitude)

            cave_volume = noise_2d([world_tile_x * cave_scale , world_tile_y * cave_scale])

            depth = world_tile_y - surface_y

            #the depth determines how deep the caves should go
            if depth < 0:
                row.append('-1')
            #surface Layer
            elif depth == 0:
                if cave_volume <= -0.25:
                    row.append('-1')
                else:
                    row.append('1')
            elif depth <4:
                if cave_volume <= -0.22:
                    row.append('-1')
                else:
                    row.append('11')
            #underground Caves
            else:
                cave_threshold = -0.01 + min(0.15, (depth-4)*0.01)

                if depth >20:
                    cave_threshold -= (depth-20)*0.02

                if cave_volume <= cave_threshold:
                    row.append('-1')
                else:
                    row.append('11')
            
                    
        grid.append(row)
    return grid

 
# *-----------------------------------------------------------PLAYER STUFF---------------------------------------------------------------------*

player = Player(
    Name=None,
    rect = pygame.Rect(100, 200, 32, 32),
    movement=[0,0],
    moving_up = False,
    moving_down = False,
    moving_right = False,
    moving_left = False,
    press_space = False,
    aim_up = False,
    aim_down = False,
    aim_right = False,
    aim_left = False,
    y_momentum = 0,
    max_air_jumps = 2,
    jump = False,
    jump_height = 3,
    on_ground = None,
    x_flip = False,
    all_frames = [],
    current_frames = [],
    frame_index = 0,
    animation_mode = 0,
    animation_count = 0,    
    max_HP = 50,
    damaged=False,
    base_ATK=5, 
    attack_dir = None,
    first_hit_count = 0,
    combo_tick = 0,
    combo_stage = 0,
    first_hit_cooldown = 120,
    combo_cooldown = 20,
    combo_window = 0,
    max_combo_window = 25,
    attacking = False,
    attacked = False,
    CRIT_DMG=None, 
    CRIT_CHANCE=None, 
    LEVEL=None, 
    EXP=None, 
    DOLLARS=None, 
    S_COIN=None
)

# *--------------------------------------------ENTITIES-------------------------------------------------------*

#ZOMBIES
choice_count = 0 #stores the amount of frames it has been to make a new choice
zombie_sprite = pygame.image.load('animations/base_zombie.png')



# *------------------------------ANIMATION------------------------------------------------------------------------

jimmy_sheet = Spritesheet('animations/spritesheets/red_jimmy_sheet.png')


# 0-5 idle, 6-10 walk, 11-14 jump, 15-17 fall
# -idle
# LOAD PLAYER ANIMATIONS      
for i in range(6):
    filename = f'idle_{i}'
    player.all_frames.append(jimmy_sheet.parse_sprite(filename))

# -walk
for i in range(5):
    filename = f'walk_{i}'
    player.all_frames.append(jimmy_sheet.parse_sprite(filename))

# -jump
for i in range(4):
    filename = f'jump_{i}'
    player.all_frames.append(jimmy_sheet.parse_sprite(filename))

# -fall
for i in range(3):
    filename = f'fall_{i}'
    player.all_frames.append(jimmy_sheet.parse_sprite(filename))


# 0-5 idle, 6-10 walk, 11-14 jump, 15-17 fall
# 0=idle, 1=walk, 2=jump, 3=fall





#note for rendering: whatever is first rendered in the loop will be behind while whatever is last rendered in the loop will be in the very front
# *--GAME LOOP--*
while True: 



    player.jump = False #resets jump



       # *--INPUT DETECTION--*
    for event in pygame.event.get(): #just detects if any 'events' occur



        # *--QUIT--*
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        # elif player_rect.right>total_map_w or player_rect.top <0 or player_rect.bottom> total_map_h:
        #     pygame.quit()
        #     sys.exit()
        # elif player_rect.left <0:
        #     player_rect.left = 1
        
        # *--KEY DETECTION--*

        # *--WINDOW CONTROLS--*

        if event.type == pygame.MOUSEBUTTONDOWN:
            player.attacking = True
        if event.type == pygame.MOUSEBUTTONUP:
            player.attacking = False

        if event.type == VIDEORESIZE and status == RESIZABLE:
            window_w, window_h = event.w , event.h
            screen_state_w, screen_state_h = window_w, window_h
            screen = pygame.display.set_mode((screen_state_w, screen_state_h),status)

        
        if event.type == KEYDOWN:
            if event.key == K_F1:
                status = RESIZABLE
                screen_state_w, screen_state_h = window_w, window_h
                screen = pygame.display.set_mode((screen_state_w, screen_state_h), status)

            elif event.key == K_F11:
                status = FULLSCREEN
                screen_state_w, screen_state_h = display_w, display_h
                screen = pygame.display.set_mode((display_w,display_h), status)


            # *--KEY PRESSED--*
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w: #pressing W (up)
                player.aim_up = True
            if event.key == pygame.K_s: #pressing S (down)
                player.aim_down = True
            if event.key == pygame.K_d: #pressing D (right)
                player.moving_right = True
                player.aim_right = True
            if event.key == pygame.K_a: #pressing A (left)
                player.moving_left = True
                player.aim_left = True
            if event.key == pygame.K_SPACE:
                player.press_space = True
        


            # *--KEY IS LET GO--*  
        if event.type == pygame.KEYUP:

            if event.key == pygame.K_a and event.key == pygame.K_d and event.key == pygame.K_SPACE: #nothing is being touched
                player.animation_mode = 0  
            if event.key == pygame.K_w: #let go of W (up)
                player.aim_up = False
            if event.key == pygame.K_s:#let go of S (down)
                player.aim_down = False
            if event.key == pygame.K_d: #let go of D (right)
                player.moving_right = False
                player.aim_right = False
            if event.key == pygame.K_a: #let go of A (left)
                player.moving_left = False
                player.aim_left = False
            

    #chunk manager
    position_chunk_x , position_chunk_y = world_to_chunk(player.rect.centerx, player.rect.centery)
    needed_chunks = set()

    for chunk_y in range(position_chunk_y - render_distance, position_chunk_y + render_distance + 1):
        for chunk_x in range (position_chunk_x - render_distance, position_chunk_x + render_distance + 1):
            chunk_key = (chunk_x, chunk_y)
            needed_chunks.add(chunk_key)

            if chunk_key not in loaded_chunks:
                raw_data = generate_chunk_data(chunk_x,chunk_y)
                loaded_chunks[chunk_key] = TileMap(raw_data,sprites, tile_size)

    for chunk_key in list(loaded_chunks.keys()):
        if chunk_key not in needed_chunks:
            del loaded_chunks[chunk_key]

    tile_rect = []
    for (chunk_x,chunk_y), tile_map in loaded_chunks.items():
        chunk_world_x = chunk_x * chunk_pixel_w
        chunk_world_y = chunk_y * chunk_pixel_h
        tile_rect.extend(tile_map.get_rects(chunk_world_x,chunk_world_y))
    # *--------------------------SPAWNING/DESPAWNING ZOMBIES----------------------------------


    #Generating Zombies:

    zombie_count = 1

    if len(zombies) < zombie_count:

        for i in range(zombie_count):
            zombie = Zombie(None, [0,0],0,0,0, False, (0,0), None, '',None, 0, 0, False, False, False,0,45,100, 5)
            zombie.generate_rect(i, position_chunk_x)
            zombies.append(zombie)
            zombie.chase_speed = random.randint(1,3)

    # *---------------------------------------------------------------------------

    # *--PLAYER HORIZONTAL MOVEMENT + COLLISIONS--*

    player.movement = [0,0]  

    #left and right movement
    if player.moving_right == True:
        player.movement[0]= 4
        player.rect.x += player.movement[0]

    if player.moving_left == True:
        player.movement[0]= -4
        player.rect.x += player.movement[0]

    #collisions
    for tile in tile_rect:    
        if player.rect.colliderect(tile):
            if player.movement[0] > 0:
                player.rect.right = tile.left

            if player.movement[0] < 0:
                player.rect.left = tile.right

#---------------------------------------------------------------------

    # *-- PLAYER VERTICAL MOVEMENT + VERTICAL COLLISIONS --*
    
    #PLAYER
    #gravity
    player.movement[1] = player.y_momentum
    
    player.y_momentum += 0.2
    if player.y_momentum > 10:
        player.y_momentum = 10

    if player.y_momentum >= 0 and player.y_momentum <= 1: #checks if player is in the air
        pass
    else:
        player.on_ground = False

    player.rect.y += player.movement[1]

    


    for tile in tile_rect:
        if player.rect.colliderect(tile):
            if player.movement[1] > 0:
                player.rect.bottom = tile.top
                player.y_momentum = 0 # <-- basically tells the game that i can stop falling now
                player.on_ground = True
        
            if player.movement[1] < 0:
                player.rect.top = tile.bottom
                player.y_momentum = 0 # <-- same with this


    #                    *--JUMP--*
    
    #positive y momentum is downward | negative y momentum is upward
    if player.press_space == True:
        if player.on_ground is True: #player touching ground
            player.jump = True
            player.air_jump_count = player.max_air_jumps
        else: #player is in the air
            if player.air_jump_count > 0: #if player has an extra jump, then jump then deduct from remaining jumps
                player.jump = True
                player.air_jump_count -= 1
            else:
                pass
    else:
         pass

    player.press_space = False #just returns it back to the original state so it doesn't infintely jump

    if player.jump == True:
        player.y_momentum = -player.jump_height

#------------------------------------PLAYER ZOMBIE INTERACTION---------------------------------------------------

    #PLAYER ATTACKING ZOMBIES
    zomb_no = 0
    del_zomb = None
    player_damage = 0
    player.check_cooldown()
    for zombie in zombies:
        zombie.damaged, applied_damage = player.attack(zombie.damaged, zombie.rect, player_damage)
        zombie.receive_damage(applied_damage)
        zombie.calculate_knockback(player.mom_force, player.x_flip, player.rect)
        zombie.check_staggered()
        del_zomb = zombie.dead_check(zomb_no)
        if del_zomb is not None:
            zombies.pop(del_zomb)
        zomb_no += 1

        


    #ZOMBIES ATTACKING PLAYER
    for zombie in zombies:
        zombie.touch_player(player.rect)
        if zombie.staggered == False:
            player.damaged = zombie.attack_player(player.HP)
        player.receive_damage(zombie.ATK)

    
    
    
    
    
    
# *---------------------------------------ENTITIES---------------------------------------------------------


    # 60*x frames to tell the game to change what action the zombies should be doing
    choice_count += 1
    if choice_count >= 120: #120 means every 2 seconds since 60x2=120
        choice_count = 0
        change_action = True
    else:
        change_action = False

    #IF 
    if change_action == True:
        for zombie in zombies:
            #determining left and right movement
                action_pool = ['Left', 'Right', 'Still']
                action_weightage = [15,15,70]
                zombie.idle_move = random.choices(action_pool, weights=action_weightage, k=1)[0]
                

    #ZOMBIE HORIZONTAL MOVEMENT

    for zombie in zombies:
        try:#because initially player_render_pos hasn't been defined yet
            zombie.aggro_player(player_render_pos) 
        except NameError:
            pass
    

    
    for zombie in zombies: 
        if zombie.render_pos[0] < position_chunk_x:#freezes movement horizontal movement if zombie isn't in frame
            zombie.idle_move = 'Still'

        zombie.movement = [0,0]

        if abs(zombie.x_push_momentum) > 0:#if there is any X_knockback applied to zombie then apply it

            zombie.x_push_momentum *= 0.85
            
            if abs(zombie.x_push_momentum) < 0.1: #if its near 0, its negligible so make it zero
                zombie.x_push_momentum = 0 
            else:
                zombie.movement[0] = zombie.x_push_momentum
                zombie.rect.x += zombie.movement[0]

        else:


            if zombie.staggered == False: #if zombie is not staggered
                if zombie.chase_player == True: #chase player

                    try:
                        if zombie.render_pos > player_render_pos:
                            zombie.movement[0] = -zombie.chase_speed
                            zombie.rect.x += zombie.movement[0]

                        if zombie.render_pos < player_render_pos:
                            zombie.movement[0] = zombie.chase_speed
                            zombie.rect.x += zombie.movement[0]
                            
                    except NameError:
                        pass



                else: #idle movement

                    speed_pool = [1, 2, 3]
                    speed_weightage = [70,25,5]
                    random_zomb_speed = random.choices(speed_pool, weights=speed_weightage, k=1)[0]    
                    
                    #move right
                    if zombie.idle_move == 'Right':
                        zombie.movement[0] = random_zomb_speed
                        zombie.rect.x += zombie.movement[0]

                    #move left
                    if zombie.idle_move == 'Left':
                        zombie.movement[0] = -random_zomb_speed
                        zombie.rect.x += zombie.movement[0]

                    #dont move
                    if zombie.idle_move == 'Still':
                        pass
            else: #if zombie is staggered
                zombie.movement = [0,0]
            
    #HORIZONTAL KNOCKBACK CODE



    #ZOMBIE HORIZONTAL COLLISIONS
    for tile in tile_rect:    
        for zombie in zombies:
            if zombie.rect.colliderect(tile):
                if zombie.movement[0] > 0:
                    zombie.rect.right = tile.left

                if zombie.movement[0] < 0:
                    zombie.rect.left = tile.right
            
    #ZOMBIE VERTICAL MOVEMENT AND GRAVITY + VERTICAL COLLISION



    for zombie in zombies:

        if abs(zombie.y_push_momentum) > 0: #if there is any Y_knockback applied to zombie then apply it

            zombie.y_push_momentum *= 0.85
            
            if abs(zombie.y_push_momentum) < 0.1: #if its near 0, its negligible so make it zero
                zombie.y_push_momentum = 0 
            else:
                zombie.movement[1] = zombie.y_push_momentum
                zombie.rect.y += zombie.movement[1]


        zombie.movement[1] = zombie.y_momentum
        zombie.y_momentum += 0.2
        if zombie.y_momentum > 4.5:
            zombie.y_momentum = 4.5
        

        if zombie.y_momentum >= 0 and zombie.y_momentum <= 1: #checks if zombie is in the air
            pass
        else:
            zombie.on_ground = False

        zombie.rect.y += zombie.movement[1]



        
        for tile in tile_rect:
            if zombie.rect.colliderect(tile):
                if zombie.movement[1] > 0:
                    zombie.rect.bottom = tile.top
                    zombie.y_momentum = 0 # <-- basically tells the game that the zombie can stop falling now
                    zombie.on_ground = True
            
                if zombie.movement[1] < 0:
                    zombie.rect.top = tile.bottom
                    zombie.y_momentum = 0 # <-- same with this


                                # *--ANIMATION--*
 #-----------------------------------------------------------------------------------------------------
    #chooses what type of action the player is doing to then determine animation playing

    if player.on_ground == False and player.y_momentum > 0: #falling animation
        player.animation_mode = 3
    elif player.on_ground == False and player.y_momentum <= 0: #jumping animation
        player.animation_mode = 2
    elif player.moving_right or player.moving_left:
        player.animation_mode = 1
    else: #idle
        player.animation_mode = 0


                                # *--RENDERING--*
 #----------------------------------------------------------------------------------------------------------

    # void
    if player.rect.y > 2000:
        player.rect.x, player.rect.y = 250,100
        player.y_momentum = 0


    # *--CAMERA MOVEMENT--*
    #these 2 centers the player within the base canvas
    camera_x = player.rect.centerx - (base_res_x // 2) 
    camera_y = player.rect.centery - (base_res_y // 2)

     #map clamping      
    # max_cam_x = total_map_w - base_res_x
    # max_cam_y = total_map_h - base_res_y

    # camera_x = max(0, min(camera_x, max_cam_x))
    # camera_y = max(0, min(camera_y, max_cam_y))



    canvas.fill((159, 215, 255))    #nice sky background
    # current_y= 0

    # #filtering through the top and bottom layer in maps
    # for row in maps:            
    #     current_x = 0
    #     #filtering through each screen in each layer
    #     for tile_map in row:
    #         #drawing the map with respect to each offset
    #         tile_map.draw_map(canvas, camera_x, camera_y, offset_x = current_x, offset_y = current_y)
    #         #updating x offset
    #         current_x += tile_map.map_w
    #     #updating y offset
    #     current_y += row[0].map_h

    #X camera delay
    if abs(player.movement[0]) > 0:
        if player.movement[0] > 0: #if player moving right
            if x_camera_delay < 0: #if player was previously moving left
                x_camera_delay += 0.8 
            else:
                x_camera_delay += 0.4 #if from 0
                if x_camera_delay >= 20:
                    x_camera_delay = 20

        if player.movement[0] < 0:#if player moving left
            if x_camera_delay > 0:#if player was previously moving right
                x_camera_delay -= 0.8
            else:
                x_camera_delay -= 0.4 #if from 0
                if x_camera_delay <= -20:
                    x_camera_delay = -20
    else:
        if x_camera_delay > 0: #if player isn't moving then revert back to original
            x_camera_delay -= 1.0
            if x_camera_delay <= 0:
                x_camera_delay = 0

        if x_camera_delay < 0: #same with this
            x_camera_delay += 1.0
            if x_camera_delay >= 0:
                x_camera_delay = 0

    
    #Y camera delay
    if not player.on_ground and abs(player.movement[1]) > 0:
        if player.movement[1] > 0: #if player moving down
            if y_camera_delay < 0: #if player was previously moving up
                y_camera_delay += 0.8 
            else:
                y_camera_delay += 0.4 #if from 0
                if y_camera_delay >= 20:
                    y_camera_delay = 20

        if player.movement[1] < 0:#if player moving up
            if y_camera_delay > 0:#if player was previously moving down
                y_camera_delay -= 0.8
            else:
                y_camera_delay -= 0.4 #if from 0
                if y_camera_delay <= -20:
                    y_camera_delay = -20
    else:
        if y_camera_delay > 0: #if player isn't moving then revert back to original
            y_camera_delay -= 1.0
            if y_camera_delay <= 0:
                y_camera_delay = 0

        if y_camera_delay < 0: #same with this
            y_camera_delay += 1.0
            if y_camera_delay >= 0:
                y_camera_delay = 0




    for (chunk_x,chunk_y), tile_map in loaded_chunks.items():
        chunk_world_x = chunk_x *chunk_pixel_w
        chunk_world_y = chunk_y * chunk_pixel_h
        tile_map.draw_map(canvas, (camera_x + x_camera_delay), (camera_y + y_camera_delay) ,offset_x=chunk_world_x,offset_y=chunk_world_y)
    #                                        ^positive map delay           ^


     
    
    player_render_pos = ((player.rect.x - camera_x) - x_camera_delay, (player.rect.y - camera_y) - y_camera_delay) #centers player on screen
    #                                                                                                   ^negative camera delay
    #zombie render code
    for zombie in zombies:
        zombie.render_pos = ((zombie.rect.x - camera_x) - x_camera_delay, (zombie.rect.y - camera_y) - y_camera_delay)
    #                                                                                                   ^negative camera delay
        #disables zombie gravity if out of range
        if zombie.render_pos[0] < position_chunk_x:
            zombie.y_momentum = 0

    #flipping code
    
    #player
    if player.moving_left == True:
        player.x_flip = True
    elif player.moving_right == True:
        player.x_flip = False
    else:
         pass  

    #zombies
    for zombie in zombies:
        if zombie.movement[0] > 0:
            zombie.x_flip = False
        elif zombie.movement[0] < 0:
            zombie.x_flip = True
        else:
            zombie.x_flip = False

 
    player.current_frames = player.update_action() #determines the current type of animation playing
    player.update_player_frame() #update frame played
    player_sprite = player.current_frames[player.frame_index] #determines the image/sprite which will be displayed on player pos
    canvas.blit(pygame.transform.flip(player_sprite, player.x_flip, False), player_render_pos) 


    for zombie in zombies:
        canvas.blit(pygame.transform.flip(zombie_sprite, zombie.x_flip, False), (zombie.render_pos))
    

     

    #^^ draws the player onto the location of its hitbox*
    # x_flip tells the game whether it should flip the direction of the sprite on the x axis or not.
    # all sprites are all originally drawn to the right side.


    #scale the screen
    scaled_resolution = pygame.transform.scale(canvas, (screen_state_w, screen_state_h))

    screen.blit(scaled_resolution,(0,0))   #creates a window to be displayed

    pygame.display.update() #updates the screen
    clock.tick(60) #ensures framerate is consistently 60fps

