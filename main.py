import pygame, sys
from pygame.locals import *
pygame.init()

clock = pygame.time.Clock()

WINDOW_RESOLUTION = (400,400)
screen = pygame.display.set_mode(WINDOW_RESOLUTION)

while True:

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    pygame.display.update()
    clock.tick(60)