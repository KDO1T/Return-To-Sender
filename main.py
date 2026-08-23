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


map = TileMap('test_level.csv', sprites)
start_x, start_y = map.start_x, map.start_y

while True:

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    canvas.fill((255,255,255))
    map.draw_map(canvas)
    screen.blit(canvas,(0,0))
    pygame.display.update()
    clock.tick(60)