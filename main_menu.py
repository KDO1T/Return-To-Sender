import json
import os
import subprocess
from sys import executable, exit

import pygame

import config

pygame.init()

# Save file paths
saves_dir = os.path.join(os.getcwd(), "saves")
os.makedirs(saves_dir, exist_ok=True)


def save_file_path(slot_name):
    return os.path.join(saves_dir, f"{slot_name}.json")


def save_exists(slot_name):
    return os.path.exists(save_file_path(slot_name))


def create_save_file(slot_name, slot_index):
    with open(save_file_path(slot_name), "w") as save_file:
        json.dump({"name": slot_name, "slot_index": slot_index}, save_file, indent=4)


def delete_save_file(slot_name):
    save_path = save_file_path(slot_name)
    if os.path.exists(save_path):
        os.remove(save_path)


def rename_save_file(old_name, new_name):
    old_path = save_file_path(old_name)
    new_path = save_file_path(new_name)
    if os.path.exists(old_path):
        with open(old_path, "r") as save_file:
            save_data = json.load(save_file)

        save_data["name"] = new_name
        os.rename(old_path, new_path)

        with open(new_path, "w") as save_file:
            json.dump(save_data, save_file, indent=4)


def delete_save_slot(slot_index):
    """Delete a save slot: remove JSON file if it exists, mark slot as Empty."""
    slot_name = save_slots[slot_index]["name"]
    if save_exists(slot_name):
        delete_save_file(slot_name)
    save_slots[slot_index]["name"] = f"Save {slot_index + 1}"
    save_slots[slot_index]["exists"] = False
    save_slots[slot_index]["last_saved"] = None


def sync_save_slots_with_files():
    """Sync save_slots with existing JSON files on startup."""
    for index, slot in enumerate(save_slots):
        slot["name"] = f"Save {index + 1}"
        slot["exists"] = False

    for filename in os.listdir(saves_dir):
        if not filename.endswith(".json"):
            continue

        save_path = os.path.join(saves_dir, filename)

        try:
            with open(save_path, "r") as save_file:
                save_data = json.load(save_file)
        except (OSError, json.JSONDecodeError):
            continue

        slot_index = save_data.get("slot_index")

        if not isinstance(slot_index, int) or isinstance(slot_index, bool):
            save_name = os.path.splitext(filename)[0]

            if save_name.startswith("Save ") and save_name[-1:].isdigit():
                slot_index = int(save_name[-1:]) - 1
            else:
                continue

        if not 0 <= slot_index < len(save_slots):
            continue

        save_slots[slot_index]["name"] = os.path.splitext(filename)[0]
        save_slots[slot_index]["exists"] = True


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
font_section = pygame.font.Font("fonts/VT323/VT323.ttf", 28)
font_small = pygame.font.Font("fonts/VT323/VT323.ttf", 24)


text = font_title.render(
    "Return To Sender",
    False,
    (240, 240, 240)
)

rect_text = text.get_rect()

rect_text.center = (
    base_res_x / 2,
    base_res_y /4
)


# text positioning
start_y = 180
spacing = 50

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

# Sync save slots with existing JSON files on startup
sync_save_slots_with_files()

selected_save = None
renaming_save = False
rename_text = ""
old_name = ""
max_name_length = 10
message = ""

selected = 0
current_state = "MAIN"

# Options menu state
selected_option = None
dropdown_open = False
resolution_options = [
    (640, 360),
    (1280, 720),
    (1920, 1080)
]
selected_resolution = 1
fullscreen = False

# Audio values (0 - 100)
master_volume = 100
music_volume = 80
sfx_volume = 100

# Brightness value (0 - 100)
brightness = 0

# Drag state for sliders
drag = False
dragging_slider = None


def open_save(slot_index):
    slot_name = save_slots[slot_index]["name"]

    if not save_exists(slot_name):
        create_save_file(slot_name, slot_index)
        save_slots[slot_index]["exists"] = True

    subprocess.Popen(
        [executable, "main.py", "--save-slot", str(slot_index), "--brightness", str(brightness)]
    )

    pygame.quit()
    exit()


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

    # Rename the JSON file if it exists
    if save_exists(old_name):
        rename_save_file(old_name, new_name)

    # Indicator for the save slot "Exists" or "None"
    save_slots[selected_save]["name"] = new_name
    # Syncs "exists" indicator with file existence after rename
    save_slots[selected_save]["exists"] = save_exists(new_name)
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

            option_rect.left = 50
            option_rect.centery = y

            mouse_x = pygame.mouse.get_pos()[0] * base_res_x / screen_state_w
            mouse_y = pygame.mouse.get_pos()[1] * base_res_y / screen_state_h

            if option_rect.collidepoint(mouse_x, mouse_y):

                option_text = font_menu.render(
                    option,
                    False,
                    (235, 65, 40)
                )

            canvas.blit(option_text, option_rect)

    # PLAY MENU
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

    # OPTIONS Menu
    elif current_state == "OPTIONS":

        options_title = font_title.render(
            "Options",
            False,
            (240, 240, 240)
        )
        options_title_rect = options_title.get_rect(center=(base_res_x / 2, 35))
        canvas.blit(options_title, options_title_rect)

        options_subtitle = font_section.render(
            "[ SETTINGS ]",
            False,
            (140, 140, 140)
        )
        options_subtitle_rect = options_subtitle.get_rect(center=(base_res_x / 2, 68))
        canvas.blit(options_subtitle, options_subtitle_rect)

        # Menu cards
        option_cards = [
            "Audio Settings",
            "Video Settings",
            "Controls"
        ]

        for index, option in enumerate(option_cards):

            card_rect = pygame.Rect(
                100,
                95 + (index * 55),
                440,
                40
            )

            pygame.draw.rect(
                canvas,
                (25, 25, 30),
                card_rect,
                2
            )

            card_text = font_section.render(
                option,
                False,
                (240, 240, 240)
            )
            card_text_rect = card_text.get_rect(
                midleft=(card_rect.left + 20, card_rect.centery)
            )
            canvas.blit(card_text, card_text_rect)

            arrow_text = font_section.render(
                ">",
                False,
                (235, 65, 40)
            )
            arrow_rect = arrow_text.get_rect(
                midright=(card_rect.right - 20, card_rect.centery)
            )
            canvas.blit(arrow_text, arrow_rect)

        # Back button
        back_text = font_section.render(
            "Back",
            False,
            (240, 240, 240)
        )
        back_rect = back_text.get_rect(
            center=(base_res_x / 2, 330)
        )

        mouse_x = pygame.mouse.get_pos()[0] * base_res_x / screen_state_w
        mouse_y = pygame.mouse.get_pos()[1] * base_res_y / screen_state_h

        if back_rect.collidepoint(mouse_x, mouse_y):
            back_text = font_section.render(
                "Back",
                False,
                (235, 65, 40)
            )

        canvas.blit(back_text, back_rect)


    # VIDEO Settings sub-screen
    elif current_state == "VIDEO":

        video_title = font_title.render(
            "Video",
            False,
            (240, 240, 240)
        )
        video_title_rect = video_title.get_rect(center=(base_res_x / 2, 35))
        canvas.blit(video_title, video_title_rect)

        video_subtitle = font_section.render(
            "[ SCREEN & PERFORMANCE ]",
            False,
            (140, 140, 140)
        )
        video_subtitle_rect = video_subtitle.get_rect(
            center=(base_res_x / 2, 68)
        )
        canvas.blit(video_subtitle, video_subtitle_rect)

        panel_rect = pygame.Rect(80, 95, 480, 190)

        pygame.draw.rect(
            canvas,
            (25, 25, 30),
            panel_rect,
            2
        )

        # Resolution
        res_label = font_section.render(
            "Resolution:",
            False,
            (240, 240, 240)
        )
        res_label_rect = res_label.get_rect(
            midleft=(panel_rect.left + 25, 130)
        )
        canvas.blit(res_label, res_label_rect)

        res_text = font_section.render(
            f"{resolution_options[selected_resolution][0]}x{resolution_options[selected_resolution][1]}",
            False,
            (235, 65, 40)
        )
        res_text_rect = res_text.get_rect(
            midright=(panel_rect.right - 55, 130)
        )
        canvas.blit(res_text, res_text_rect)

        arrow_text = font_section.render(
            "v",
            False,
            (235, 65, 40)
        )
        arrow_rect = arrow_text.get_rect(
            midright=(panel_rect.right - 20, 130)
        )
        canvas.blit(arrow_text, arrow_rect)

        # Fullscreen
        fullscreen_text = font_section.render(
            "Fullscreen:",
            False,
            (240, 240, 240)
        )
        fullscreen_text_rect = fullscreen_text.get_rect(
            midleft=(panel_rect.left + 25, 175)
        )
        canvas.blit(fullscreen_text, fullscreen_text_rect)

        fullscreen_value = font_section.render(
            "ON" if fullscreen else "OFF",
            False,
            (235, 65, 40)
        )
        fullscreen_value_rect = fullscreen_value.get_rect(
            midright=(panel_rect.right - 55, 175)
        )
        canvas.blit(fullscreen_value, fullscreen_value_rect)

        # Brightness
        bright_label = font_section.render(
            "Brightness:",
            False,
            (240, 240, 240)
        )
        bright_label_rect = bright_label.get_rect(
            midleft=(panel_rect.left + 25, 250)
        )
        canvas.blit(bright_label, bright_label_rect)

        slider_x = 270
        slider_y = 243
        slider_width = 220

        pygame.draw.rect(
            canvas,
            (60, 60, 70),
            (slider_x, slider_y, slider_width, 14),
            2
        )

        handle_x = slider_x + (brightness / 100 * slider_width)

        pygame.draw.rect(
            canvas,
            (235, 65, 40),
            (handle_x - 4, slider_y - 5, 8, 24)
        )

        # Back button
        back_text = font_section.render(
            "Back",
            False,
            (240, 240, 240)
        )
        back_rect = back_text.get_rect(
            center=(base_res_x / 2, 330)
        )

        mouse_x = pygame.mouse.get_pos()[0] * base_res_x / screen_state_w
        mouse_y = pygame.mouse.get_pos()[1] * base_res_y / screen_state_h

        if back_rect.collidepoint(mouse_x, mouse_y):
            back_text = font_section.render(
                "Back",
                False,
                (235, 65, 40)
            )

        # Resolution dropdown
        if dropdown_open:

            dropdown_height = len(resolution_options) * 30

            dropdown_rect = pygame.Rect(
                270,
                145,
                245,
                dropdown_height
            )

            pygame.draw.rect(
                canvas,
                (15, 15, 20),
                dropdown_rect
            )

            pygame.draw.rect(
                canvas,
                (60, 60, 70),
                dropdown_rect,
                2
            )

            for index, option in enumerate(resolution_options):

                option_text = font_small.render(
                    f"{option[0]}x{option[1]}",
                    False,
                    (240, 240, 240)
                )

                option_rect = option_text.get_rect(
                    midleft=(dropdown_rect.left + 12, 160 + (index * 30))
                )

                canvas.blit(option_text, option_rect)

        canvas.blit(back_text, back_rect)

    # CONTROLS sub-screen
    elif current_state == "CONTROLS":

        controls_title = font_title.render(
            "Controls",
            False,
            (240, 240, 240)
        )
        controls_title_rect = controls_title.get_rect(
            center=(base_res_x / 2, 35)
        )
        canvas.blit(controls_title, controls_title_rect)

        controls_subtitle = font_section.render(
            "[ INPUT CONFIGURATION ]",
            False,
            (140, 140, 140)
        )
        controls_subtitle_rect = controls_subtitle.get_rect(
            center=(base_res_x / 2, 68)
        )
        canvas.blit(controls_subtitle, controls_subtitle_rect)

        panel_rect = pygame.Rect(80, 95, 480, 185)

        pygame.draw.rect(
            canvas,
            (25, 25, 30),
            panel_rect,
            2
        )

        controls = [
            ("Move Up", "W"),
            ("Move Left", "A"),
            ("Move Down", "S"),
            ("Move Right", "D"),
            ("Jump", "Space")
        ]

        for index, (action, key) in enumerate(controls):

            row_y = 118 + (index * 31)

            action_text = font_section.render(
                action,
                False,
                (240, 240, 240)
            )
            action_rect = action_text.get_rect(
                midleft=(panel_rect.left + 25, row_y)
            )
            canvas.blit(action_text, action_rect)

            key_text = font_section.render(
                key,
                False,
                (235, 65, 40)
            )
            key_rect = key_text.get_rect(
                midright=(panel_rect.right - 25, row_y)
            )
            canvas.blit(key_text, key_rect)

        # Back button
        back_text = font_section.render(
            "Back",
            False,
            (240, 240, 240)
        )
        back_rect = back_text.get_rect(
            center=(base_res_x / 2, 330)
        )

        mouse_x = pygame.mouse.get_pos()[0] * base_res_x / screen_state_w
        mouse_y = pygame.mouse.get_pos()[1] * base_res_y / screen_state_h

        if back_rect.collidepoint(mouse_x, mouse_y):
            back_text = font_section.render(
                "Back",
                False,
                (235, 65, 40)
            )

        canvas.blit(back_text, back_rect)


    # AUDIO sub-screen
    elif current_state == "AUDIO":

        audio_title = font_title.render(
            "Audio",
            False,
            (240, 240, 240)
        )
        audio_title_rect = audio_title.get_rect(
            center=(base_res_x / 2, 35)
        )
        canvas.blit(audio_title, audio_title_rect)

        audio_subtitle = font_section.render(
            "[ AUDIO & SOUND ]",
            False,
            (140, 140, 140)
        )
        audio_subtitle_rect = audio_subtitle.get_rect(
            center=(base_res_x / 2, 68)
        )
        canvas.blit(audio_subtitle, audio_subtitle_rect)

        panel_rect = pygame.Rect(60, 95, 520, 190)

        pygame.draw.rect(
            canvas,
            (25, 25, 30),
            panel_rect,
            2
        )

        audio_settings = [
            ("Master Volume", master_volume),
            ("Music Volume", music_volume),
            ("SFX Volume", sfx_volume)
        ]

        slider_x = 255
        slider_width = 250

        for index, (label, value) in enumerate(audio_settings):

            row_y = 130 + (index * 48)

            label_text = font_section.render(
                label,
                False,
                (240, 240, 240)
            )
            label_rect = label_text.get_rect(
                midleft=(panel_rect.left + 20, row_y)
            )
            canvas.blit(label_text, label_rect)

            slider_y = row_y - 7

            pygame.draw.rect(
                canvas,
                (60, 60, 70),
                (slider_x, slider_y, slider_width, 14),
                2
            )

            handle_x = slider_x + (value / 100 * slider_width)

            pygame.draw.rect(
                canvas,
                (235, 65, 40),
                (handle_x - 4, slider_y - 5, 8, 24)
            )

            value_text = font_small.render(
                f"{value}%",
                False,
                (140, 140, 140)
            )
            value_rect = value_text.get_rect(
                midleft=(slider_x + slider_width + 12, row_y)
            )
            canvas.blit(value_text, value_rect)

        # Back button
        back_text = font_section.render(
            "Back",
            False,
            (240, 240, 240)
        )
        back_rect = back_text.get_rect(
            center=(base_res_x / 2, 330)
        )

        mouse_x = pygame.mouse.get_pos()[0] * base_res_x / screen_state_w
        mouse_y = pygame.mouse.get_pos()[1] * base_res_y / screen_state_h

        if back_rect.collidepoint(mouse_x, mouse_y):
            back_text = font_section.render(
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

                fullscreen = False
                status = pygame.RESIZABLE

                screen_state_w = window_w
                screen_state_h = window_h

                screen = pygame.display.set_mode(
                    (screen_state_w, screen_state_h),
                    status
                )

            elif event.key == pygame.K_F11:

                fullscreen = True
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

                                current_state = "OPTIONS"
                                selected_option = None
                                dropdown_open = False

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

                                    open_save(index)


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


                elif current_state == "OPTIONS":

                    # Handle back button
                    back_rect = pygame.Rect(
                        0,
                        310,
                        base_res_x,
                        40
                    )

                    if back_rect.collidepoint(mouse_pos):
                        current_state = "MAIN"
                        selected_option = None
                        dropdown_open = False

                    # Handle menu cards
                    option_cards = [
                        "Audio Settings",
                        "Video Settings",
                        "Controls"
                    ]

                    for index, option in enumerate(option_cards):

                        card_rect = pygame.Rect(
                            100,
                            95 + (index * 55),
                            440,
                            40
                        )

                        if card_rect.collidepoint(mouse_pos):

                            if option == "Audio Settings":
                                current_state = "AUDIO"
                                dropdown_open = False

                            elif option == "Video Settings":
                                current_state = "VIDEO"
                                dropdown_open = False

                            elif option == "Controls":
                                current_state = "CONTROLS"
                                dropdown_open = False


                elif current_state == "VIDEO":

                    # Back button
                    back_rect = pygame.Rect(
                        0,
                        310,
                        base_res_x,
                        40
                    )

                    if back_rect.collidepoint(mouse_pos):
                        current_state = "OPTIONS"
                        dropdown_open = False

                    # Resolution selector
                    resolution_rect = pygame.Rect(
                        270,
                        112,
                        245,
                        36
                    )

                    if resolution_rect.collidepoint(mouse_pos):
                        dropdown_open = not dropdown_open

                    # Resolution dropdown choices
                    elif dropdown_open:

                        for index, option in enumerate(resolution_options):

                            dropdown_rect = pygame.Rect(
                                270,
                                145 + (index * 30),
                                245,
                                30
                            )

                            if dropdown_rect.collidepoint(mouse_pos):
                                selected_resolution = index
                                dropdown_open = False
                                
                                # Get the selected (width, height) from resolution_options using selected_resolution
                                selected_width, selected_height = resolution_options[selected_resolution]
                                
                                # Set the existing window_w and window_h variables to that width and height
                                window_w = selected_width
                                window_h = selected_height
                                
                                # Only update the active window when in windowed mode
                                if status == pygame.RESIZABLE:
                                    screen_state_w = window_w
                                    screen_state_h = window_h
                                    
                                    screen = pygame.display.set_mode(
                                        (screen_state_w, screen_state_h),
                                        status
                                    )
                                
                                break

                    # Fullscreen toggle
                    fullscreen_rect = pygame.Rect(
                        450,
                        157,
                        60,
                        36
                    )

                    if fullscreen_rect.collidepoint(mouse_pos):

                        fullscreen = not fullscreen

                        if fullscreen:
                            status = pygame.FULLSCREEN
                            screen_state_w = display_w
                            screen_state_h = display_h

                            screen = pygame.display.set_mode(
                                (display_w, display_h),
                                status
                            )

                        else:
                            status = pygame.RESIZABLE
                            screen_state_w = window_w
                            screen_state_h = window_h

                            screen = pygame.display.set_mode(
                                (screen_state_w, screen_state_h),
                                status
                            )

                    # Brightness slider
                    brightness_slider_rect = pygame.Rect(
                        270,
                        241,
                        220,
                        18
                    )

                    if brightness_slider_rect.collidepoint(mouse_pos):
                        drag = True
                        dragging_slider = "brightness"
                        brightness = int(
                            (mouse_x - 270) / 220 * 100
                        )
                        brightness = max(0, min(100, brightness))


                elif current_state == "CONTROLS":

                    back_rect = pygame.Rect(
                        0,
                        310,
                        base_res_x,
                        40
                    )

                    if back_rect.collidepoint(mouse_pos):
                        current_state = "OPTIONS"


                elif current_state == "AUDIO":

                    back_rect = pygame.Rect(
                        0,
                        310,
                        base_res_x,
                        40
                    )

                    if back_rect.collidepoint(mouse_pos):
                        current_state = "OPTIONS"

                    # Audio slider hitboxes
                    audio_sliders = [
                        ("master", 130),
                        ("music", 178),
                        ("sfx", 226)
                    ]

                    for slider_name, slider_y in audio_sliders:

                        slider_rect = pygame.Rect(
                            255,
                            slider_y - 9,
                            250,
                            18
                        )

                        if slider_rect.collidepoint(mouse_pos):
                            drag = True
                            dragging_slider = slider_name

                            value = int(
                                (mouse_x - 255) / 250 * 100
                            )
                            value = max(0, min(100, value))

                            if slider_name == "master":
                                master_volume = value
                            elif slider_name == "music":
                                music_volume = value
                            elif slider_name == "sfx":
                                sfx_volume = value

                            break

    # Continuous slider dragging
    if drag:

        if pygame.mouse.get_pressed()[0]:

            mouse_x = pygame.mouse.get_pos()[0] * base_res_x / screen_state_w

            if dragging_slider == "brightness" and current_state == "VIDEO":
                brightness = int(
                    (mouse_x - 270) / 220 * 100
                )
                brightness = max(0, min(100, brightness))

            elif dragging_slider == "master" and current_state == "AUDIO":
                master_volume = int(
                    (mouse_x - 255) / 250 * 100
                )
                master_volume = max(0, min(100, master_volume))

            elif dragging_slider == "music" and current_state == "AUDIO":
                music_volume = int(
                    (mouse_x - 255) / 250 * 100
                )
                music_volume = max(0, min(100, music_volume))

            elif dragging_slider == "sfx" and current_state == "AUDIO":
                sfx_volume = int(
                    (mouse_x - 255) / 250 * 100
                )
                sfx_volume = max(0, min(100, sfx_volume))

        else:
            drag = False
            dragging_slider = None

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