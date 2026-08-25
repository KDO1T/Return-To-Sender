import pygame, sys

clock = pygame.time.Clock() #assigning the clock function to a variable to use for the fps in the gameloop

#1. initiliaze pygame, 2. names the window, 3. sets the window size and sets its paramaters
pygame.init()
pygame.display.set_caption("Return To Sender") 
window_size = (1000, 500)
screen = pygame.display.set_mode(window_size) # fixed resolution, might change later due to technical issues



# *--PLAYER STUFF--*
player_sprite = pygame.image.load('sprites/jimmy_2.png')
moving_up = False
moving_down = False
moving_right = False
moving_left = False
player_rect = pygame.Rect(250, 250, player_sprite.get_width(), player_sprite.get_height()) #player hitbox
player_y_momentum = 0 # <-- gravity enacted on the player
air_jumps = 0
can_jump = True

object_rect = pygame.Rect(300, 300, 250,250)

# *--TILES OBJECTS--*
floor_tiles = [pygame.Rect(0, window_size[1]-50, 200,50 ), pygame.Rect(200, window_size[1]-50, 200,50), 
         pygame.Rect(400, window_size[1]-50, 200,50), pygame.Rect(600, window_size[1]-50, 200,50),
         pygame.Rect(800, window_size[1]-50, 200,50 ),pygame.Rect(1000, window_size[1]-50, 200,50 ),
         ]

platform_tiles = [
                 pygame.Rect(0, window_size[1]-300, 200,50 ),  
                pygame.Rect(400, window_size[1]-300, 200,50),
                pygame.Rect(800, window_size[1]-300, 200,50 )
                ]



#note for rendering: whatever is first rendered in the loop will be behind while whatever is last rendered in the loop will be in the very front
# *--GAME LOOP--*
running = True
while running: 

    # max_air_jumps = 1
    jump = False

       # *--INPUT DETECTION--*
    for event in pygame.event.get(): #just detects if any 'events' occur

        # *--QUIT--*
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # *--KEY DETECTION--*

            # *--KEY IS PRESSED--*
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:#pressing W (up)
                moving_up = True
            if event.key == pygame.K_s:#pressing S (down)
                moving_down = True
            if event.key == pygame.K_d: #pressing D (right)
                moving_right = True
            if event.key == pygame.K_a: #pressing A (left)
                moving_left = True
            if event.key == pygame.K_SPACE:

                # for tile in floor_tiles and tile in platform_tiles:
                #     if player_rect.colliderect(tile):
                        
                        #positive y momentum is downward | negative y momentum is upward
                        if  player_y_momentum >= 0 and player_y_momentum <= 1:#player touching ground
                            can_jump = True
                        else:
                            can_jump = False

                        print(player_y_momentum)
                        print(can_jump)

                        if can_jump == True:  
                            #player is jumping from a stable surface i.e. not in the air
                            jump = True
                        else:  
                            jump = False
                        


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


    player_movement = [0,0]  








    # *--HORIZONTAL MOVEMENT + COLLISIONS--*

    #left and right movement
    if moving_right == True:
        player_movement[0]= 4
        player_rect.x += player_movement[0]

    if moving_left == True:
        player_movement[0]= -4
        player_rect.x += player_movement[0]
 
    #collisions
    for tile in platform_tiles:    
        if player_rect.colliderect(tile):
            
            if player_movement[0] > 0:
                player_rect.right = tile.left

            if player_movement[0] < 0:
                player_rect.left = tile.right



    # *-- VERTICAL MOVEMENT + VERTICAL COLLISIONS --*
    
    #gravity
    player_movement[1] = player_y_momentum
    
    player_y_momentum += 0.2
    if player_y_momentum > 10:
        player_y_momentum = 10

    player_rect.y += player_movement[1]

    #jump
    if jump == True:
        player_y_momentum = -4.5


    for tile in floor_tiles:
        if player_rect.colliderect(tile):
            if player_movement[1] > 0:
                player_rect.bottom = tile.top
                player_y_momentum = 0 # <-- basically tells the game that i can stop falling now
                print("you can jump")
                
            if player_movement[1] < 0:
                player_rect.top = tile.bottom
                player_y_momentum = 0 # <-- same with this



    for tile in platform_tiles:
        if player_rect.colliderect(tile):
            if player_movement[1] > 0:
                player_rect.bottom = tile.top
                player_y_momentum = 0 # <-- basically tells the game that i can stop falling now
                print("you can jump")
                
            if player_movement[1] < 0:
                player_rect.top = tile.bottom
                player_y_momentum = 0 # <-- same with this

    

    # *--RENDERING--*
    

    screen.fill((255,255,255)) #fills the background with white

    # *--COLLISION TESTING--*
    if player_rect.colliderect(object_rect):
        pygame.draw.rect(screen, (255,0,0), object_rect)
    else:
        pygame.draw.rect(screen, (0, 255, 0), object_rect)

    for tile in floor_tiles:
        pygame.draw.rect(screen, (92, 64, 51), tile)

    for tile in platform_tiles:
        pygame.draw.rect(screen, (92, 64, 51), tile)



    screen.blit(player_sprite, player_rect) #draws the player onto the location of its hitbox*

    pygame.display.update() #updates the screen
    clock.tick(60) #ensures framerate is consistently 60fps