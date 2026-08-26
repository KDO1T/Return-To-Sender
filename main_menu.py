from sys import exit

import pygame

pygame.init()

# Window resolution
width, height = 640, 360

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Return To Sender")
# pygame.display.set_icon()

clock = pygame.time.Clock()


# fonts
font_title = pygame.font.Font("fonts/Press_Start_2P/PressStart2P.ttf", 30)
font_menu = pygame.font.Font("fonts/VT323/VT323.ttf", 45)


text = font_title.render("Return To Sender", False, (240, 240, 240))
rect_text = text.get_rect()

rect_text.center = (width/2, height/2)

# text positioning
start_y = 220
spacing = 40

play_start_y = 130
play_spacing = 40

# --------------
main_menu = ["Play", "Options", "Quit"]
play_menu = ["Save Slot 1", "Save Slot 2", "Save Slot 3", "Skill Tree", "Back"]

play_selected = 0
selected = 0
current_state = "MAIN"

while True:
    screen.fill((15, 15, 20))

    if current_state == "MAIN":
        for index, option in enumerate(main_menu):
            y = start_y + (index * spacing)

            if selected == index:
                option_text =  font_menu.render(option, False, (235, 65, 40))
            else:
                option_text =  font_menu.render(option, False, (240, 240, 240))

            option_rect = option_text.get_rect()
            option_rect.center = (width/2, y)
            screen.blit(option_text, option_rect)

    elif current_state == "PLAY":
        for index, option in enumerate(play_menu):
            y = play_start_y + (index * play_spacing)

            if play_selected == index:
                option_text = font_menu.render(option, False, (235, 65, 40))
            else:
                option_text = font_menu.render(option, False, (240, 240, 240))

            option_rect = option_text.get_rect()
            option_rect.center = (width / 2, y)
            screen.blit(option_text, option_rect)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                selected = (selected + 1) % len(main_menu)

            elif event.key == pygame.K_UP:
                selected = (selected - 1) % len(main_menu)

            elif event.key == pygame.K_RETURN:
                if main_menu[selected] == "Play":
                    current_state = "PLAY"
                
    screen.blit(text, rect_text)
    pygame.display.update()
    clock.tick(60)