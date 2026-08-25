from sys import exit

import pygame

pygame.init()

w, h = 640, 360

screen = pygame.display.set_mode((w, h))
pygame.display.set_caption("Return To Sender")

clock = pygame.time.Clock()
running = True

sky = pygame.image.load("pygame_tutorial/assets/Sky.png")
ground = pygame.image.load("pygame_tutorial/assets/ground.png")

text_test = pygame.font.SysFont("Fixedsys", 64, bold=True)

text_surface = text_test.render("Return To Sender", False, "White")

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    screen.blit(ground, (0, 300))
    screen.blit(sky, (0, 0))
    screen.blit(text_surface, (100, 150))
            # render
    pygame.display.update()