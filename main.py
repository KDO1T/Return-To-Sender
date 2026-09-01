import pygame, sys
from pygame.locals import *
from spritesheet import Spritesheet
from tilemap import *
from player import Player
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

clock = pygame.time.Clock() #assigning the clock function to a variable to use for the fps in the gameloop

#1. initiliaze pygame, 2. names the window, 3. sets the window size and sets its paramaters
pygame.init()
pygame.display.set_caption("Return To Sender") 
canvas = pygame.Surface((base_res_x, base_res_y))
screen = pygame.display.set_mode((screen_state_w, screen_state_h), status)

# *-- MAP STUFF --*
sprites = Spritesheet('spritesheet.png')
map_grid = [['screenR1C1.csv', 'screenR1C2.csv','screenR1C3.csv'],
            ['screenR2C1.csv','screenR2C2.csv','screenR2C3.csv']] #passes the csv file and the png file into the map variable

maps = [[TileMap(file,sprites) for file in row] for row in map_grid]            #puts all row files in map_grid into a list, and putting all maps from the list into maps

#combine both map (top and bottom)
total_map_w = sum(tile_maps.map_w  for tile_maps in maps[0])   #loops through maps list
total_map_h = sum(row[0].map_h for row in maps)


# *--PLAYER STUFF--*
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

player.show_stat()


player_sprite = pygame.image.load('sprites/willie.png')
moving_up = False
moving_down = False
moving_right = False
moving_left = False
player_rect = pygame.Rect(250, 250, player_sprite.get_width(), player_sprite.get_height()) #player hitbox
player_y_momentum = 0 # <-- gravity enacted on the player
press_space = False
max_air_jumps = 0
air_jumps = max_air_jumps
on_ground = None


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
            if event.key == pygame.K_w:#let go of W (up)
                moving_up = False
            if event.key == pygame.K_s:#let go of S (down)
                moving_down = False
            if event.key == pygame.K_d: #let go of D (right)
                moving_right = False
            if event.key == pygame.K_a: #let go of A (left)
                moving_left = False


    # *--HORIZONTAL MOVEMENT + COLLISIONS--*

    player_movement = [0,0]  

    #left and right movement
    if moving_right == True:
        player_movement[0]= 4
        player_rect.x += player_movement[0]

    if moving_left == True:
        player_movement[0]= -4
        player_rect.x += player_movement[0]

    #REMOVE LATER
    if moving_down == True:
        player_movement[1]= 4
        player_rect.y += player_movement[1]

    if moving_up == True:
        player_movement[1]= -4
        player_rect.y += player_movement[1]

    #collisions
    for tile in tile_rect:    
        if player_rect.colliderect(tile):
            if player_movement[0] > 0:
                player_rect.right = tile.left

            if player_movement[0] < 0:
                player_rect.left = tile.right

#---------------------------------------------------------------------

    # *-- VERTICAL MOVEMENT + VERTICAL COLLISIONS --*
    
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















                                         # *--RENDERING--*
 #------------------------------------



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
    canvas.blit(player_sprite, player_render_pos) #draws the player onto the location of its hitbox*



    #scale the screen
    scaled_resolution = pygame.transform.scale(canvas, (screen_state_w, screen_state_h))


    screen.blit(scaled_resolution,(0,0))   #creates a window to be displayed

    pygame.display.update() #updates the screen
    clock.tick(60) #ensures framerate is consistently 60fps

