import pygame, sys

clock = pygame.time.Clock() #assigning the clock function to a variable to use for the fps in the gameloop

#1. initiliaze pygame, 2. names the window, 3. sets the window size and sets its paramaters
pygame.init()
pygame.display.set_caption("Return To Sender") 
screen = pygame.display.set_mode((0,0)) # (0,0) means it will fit whatever screen its displayed on, might change later due to technical issues




# *--GAME LOOP--*
running = True
while running: 


    # *--INPUT DETECTION--*
    for event in pygame.event.get(): 
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()



    pygame.display.update() #updates the screen
    clock.tick(60) #ensures framerate is consistently 60fps