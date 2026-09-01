from sys import exit

import pygame

pygame.init()

# Window resolution
width, height = 640, 360

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Return To Sender")
# pygame.display.set_icon()

clock = pygame.time.Clock()

# --------------
main_menu = ["Play", "Options", "Quit"]



# fonts
font_title = pygame.font.Font("pygame_tutorial/Press_Start_2P/PressStart2P.ttf", 30)
font_menu = pygame.font.Font("pygame_tutorial/VT323/VT323.ttf", 45)

option_text = font_menu.render("Play", False, (240, 240, 240))
text = font_title.render("Return To Sender", False, (240, 240, 240))
rect_text = text.get_rect()

rect_text.center = (width/2, height/2)


start_y = 220
spacing = 40


selected = 0


while True:
    screen.fill((15, 15, 20))
    for index, option in enumerate(main_menu):
        y = start_y + (index * spacing)

        if selected == index:
            option_text =  font_menu.render(option, False, (235, 65, 40))
        else:
            option_text =  font_menu.render(option, False, (240, 240, 240))

        option_rect = option_text.get_rect()
        option_rect.center = (width/2, y)
        screen.blit(option_text, option_rect)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    screen.blit(text, rect_text)
    pygame.display.update()
    clock.tick(60)