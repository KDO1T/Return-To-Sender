import pygame, sys
from pygame.locals import *
from spritesheet import Spritesheet
from tilemap import *
pygame.init()

clock = pygame.time.Clock()

#grab resolution for the users monitor
resolution = pygame.display.get_desktop_sizes()
#baseline resolution
base_res_x, base_res_y = 640, 360        

display_w , display_h = resolution[0]   #index 0 for the first monitor   
window_w, window_h = 1280,720

screen_state_w, screen_state_h = window_w, window_h

#base window status
status = RESIZABLE

canvas = pygame.Surface((base_res_x, base_res_y))
screen = pygame.display.set_mode((screen_state_w, screen_state_h), status)

sprites = Spritesheet('spritesheet.png')


map = TileMap('test_level.csv', sprites) #passes the csv file and the png file into the map variable

while True:

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        if event.type == VIDEORESIZE and status == RESIZABLE:
            window_w, window_h = event.w , event.h
            screen_state_w, screen_state_h = window_w, window_h
            screen = pygame.display.set_mode((screen_state_w, screen_state_h),status)

        if event.type == KEYDOWN:
            if event.key == K_F1:
                status = RESIZABLE
                screen_state_w, screen_state_h = window_w, window_h
                screen = pygame.display.set_mode((screen_state_w, screen_state_h), status)

            elif event.key == K_F2:
                status = NOFRAME
                screen_state_w, screen_state_h = display_w, display_h
                screen = pygame.display.set_mode((display_w, display_h), status)

            elif event.key == K_F3:
                status = FULLSCREEN
                screen_state_w, screen_state_h = display_w, display_h
                screen = pygame.display.set_mode((display_w,display_h), status)
                
    

    canvas.fill((159, 215, 255))    #nice sky background
    map.draw_map(canvas)    #uses the draw_map function to blit the surface of the tilemap onto the screen

    #scale the screen
    scaled_resolution = pygame.transform.scale(canvas, (screen_state_w, screen_state_h))

    screen.blit(scaled_resolution,(0,0))   #creates a window to be displayed
    pygame.display.update()
    clock.tick(60)