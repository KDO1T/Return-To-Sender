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

save_card_width = 170
save_card_height = 150
save_card_y = 100

save_card_positions = [
    (35, save_card_y),
    (235, save_card_y),
    (435, save_card_y)
]

# --------------
main_menu = ["Play", "Options", "Quit"]
save_slots = [
    {
        "name": "Save 1",
        "exists": False,
        "last_saved": None
    },
    {
        "name": "Save 2",
        "exists": False,
        "last_saved": None
    },
    {
        "name": "Save 3",
        "exists": False,
        "last_saved": None
    }
]

selected_save = None


selected = 0
current_state = "MAIN"

while True:
    screen.fill((15, 15, 20))

    # main menu
    if current_state == "MAIN":
        screen.blit(text, rect_text)

        for index, option in enumerate(main_menu):
            y = start_y + (index * spacing)

            option_text = font_menu.render(
                option, False, (240, 240, 240)
            )

            option_rect = option_text.get_rect()
            option_rect.center = (width / 2, y)

            if option_rect.collidepoint(pygame.mouse.get_pos()):
                option_text = font_menu.render(
                    option, False, (235, 65, 40)
                )

            screen.blit(option_text, option_rect)

    elif current_state == "PLAY":
        for index, save in enumerate(save_slots):
            x, y = save_card_positions[index]

            card_rect = pygame.Rect(
                x,
                y,
                save_card_width,
                save_card_height
            )

            if selected_save == index:
                pygame.draw.rect(
                    screen, (235, 65, 40), card_rect, 3
                )
            else:
                pygame.draw.rect(
                    screen, (60, 60, 70), card_rect, 3
                )

            name_text = font_menu.render(
                save["name"], False, (240, 240, 240)
            )

            name_rect = name_text.get_rect()
            name_rect.center = (
                card_rect.centerx,
                card_rect.y + 35
            )

            screen.blit(name_text, name_rect)

            if save["exists"]:
                info_text = font_menu.render(
                    "SAVED", False, (240, 240, 240)
                )
            else:
                info_text = font_menu.render(
                    "EMPTY", False, (140, 140, 140)
                )

            info_rect = info_text.get_rect()
            info_rect.center = (
                card_rect.centerx,
                card_rect.y + 90
            )

            screen.blit(info_text, info_rect)

        # back button
        back_text = font_menu.render(
            "Back", False, (240, 240, 240)
        )

        back_rect = back_text.get_rect()
        back_rect.center = (width / 2, 310)

        if back_rect.collidepoint(pygame.mouse.get_pos()):
            back_text = font_menu.render(
                "Back", False, (235, 65, 40)
            )

        screen.blit(back_text, back_rect)

    # input
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        elif event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:

                if current_state == "MAIN":

                    for index, option in enumerate(main_menu):
                        y = start_y + (index * spacing)

                        option_rect = pygame.Rect(
                            0, y - 20, width, 40
                        )

                        if option_rect.collidepoint(event.pos):

                            if option == "Play":
                                current_state = "PLAY"
                                selected_save = None

                            elif option == "Options":
                                print("Options")

                            elif option == "Quit":
                                pygame.quit()
                                exit()

                elif current_state == "PLAY":

                    for index, position in enumerate(save_card_positions):
                        x, y = position

                        card_rect = pygame.Rect(
                            x,
                            y,
                            save_card_width,
                            save_card_height
                        )

                        if card_rect.collidepoint(event.pos):

                            if selected_save == index:
                                print(
                                    "OPEN SAVE:",
                                    save_slots[index]["name"]
                                )
                            else:
                                selected_save = index

                    back_rect = pygame.Rect(
                        0, 290, width, 40
                    )

                    if back_rect.collidepoint(event.pos):
                        current_state = "MAIN"
                        selected_save = None

    pygame.display.update()
    clock.tick(60)