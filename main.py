import pygame, sys
from pygame.locals import *
from spritesheet import Spritesheet
from tilemap import *
pygame.init()

clock = pygame.time.Clock()

display_w , display_h = 768, 512

canvas = pygame.Surface((display_w,display_h))
screen = pygame.display.set_mode((display_w,display_h))

sprites = Spritesheet('spritesheet.png')


map = TileMap('test_level.csv', sprites) #passes the csv file and the png file into the map variable

while True:

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    canvas.fill((159, 215, 255))    #nice sky background
    map.draw_map(canvas)    #uses the draw_map function to blit the surface of the tilemap onto the screen
    screen.blit(canvas,(0,0))   #creates a window to be displayed
    pygame.display.update()
    clock.tick(60)