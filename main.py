import pygame, sys
from pygame.locals import *
from spritesheet import Spritesheet
from tilemap import *
from perlin_noise import PerlinNoise
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

tile_size = 32
#16 tiles / chunk
chunk_tiles_x = 16
chunk_tiles_y = 16

chunk_pixel_w = chunk_tiles_x*tile_size
chunk_pixel_h = chunk_tiles_y*tile_size

render_distance = 2
loaded_chunks = {}

#Surface_Level
noise_1d = PerlinNoise(octaves=2, seed = 1234)
#Caves
noise_2d = PerlinNoise(octaves=3, seed = 1234)


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

            #spawns 0 at below tile level of 8
            if depth < 0:
                row.append('-1')
            elif depth == 0:
                if cave_volume <= -0.1:
                    row.append('-1')
                else:
                    row.append('1')
            else:
                if depth > 20:
                    row.append('11')
                else:
                    cave_threshold = -0.15 + min(0.1, depth*0.005)
                    if cave_volume <= cave_threshold:
                        row.append('-1')
                    else:
                        row.append('11')
        grid.append(row)
    return grid

# *--PLAYER STUFF--*

player_sprite = pygame.image.load('sprites/ajimmus.png')
moving_up = False
moving_down = False
moving_right = False
moving_left = False
player_rect = pygame.Rect(250, 250, player_sprite.get_width(), player_sprite.get_height()) #player hitbox
player_y_momentum = 0 # <-- gravity enacted on the player
max_air_jumps = 1
air_jumps = 0
on_ground = None

object_rect = pygame.Rect(300, 300, 250,250)

# # *--TILES OBJECTS--*
# tile_rect = []
# current_y = 0
# for row in maps:    
#     current_x = 0
#     for tile_map in row:
#         # Fetch rects offset by their section's x and y world positions
#         section_rects = tile_map.get_rects(current_x, current_y)
#         tile_rect.extend(section_rects)
        
#         current_x += tile_map.map_w
#     current_y += row[0].map_h


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
        # elif player_rect.right>total_map_w or player_rect.top <0 or player_rect.bottom> total_map_h:
        #     pygame.quit()
        #     sys.exit()
        # elif player_rect.left <0:
        #     player_rect.left = 1
        
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

                #positive y momentum is downward | negative y momentum is upward
                if on_ground is True: #player touching ground
                    jump = True
                    air_jumps = max_air_jumps
                else: #player is in the air
                    if air_jumps > 0: #if player has an extra jump, then jump then deduct from remaining jumps
                        jump = True
                        air_jumps -= 1
                    else:
                        pass
             


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

    #chunk manager
    position_chunk_x , position_chunk_y = world_to_chunk(player_rect.centerx, player_rect.centery)
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

    #jump
    if jump == True:
        player_y_momentum = -4.5


    for tile in tile_rect:
        if player_rect.colliderect(tile):
            if player_movement[1] > 0:
                player_rect.bottom = tile.top
                player_y_momentum = 0 # <-- basically tells the game that i can stop falling now
                on_ground = True
        
            if player_movement[1] < 0:
                player_rect.top = tile.bottom
                player_y_momentum = 0 # <-- same with this

                                         # *--RENDERING--*
 #------------------------------------

    # void
    if player_rect.y > 2000:
        player_rect.x, player_rect.y = 250,100
        player_y_momentum = 0


    # *--CAMERA MOVEMENT--*
    #these 2 centers the player within the base canvas
    camera_x = player_rect.centerx - (base_res_x // 2) 
    camera_y = player_rect.centery - (base_res_y // 2)

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

    for (chunk_x,chunk_y), tile_map in loaded_chunks.items():
        chunk_world_x = chunk_x *chunk_pixel_w
        chunk_world_y = chunk_y * chunk_pixel_h
        tile_map.draw_map(canvas, camera_x, camera_y,offset_x=chunk_world_x,offset_y=chunk_world_y)

    player_render_pos = (player_rect.x - camera_x, player_rect.y - camera_y) #centers player on screen
    canvas.blit(player_sprite, player_render_pos) #draws the player onto the location of its hitbox*



    #scale the screen
    scaled_resolution = pygame.transform.scale(canvas, (screen_state_w, screen_state_h))


    screen.blit(scaled_resolution,(0,0))   #creates a window to be displayed


    pygame.display.update() #updates the screen
    clock.tick(60) #ensures framerate is consistently 60fps

