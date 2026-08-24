import pygame, sys

clock = pygame.time.Clock() #assigning the clock function to a variable to use for the fps in the gameloop

#1. initiliaze pygame, 2. names the window, 3. sets the window size and sets its paramaters
pygame.init()
pygame.display.set_caption("Return To Sender") 

window_size = (1000, 500)
screen = pygame.display.set_mode(window_size) # fixed resolution, might change later due to technical issues



# *--PLAYER STUFF--*
player_sprite = pygame.image.load('sprites/jimmy.png')
moving_up = False
moving_down = False
moving_right = False
moving_left = False
player_rect = pygame.Rect(250, 250, player_sprite.get_width(), player_sprite.get_height()) #player hitbox
player_y_momentum = 0 # <-- gravity enacted on the player



object_rect = pygame.Rect(300, 300, 250,250)

# *--TILES OBJECTS--*
tiles = [pygame.Rect(0, window_size[1]-50, 200,50 ), pygame.Rect(200, window_size[1]-50, 200,50), 
         pygame.Rect(400, window_size[1]-50, 200,50), pygame.Rect(600, window_size[1]-50, 200,50),
         pygame.Rect(800, window_size[1]-50, 200,50 ),pygame.Rect(1000, window_size[1]-50, 200,50 ) ]


# *-- FLOOR OBJECT--*
# floor_object = [window_size[0], 50] # width x height
# floor_location = [0, window_size[1]-floor_object[1]]
# floor_rect = pygame.Rect(floor_location[0], floor_location[1], floor_object[0], floor_object[1])






#note for rendering: whatever is first rendered in the loop will be behind while whatever is last rendered in the loop will be in the very front
# *--GAME LOOP--*
running = True
while running: 

    x_movement = 0
    y_movement = 0

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

     # *--PLAYER MOVEMENT--*
    if moving_up == True:
        y_movement= -4
        player_rect.y += y_movement

    if moving_down == True:
        y_movement= 4
        player_rect.y += y_movement

    if moving_right == True:
        x_movement= 4
        player_rect.x += x_movement

    if moving_left == True:
        x_movement= -4
        player_rect.x += x_movement
 



    
    
    # *--TILE COLLISIONS--*


    for tile in tiles:
        if player_rect.colliderect(tile):
           
                if x_movement > 0:
                    player_rect.right = tile.left

                if x_movement < 0:
                    player_rect.left = tile.right



    for tile in tiles:
        if player_rect.colliderect(tile):
                
                if y_movement > 0:
                    player_rect.bottom = tile.top

                if y_movement < 0:
                    player_rect.top = tile.bottom





    


    # *--PLAYER GRAVITY--*
    # if player_location[1] > window_size[1]-50:
    #     player_y_momentum += 0.2
    # else:
    #     player_y_momentum = 0

    # player_location[1] += player_y_momentum

    

    # *--RENDERING--*
    

    screen.fill((255,255,255)) #fills the background with white

    # *--COLLISION TESTING--*
    if player_rect.colliderect(object_rect):
        pygame.draw.rect(screen, (255,0,0), object_rect)
    else:
        pygame.draw.rect(screen, (0, 255, 0), object_rect)

    for tile in tiles:
        pygame.draw.rect(screen, (92, 64, 51), tile)


    screen.blit(player_sprite, player_rect) #draws the player onto the screen with its corresponding location

    pygame.display.update() #updates the screen
    clock.tick(60) #ensures framerate is consistently 60fps