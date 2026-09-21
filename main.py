import pygame, sys
from pygame.locals import *
from spritesheet import Spritesheet
from tilemap import *
from player import Player, Player_Sprite
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
map_grid = [['screenR1C1.csv', 'screenR1C2.csv','screenR1C3.csv'],
            ['screenR2C1.csv','screenR2C2.csv','screenR2C3.csv']] #passes the csv file and the png file into the map variable

maps = [[TileMap(file,sprites) for file in row] for row in map_grid]            #puts all row files in map_grid into a list, and putting all maps from the list into maps

#combine both map (top and bottom)
total_map_w = sum(tile_maps.map_w  for tile_maps in maps[0])   #loops through maps list
total_map_h = sum(row[0].map_h for row in maps)

 
# *-----------------------------------------------------------PLAYER STUFF---------------------------------------------------------------------*

player = Player(
    Name=None,
    HP=None,    
    ATK=None, 
    CRIT_DMG=None, 
    CRIT_CHANCE=None, 
    LEVEL=None, 
    EXP=None, 
    DOLLARS=None, 
    S_COIN=None
)






moving_up = False
moving_down = False
moving_right = False
moving_left = False

player_y_momentum = 0 # <-- gravity enacted on the player
press_space = False
max_air_jumps = 2
air_jumps = max_air_jumps
on_ground = None
x_flip = False

# *--------------------------------------------ENTITIES-------------------------------------------------------*



#stores the rect of the zombies
zombies = []
#to use later for rendering pos
zombies_render_positions = [] #acts the same as player render pos.
zombies_movements = [] #holds the x and y values for zombie movement
zombie_ground_check = [] #holds boolean if zombie is in the air or not
zombies_y_momentums = []
zombie_y_momentum = 0

for i in range(10):
    zombie = pygame.Rect(i*128, 200, 32,32)
    zombies.append(zombie)




zombie_sprite = pygame.image.load('animations/base_zombie.png')



# *--------------------------------------------------------------------------------------------------------*

# *--TILES OBJECTS--*
tile_rect = []
current_y = 0
for row in maps:    
    current_x = 0
    for tile_map in row:
        # Fetch rects offset by their section's x and y world positions
        section_rects = tile_map.get_rects(current_x, current_y)
        tile_rect.extend(section_rects)
        
        current_x += tile_map.map_w
    current_y += row[0].map_h

# *------------------------------ANIMATION------------------------------------------------------------------------

jimmy_sheet = Spritesheet('animations/spritesheets/red_jimmy_sheet.png')

jimmy_frames = []
current_frames = []
index = 0
mode = 0
count = 0

# 0-5 idle, 6-10 walk, 11-14 jump, 15-17 fall
# -idle       
for i in range(6):
    filename = f'idle_{i}'
    jimmy_frames.append(jimmy_sheet.parse_sprite(filename))

# -walk
for i in range(5):
    filename = f'walk_{i}'
    jimmy_frames.append(jimmy_sheet.parse_sprite(filename))

# -jump
for i in range(4):
    filename = f'jump_{i}'
    jimmy_frames.append(jimmy_sheet.parse_sprite(filename))

# -fall
for i in range(3):
    filename = f'fall_{i}'
    jimmy_frames.append(jimmy_sheet.parse_sprite(filename))


# 0-5 idle, 6-10 walk, 11-14 jump, 15-17 fall
# 0=idle, 1=walk, 2=jump, 3=fall

def update_action (mod):

    if mod == 0: #idle
        current_frames = jimmy_frames[0:5]

    if mod == 1: #walk
        current_frames = jimmy_frames[6:10]

    if mod == 2: #jump
        current_frames = jimmy_frames[11:14]

    if mod == 3: #fall
        current_frames = jimmy_frames[15:17]

    return current_frames


def update_player_frame (mod, frame, tick): #math for frame 
    tick += 1

    if tick == 60:
        tick = 0

    if mod == 0: #idling
        frame = (tick // 10) % len(current_frames)

    if mod == 1: #walking
        frame = (tick // 12) % len(current_frames)
        
    if mod == 2: #jumping
        frame = (tick // 15) % len(current_frames)
        
    if mod == 3: #falling
        frame = (tick // 20) % len(current_frames)

    return tick, frame


player_rect = pygame.Rect(100, 200, 32, 32) #player hitbox
#                                   ^^  ^^ change this number to alter player hitbox



#note for rendering: whatever is first rendered in the loop will be behind while whatever is last rendered in the loop will be in the very front
# *--GAME LOOP--*
while True: 



    jump = False
        



       # *--INPUT DETECTION--*
    for event in pygame.event.get(): #just detects if any 'events' occur



        # *--QUIT--*
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif player_rect.right>total_map_w or player_rect.top <0 or player_rect.bottom> total_map_h:
            pygame.quit()
            sys.exit()
        elif player_rect.left <0:
            player_rect.left = 1
        
        # *--KEY DETECTION--*

        # *--WINDOW CONTROLS--*
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
            if event.key == pygame.K_d: #pressing D (right)
                moving_right = True
            if event.key == pygame.K_a: #pressing A (left)
                moving_left = True
            if event.key == pygame.K_SPACE:
                press_space = True


            # *--KEY IS LET GO--*  
        if event.type == pygame.KEYUP:

            if event.key == pygame.K_a and event.key == pygame.K_d and event.key == pygame.K_SPACE: #nothing is being touched
                mode = 0  
            if event.key == pygame.K_w:#let go of W (up)
                moving_up = False
            if event.key == pygame.K_s:#let go of S (down)
                moving_down = False
            if event.key == pygame.K_d: #let go of D (right)
                moving_right = False
            if event.key == pygame.K_a: #let go of A (left)
                moving_left = False

    # *---------------------------------------------------------------------------

    # *--PLAYER HORIZONTAL MOVEMENT + COLLISIONS--*

    player_movement = [0,0]  

    #left and right movement
    if moving_right == True:
        player_movement[0]= 4
        player_rect.x += player_movement[0]

    if moving_left == True:
        player_movement[0]= -4
        player_rect.x += player_movement[0]

    #collisions
    for tile in tile_rect:    
        if player_rect.colliderect(tile):
            if player_movement[0] > 0:
                player_rect.right = tile.left

            if player_movement[0] < 0:
                player_rect.left = tile.right

#---------------------------------------------------------------------

    # *-- PLAYER VERTICAL MOVEMENT + VERTICAL COLLISIONS --*
    
    #PLAYER
    #gravity
    player_movement[1] = player_y_momentum
    
    player_y_momentum += 0.2
    if player_y_momentum > 10:
        player_y_momentum = 10

    if player_y_momentum >= 0 and player_y_momentum <= 1: #checks if player is in the air
        pass
    else:
        on_ground = False

    player_rect.y += player_movement[1]

    


    for tile in tile_rect:
        if player_rect.colliderect(tile):
            if player_movement[1] > 0:
                player_rect.bottom = tile.top
                player_y_momentum = 0 # <-- basically tells the game that i can stop falling now
                on_ground = True
        
            if player_movement[1] < 0:
                player_rect.top = tile.bottom
                player_y_momentum = 0 # <-- same with this


    #                    *--JUMP--*
    
    #positive y momentum is downward | negative y momentum is upward
    if press_space == True:
        if on_ground is True: #player touching ground
            jump = True
            air_jumps = max_air_jumps
        else: #player is in the air
            if air_jumps > 0: #if player has an extra jump, then jump then deduct from remaining jumps
                jump = True
                air_jumps -= 1
            else:
                pass
    else:
         pass

    press_space = False #just returns it back to the original state so it doesn't infintely jump

    if jump == True:
        player_y_momentum = -4.5

# *---------------------------------------ENTITIES---------------------------------------------------------


    #ZOMBIE MOVEMENT
    zombies_movements = []
    for i in range(len(zombies)):
        zombie_movement = [0,0]
        
        #left and right movement


        # zombie_movement_chance = random.randint(0,1000)
        # #random decision to move right
        # if zombie_movement_chance <= 50:
        #     zombie_movement[0] = 4
        #     zombies[i].x += zombie_movement[0]

        # #random decision to move left
        # if zombie_movement_chance >= 950:
        #     zombie_movement[0]= -4
        #     zombies[i].x += zombie_movement[0]
    




        zombies_movements.append(zombie_movement)
        #left and right movement code/ zombie ai 
    

    #ZOMBIE HORIZONTAL MOVEMENT
    for tile in tile_rect:    
        for i in range(len(zombies)):
            if zombies[i].colliderect(tile):
                if zombies_movements[i][0] > 0:
                    zombies[i].right = tile.left

                if zombies_movements[i][0] < 0:
                    zombies[i].left = tile.right
            
    #ZOMBIE VERTICAL MOVEMENT AND GRAVITY + VERTICAL COLLISION

    zombies_y_momentums = []
    for i in range(len(zombies)):
        zombies_movements[i][1] = zombie_y_momentum
        zombie_y_momentum += 0.2
        if zombie_y_momentum > 4.5:
            zombie_y_momentum = 4.5
        
        zombies_y_momentums.append(zombie_y_momentum)

        if zombies_y_momentums[i] >= 0 and zombies_y_momentums[i] <= 1: #checks if zombie is in the air
            pass
        else:
            zombie_on_ground = False

        zombies[i].y += zombies_movements[i][1]

        for tile in tile_rect:
            if zombies[i].colliderect(tile):
                if zombies_movements[i][1] > 0:
                    zombies[i].bottom = tile.top
                    zombies_y_momentums[i] = 0 # <-- basically tells the game that i can stop falling now
                    zombie_on_ground = True
            
                if zombies_movements[i][1] < 0:
                    zombies[i].top = tile.bottom
                    zombies_y_momentums[i] = 0 # <-- same with this


                                # *--ANIMATION--*
 #-----------------------------------------------------------------------------------------------------
    #chooses what type of action the player is doing to then determine animation playing

    if on_ground == False and player_y_momentum > 0: #falling animation
        mode = 3
    elif on_ground == False and player_y_momentum <= 0: #jumping animation
        mode = 2
    elif moving_right or moving_left:
        mode = 1
    else: #idle
        mode = 0


                                # *--RENDERING--*
 #----------------------------------------------------------------------------------------------------------



    # *--CAMERA MOVEMENT--*
    #these 2 centers the player within the base canvas
    camera_x = player_rect.centerx - (base_res_x // 2) 
    camera_y = player_rect.centery - (base_res_y // 2)

     #map clamping      
    max_cam_x = total_map_w - base_res_x
    max_cam_y = total_map_h - base_res_y

    camera_x = max(0, min(camera_x, max_cam_x))
    camera_y = max(0, min(camera_y, max_cam_y))



    canvas.fill((159, 215, 255))    #nice sky background
    current_y= 0

    #filtering through the top and bottom layer in maps
    for row in maps:            
        current_x = 0
        #filtering through each screen in each layer
        for tile_map in row:
            #drawing the map with respect to each offset
            tile_map.draw_map(canvas, camera_x, camera_y, offset_x = current_x, offset_y = current_y)
            #updating x offset
            current_x += tile_map.map_w
        #updating y offset
        current_y += row[0].map_h

    player_render_pos = (player_rect.x - camera_x, player_rect.y - camera_y) #centers player on screen



    zombies_render_positions = []
    for i in range(len(zombies)):
        zombie_render_pos = (zombies[i].x - camera_x, zombies[i].y - camera_y)
        zombies_render_positions.append(zombie_render_pos)

    #flipping code
    
    if moving_left == True:
        x_flip = True
    elif moving_right == True:
        x_flip = False
    else:
         pass

 
    current_frames = update_action(mode) #determines the current type of animation playing
    count, index = update_player_frame(mode, index, count) #update frame played
    player_sprite = current_frames[index] #determines the image/sprite which will be displayed on player pos
    canvas.blit(pygame.transform.flip(player_sprite, x_flip, False), player_render_pos) 

    for i in range(len(zombies)):
        canvas.blit(zombie_sprite, (zombies_render_positions[i]))

     

    #^^ draws the player onto the location of its hitbox*
    # x_flip tells the game whether it should flip the direction of the sprite on the x axis or not.
    # all sprites are all originally drawn to the right side.


    #scale the screen
    scaled_resolution = pygame.transform.scale(canvas, (screen_state_w, screen_state_h))

    screen.blit(scaled_resolution,(0,0))   #creates a window to be displayed

    pygame.display.update() #updates the screen
    clock.tick(60) #ensures framerate is consistently 60fps

