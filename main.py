import pygame, sys

clock = pygame.time.Clock() #assigning the clock function to a variable to use for the fps in the gameloop

#1. initiliaze pygame, 2. names the window, 3. sets the window size and sets its paramaters
pygame.init()
pygame.display.set_caption("Return To Sender") 
screen = pygame.display.set_mode((1920,1080)) # (0,0) means it will fit whatever screen its displayed on, might change later due to technical issues



# *--PLAYER STUFF--*
player_sprite = pygame.image.load('picture test.png')
player_location = [50, 50]
moving_up = False
moving_down = False
moving_right = False
moving_left = False


# *--GAME LOOP--*
running = True
while running: 

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
        player_location[1] -= 4 
    if moving_down == True:
        player_location[1] += 4
    if moving_right == True:
        player_location[0] += 4
    if moving_left == True:
        player_location[0] -= 4

    screen.fill((0,0,0)) #fills the background with black
    screen.blit(player_sprite, player_location) #draws the player onto the screen with its corresponding location

    pygame.display.update() #updates the screen
    clock.tick(60) #ensures framerate is consistently 60fps