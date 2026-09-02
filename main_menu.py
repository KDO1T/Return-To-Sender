from sys import exit

import pygame

pygame.init()


# resolution
resolution = pygame.display.get_desktop_sizes()

base_res_x, base_res_y = 640, 360

display_w, display_h = resolution[0]

window_w, window_h = 1280, 720
screen_state_w, screen_state_h = window_w, window_h

status = pygame.RESIZABLE

canvas = pygame.Surface((base_res_x, base_res_y))

screen = pygame.display.set_mode(
    (screen_state_w, screen_state_h),
    status
)

pygame.display.set_caption("Return To Sender")

clock = pygame.time.Clock()


# fonts
font_title = pygame.font.Font("fonts/Press_Start_2P/PressStart2P.ttf", 30)

font_menu = pygame.font.Font("fonts/VT323/VT323.ttf", 45)

font_save_name = pygame.font.Font("fonts/VT323/VT323.ttf", 32)


text = font_title.render(
    "Return To Sender",
    False,
    (240, 240, 240)
)

rect_text = text.get_rect()

rect_text.center = (
    base_res_x / 2,
    base_res_y / 2
)


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
max_name_length = 10
message = ""

selected = 0
current_state = "MAIN"


def save_rename():

    global message

    new_name = rename_text.strip()

    if new_name == "":
        message = "Name cannot be empty."
        return False

    if len(new_name) > max_name_length:
        message = "Max 10 Characters."
        return False

    for index, save in enumerate(save_slots):

        if index != selected_save and save["name"].lower() == new_name.lower():
            message = "Name Already In Use."
            return False

    save_slots[selected_save]["name"] = new_name
    message = ""

    return True


# game loop (event loop)
while True:

    canvas.fill((15, 15, 20))

    # main menu
    if current_state == "MAIN":

        canvas.blit(text, rect_text)

        for index, option in enumerate(main_menu):

            y = start_y + (index * spacing)

            option_text = font_menu.render(
                option,
                False,
                (240, 240, 240)
            )

            option_rect = option_text.get_rect()

            option_rect.center = (
                base_res_x / 2,
                y
            )

            mouse_x = pygame.mouse.get_pos()[0] * base_res_x / screen_state_w
            mouse_y = pygame.mouse.get_pos()[1] * base_res_y / screen_state_h

            if option_rect.collidepoint(mouse_x, mouse_y):

                option_text = font_menu.render(
                    option,
                    False,
                    (235, 65, 40)
                )

            canvas.blit(option_text, option_rect)


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
                    canvas,
                    (235, 65, 40),
                    card_rect,
                    3
                )

            else:

                pygame.draw.rect(
                    canvas,
                    (60, 60, 70),
                    card_rect,
                    3
                )


            # save name
            if renaming_save and selected_save == index:

                name = rename_text

                name_text = font_save_name.render(
                    name,
                    False,
                    (235, 65, 40)
                )

            else:

                name = save["name"]

                if len(name) > 10:
                    name = name[:7] + "..."

                name_text = font_save_name.render(
                    name,
                    False,
                    (240, 240, 240)
                )


            name_rect = name_text.get_rect()

            name_rect.center = (
                card_rect.centerx,
                card_rect.y + 35
            )


            # keep name inside card
            name_rect.left = max(
                name_rect.left,
                card_rect.left + 8
            )

            name_rect.right = min(
                name_rect.right,
                card_rect.right - 8
            )

            canvas.blit(name_text, name_rect)


            # save status
            if save["exists"]:

                info_text = font_menu.render(
                    "SAVED",
                    False,
                    (240, 240, 240)
                )

            else:

                info_text = font_menu.render(
                    "EMPTY",
                    False,
                    (140, 140, 140)
                )

            info_rect = info_text.get_rect()

            info_rect.center = (
                card_rect.centerx,
                card_rect.y + 90
            )

            canvas.blit(info_text, info_rect)


        # validation message
        if message != "":

            message_text = font_menu.render(
                message,
                False,
                (235, 65, 40)
            )

            message_rect = message_text.get_rect()

            message_rect.center = (
                base_res_x / 2,
                30
            )

            canvas.blit(message_text, message_rect)


        # back button
        back_text = font_menu.render(
            "Back",
            False,
            (240, 240, 240)
        )

        back_rect = back_text.get_rect()

        back_rect.center = (
            base_res_x / 2,
            310
        )
        # change the mouse position with the 1280 x 720 resolution so user isn't clicking at a 640 x 360 coordinates
        mouse_x = pygame.mouse.get_pos()[0] * base_res_x / screen_state_w
        mouse_y = pygame.mouse.get_pos()[1] * base_res_y / screen_state_h

        if back_rect.collidepoint(mouse_x, mouse_y):

            back_text = font_menu.render(
                "Back",
                False,
                (235, 65, 40)
            )

        canvas.blit(back_text, back_rect)


    # input
    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            pygame.quit()
            exit()


        # window controls (for resoltion)
        elif event.type == pygame.VIDEORESIZE:

            if status == pygame.RESIZABLE:

                window_w = event.w
                window_h = event.h

                screen_state_w = window_w
                screen_state_h = window_h

                screen = pygame.display.set_mode(
                    (screen_state_w, screen_state_h),
                    status
                )


        # keyboard
        elif event.type == pygame.KEYDOWN:

            # window controls
            if event.key == pygame.K_F1:

                status = pygame.RESIZABLE

                screen_state_w = window_w
                screen_state_h = window_h

                screen = pygame.display.set_mode(
                    (screen_state_w, screen_state_h),
                    status
                )

            elif event.key == pygame.K_F11:

                status = pygame.FULLSCREEN

                screen_state_w = display_w
                screen_state_h = display_h

                screen = pygame.display.set_mode(
                    (display_w, display_h),
                    status
                )

            elif renaming_save:

                if event.key == pygame.K_RETURN:

                    if save_rename():

                        renaming_save = False
                        rename_text = ""

                elif event.key == pygame.K_BACKSPACE:

                    rename_text = rename_text[:-1]

                else:

                    if event.unicode.isprintable():

                        if len(rename_text) < max_name_length:

                            rename_text += event.unicode

                        else:

                            message = "Max 10 Characters."


        # mouse
        elif event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:

                mouse_x = event.pos[0] * base_res_x / screen_state_w
                mouse_y = event.pos[1] * base_res_y / screen_state_h

                mouse_pos = (mouse_x, mouse_y)


                if current_state == "MAIN":

                    for index, option in enumerate(main_menu):

                        y = start_y + (index * spacing)

                        option_rect = pygame.Rect(
                            0,
                            y - 20,
                            base_res_x,
                            40
                        )

                        if option_rect.collidepoint(mouse_pos):

                            if option == "Play":

                                current_state = "PLAY"
                                selected_save = None
                                message = ""

                            elif option == "Options":

                                print("Options")

                            elif option == "Quit":

                                pygame.quit()
                                exit()


                elif current_state == "PLAY":

                    clicked_save = False

                    for index, position in enumerate(save_card_positions):

                        x, y = position

                        card_rect = pygame.Rect(
                            x,
                            y,
                            save_card_width,
                            save_card_height
                        )

                        if card_rect.collidepoint(mouse_pos):

                            clicked_save = True

                            # make the name hitbox match the text name
                            name_text = font_save_name.render(
                                save_slots[index]["name"],
                                False,
                                (240, 240, 240)
                            )

                            name_rect = name_text.get_rect()

                            name_rect.center = (
                                card_rect.centerx,
                                card_rect.y + 35
                            )


                            # clicked the save name
                            if name_rect.collidepoint(mouse_pos):

                                if selected_save == index:

                                    if not renaming_save:

                                        renaming_save = True
                                        old_name = save_slots[index]["name"]
                                        rename_text = ""
                                        message = ""

                                else:

                                    if renaming_save:

                                        renaming_save = False
                                        rename_text = ""
                                        message = ""

                                    selected_save = index


                            # clicked the selected save
                            elif selected_save == index:

                                if renaming_save:

                                    if save_rename():

                                        renaming_save = False
                                        rename_text = ""

                                else:

                                    print(
                                        "OPEN SAVE:",
                                        save_slots[index]["name"]
                                    )


                            # clicked another save
                            else:

                                if renaming_save:

                                    renaming_save = False
                                    rename_text = ""
                                    message = ""

                                selected_save = index


                    # back button
                    back_rect = pygame.Rect(
                        0,
                        290,
                        base_res_x,
                        40
                    )

                    if back_rect.collidepoint(mouse_pos):

                        if renaming_save:

                            renaming_save = False
                            rename_text = ""
                            message = ""

                        current_state = "MAIN"
                        selected_save = None


    # scale the canvas to the current window size
    scaled_resolution = pygame.transform.scale(
        canvas,
        (screen_state_w, screen_state_h)
    )

    screen.blit(
        scaled_resolution,
        (0, 0)
    )

    pygame.display.update()

    clock.tick(60)