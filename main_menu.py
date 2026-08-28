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
renaming_save = False
rename_text = ""
old_name = ""


selected = 0
current_state = "MAIN"

def save_rename():

    new_name = rename_text.strip()

    if new_name == "":      #makes sure every rename isn't empty
        save_slots[selected_save]["name"] = old_name
        return False

    for index, save in enumerate(save_slots):

        if index != selected_save and save["name"].lower() == new_name.lower():
            save_slots[selected_save]["name"] = old_name
            return False

    save_slots[selected_save]["name"] = new_name
    return True

# event loop
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

            if renaming_save and selected_save == index:
                name = rename_text
                name_color = (235, 65, 40)
            else:
                name = save["name"]
                name_color = (240, 240, 240)

            name_text = font_menu.render(
                name, False, name_color
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
        #mouse input
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

                            name_text = font_menu.render(
                                save_slots[index]["name"],
                                False,
                                (240, 240, 240)
                            )

                            name_rect = name_text.get_rect()
                            name_rect.center = (
                                card_rect.centerx,
                                card_rect.y + 35
                            )

                            # clicked the name
                            if name_rect.collidepoint(event.pos):

                                if selected_save == index:

                                    if not renaming_save:
                                        renaming_save = True
                                        rename_text = save_slots[index]["name"]
                                        old_name = save_slots[index]["name"]

                                else:

                                    # finish the previous rename
                                    if renaming_save:
                                        save_slots[selected_save]["name"] = rename_text

                                    selected_save = index
                                    renaming_save = False

                            # clicked somewhere else on the selected card
                            elif selected_save == index:

                                if renaming_save:
                                    save_rename()
                                    renaming_save = False

                                else:
                                    print(
                                        "OPEN SAVE:",
                                        save_slots[index]["name"]
                                    )

                            # clicked another card
                            else:
                                # opening another save will still be implemented but we have to check whether it's empty or the name is duplicated
                                if renaming_save:
                                    save_rename()
                                    renaming_save = False

                                selected_save = index

                    back_rect = pygame.Rect(
                        0, 290, width, 40
                    )

                    if back_rect.collidepoint(event.pos):

                        if renaming_save:
                            # save_slots()
                            renaming_save = False

                        current_state = "MAIN"
                        selected_save = None

                        # renaming save slots
                        if card_rect.collidepoint(event.pos):

                            name_text = font_menu.render(
                                save_slots[index]["name"],
                                False,
                                (240, 240, 240)
                            )

                            name_rect = name_text.get_rect()
                            name_rect.center = (
                                card_rect.centerx,
                                card_rect.y + 35
                            )

                        
                            if name_rect.collidepoint(event.pos):

                                # when you select save 1 you can't rename save 2, and vice versa
                                if selected_save == index:
                                    renaming_save = True
                                    rename_text = save_slots[index]["name"]

                                else:
                                    selected_save = index
                                    renaming_save = False

                            elif selected_save == index:
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
                        renaming_save = None
        #keyboard
        elif event.type == pygame.KEYDOWN:

            if renaming_save:
                # makes sure that if they press enter the renaming isn't implemeted, but they are still editing
                if event.key == pygame.K_RETURN:
                    if save_rename():
                        renaming_save = False


                elif event.key == pygame.K_BACKSPACE:
                    rename_text = rename_text[:-1]

                # to add a new letter/character if there is anything "else"
                else:
                    if event.unicode.isprintable():
                        rename_text += event.unicode


    pygame.display.update()
    clock.tick(60)
    