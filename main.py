import random
import sys
import subprocess

import pygame
from perlin_noise import PerlinNoise
from pygame.locals import *

from player import Player, Player_Sprite
from spritesheet import Spritesheet
from tilemap import *
from save_system import save_game, load_game
from settings_system import load_settings, save_settings

# Safely get the brightness argument, default to 50, and keep it between 0 and 100.
brightness = 50
if "--brightness" in sys.argv:
    brightness = int(sys.argv[sys.argv.index("--brightness") + 1])
    brightness = max(0, min(100, brightness))

save_slot = 0
if "--save-slot" in sys.argv:
    save_slot = int(sys.argv[sys.argv.index("--save-slot") + 1])

# Actual Brightness Calculations
def create_brightness_surface(value):
    # 0 = 65% brightness, 50 = 100%, 100 = 125%.
    brightness_surface = pygame.Surface((base_res_x, base_res_y))

    if value < 50:
        factor = 0.65 + (value / 50.0) * 0.35
        rgb_value = int(factor * 255)
        brightness_surface.fill((rgb_value, rgb_value, rgb_value))
    elif value > 50:
        factor = 1.0 + ((value - 50) / 50.0) * 0.25
        add_value = int((factor - 1.0) * 255)
        brightness_surface.fill((add_value, add_value, add_value))

    return brightness_surface


pygame.init()

#grab resolution for the users monitor
resolution = pygame.display.get_desktop_sizes()
#baseline resolution
base_res_x, base_res_y = 640, 360        

display_w , display_h = resolution[0]   #index 0 for the first monitor   
window_w, window_h = 1280,720
screen_state_w, screen_state_h = window_w, window_h

# Load the same settings used by the main menu.
settings = load_settings()
resolution_options = [
    (640, 360),
    (1280, 720),
    (1920, 1080)
]
selected_resolution = max(0, min(len(resolution_options) - 1, settings["resolution_index"]))
window_w, window_h = resolution_options[selected_resolution]
fullscreen = settings["fullscreen"]
brightness = settings["brightness"]
master_volume = settings["master_volume"]
music_volume = settings["music_volume"]
sfx_volume = settings["sfx_volume"]
controls = settings.get("controls", {})

if fullscreen:
    status = FULLSCREEN
    screen_state_w, screen_state_h = display_w, display_h
else:
    status = RESIZABLE
    screen_state_w, screen_state_h = window_w, window_h

control_keys = {
    "up": pygame.key.key_code(controls.get("up", "W").lower()),
    "left": pygame.key.key_code(controls.get("left", "A").lower()),
    "down": pygame.key.key_code(controls.get("down", "S").lower()),
    "right": pygame.key.key_code(controls.get("right", "D").lower()),
    "jump": pygame.key.key_code(controls.get("jump", "Space").lower())
}

#camera movement
camera_x=0 #made it the same as the player's coordinates
camera_y=0 #made it the same as the player's coordinates
camera_speed=5 #will make this the difference in current player coordinates 


#1. initiliaze pygame, 2. names the window, 3. sets the window size and sets its paramaters
pygame.display.set_caption("Return To Sender") 
canvas = pygame.Surface((base_res_x, base_res_y))
screen = pygame.display.set_mode((screen_state_w, screen_state_h), status)

brightness_surface = create_brightness_surface(brightness)


clock = pygame.time.Clock() #assigning the clock function to a variable to use for the fps in the gameloop

# pause menu fonts
font_pause_title = pygame.font.Font("fonts/Press_Start_2P/PressStart2P.ttf", 24)
font_pause = pygame.font.Font("fonts/VT323/VT323.ttf", 34)
font_pause_small = pygame.font.Font("fonts/VT323/VT323.ttf", 26)

# *-- MAP STUFF --*
sprites = Spritesheet('spritesheet.png')

tile_size = 32
#16 tiles / chunk
chunk_tiles_x = 16
chunk_tiles_y = 16

chunk_pixel_w = chunk_tiles_x*tile_size
chunk_pixel_h = chunk_tiles_y*tile_size

render_distance = 2
loaded_chunks = {}
set_seed = 1234

#Surface_Level
noise_1d = PerlinNoise(octaves=2, seed = int(set_seed))
#Caves
noise_2d = PerlinNoise(octaves=3, seed = int(set_seed))


def world_to_chunk(world_x,world_y):
    chunk_coordinate_x, chunk_coordinate_y = int(world_x//chunk_pixel_w), int(world_y//chunk_pixel_h)
    return chunk_coordinate_x, chunk_coordinate_y

def generate_chunk_data(chunk_x, chunk_y):
    grid = []
    surface_scale = 0.02
    cave_scale = 0.04
    base_height = 7
    amplitude = 10

    for y in range(chunk_tiles_y):
        row = []
        world_tile_y = chunk_y*chunk_tiles_y + y
        for x in range(chunk_tiles_x):
            world_tile_x = chunk_x*chunk_tiles_x + x

            noise_volume = noise_1d([world_tile_x*surface_scale])
            surface_y = base_height + int(noise_volume*amplitude)

            cave_volume = noise_2d([world_tile_x * cave_scale , world_tile_y * cave_scale])

            depth = world_tile_y - surface_y

            #the depth determines how deep the caves should go
            if depth < 0:
                row.append('-1')
            #surface Layer
            elif depth == 0:
                if cave_volume <= -0.25:
                    row.append('-1')
                else:
                    row.append('1')
            elif depth <4:
                if cave_volume <= -0.22:
                    row.append('-1')
                else:
                    row.append('11')
            #underground Caves
            else:
                cave_threshold = -0.01 + min(0.15, (depth-4)*0.01)

                if depth >20:
                    cave_threshold -= (depth-20)*0.02

                if cave_volume <= cave_threshold:
                    row.append('-1')
                else:
                    row.append('11')
            
                    
        grid.append(row)
    return grid

 
# *-----------------------------------------------------------PLAYER STUFF---------------------------------------------------------------------*

player = Player(
    Name=None,
    HP=None,    
    ATK=None, 
    CRIT_DMG=None, 
    CRIT_CHANCE=None, 
    LEVEL=None, 
    EXP=None, 
    DOLLARS=None, 
    S_COIN=None
)






moving_up = False
moving_down = False
moving_right = False
moving_left = False

player_y_momentum = 0 # <-- gravity enacted on the player
press_space = False
max_air_jumps = 2
air_jumps = max_air_jumps
on_ground = None
x_flip = False

# *--------------------------------------------ENTITIES-------------------------------------------------------*



#stores the rect of the zombies
zombies = []
#to use later for rendering pos
zombies_render_positions = [] #acts the same as player render pos.
zombies_movements = [] #holds the x and y values for zombie movement
zombie_ground_check = [] #holds boolean if zombie is in the air or not
zombie_move_choices = []
zombies_y_momentums = []
zombie_y_mom = 0
choice_count = 0 #stores the amount of frames it has been to make a new choice

for i in range(10):
    zombie = pygame.Rect(i*128, 200, 32,32)
    zombies.append(zombie)



zombie_sprite = pygame.image.load('animations/base_zombie.png')



# *------------------------------ANIMATION------------------------------------------------------------------------

jimmy_sheet = Spritesheet('animations/spritesheets/red_jimmy_sheet.png')

jimmy_frames = []
current_frames = []
index = 0
mode = 0
count = 0

# 0-5 idle, 6-10 walk, 11-14 jump, 15-17 fall
# -idle       
for i in range(6):
    filename = f'idle_{i}'
    jimmy_frames.append(jimmy_sheet.parse_sprite(filename))

# -walk
for i in range(5):
    filename = f'walk_{i}'
    jimmy_frames.append(jimmy_sheet.parse_sprite(filename))

# -jump
for i in range(4):
    filename = f'jump_{i}'
    jimmy_frames.append(jimmy_sheet.parse_sprite(filename))

# -fall
for i in range(3):
    filename = f'fall_{i}'
    jimmy_frames.append(jimmy_sheet.parse_sprite(filename))


# 0-5 idle, 6-10 walk, 11-14 jump, 15-17 fall
# 0=idle, 1=walk, 2=jump, 3=fall

def update_action (mod):

    if mod == 0: #idle
        current_frames = jimmy_frames[0:5]

    if mod == 1: #walk
        current_frames = jimmy_frames[6:10]

    if mod == 2: #jump
        current_frames = jimmy_frames[11:14]

    if mod == 3: #fall
        current_frames = jimmy_frames[15:17]

    return current_frames


def update_player_frame (mod, frame, tick): #math for frame 
    tick += 1

    if tick == 60:
        tick = 0

    if mod == 0: #idling
        frame = (tick // 10) % len(current_frames)

    if mod == 1: #walking
        frame = (tick // 12) % len(current_frames)
        
    if mod == 2: #jumping
        frame = (tick // 15) % len(current_frames)
        
    if mod == 3: #falling
        frame = (tick // 20) % len(current_frames)

    return tick, frame


player_rect = pygame.Rect(100, 200, 32, 32) #player hitbox
#                                   ^^  ^^ change this number to alter player hitbox

# Pause menu state
paused = False
pause_state = "PAUSE"
pause_options_state = "MAIN"
pause_dragging_slider = None
pause_dropdown_open = False
pause_rebinding_control = None

# Load the player's saved progress. Global settings such as brightness are
# kept separate from the save slot so the same settings are used everywhere.
load_game(save_slot, player, player_rect, brightness)
brightness_surface = create_brightness_surface(brightness)


def update_settings_file():
    save_settings({
        "resolution_index": selected_resolution,
        "fullscreen": fullscreen,
        "brightness": brightness,
        "master_volume": master_volume,
        "music_volume": music_volume,
        "sfx_volume": sfx_volume,
        "controls": controls
    })


def apply_audio_settings():
    # The project can use these values when mixer audio is added.
    if pygame.mixer.get_init():
        pygame.mixer.music.set_volume((master_volume / 100) * (music_volume / 100))


apply_audio_settings()



#note for rendering: whatever is first rendered in the loop will be behind while whatever is last rendered in the loop will be in the very front
# *--GAME LOOP--*
while True: 



    jump = False
        



       # *--INPUT DETECTION--*
    for event in pygame.event.get(): #just detects if any 'events' occur



        # *--QUIT--*
        if event.type == pygame.QUIT:
            update_settings_file()
            save_game(save_slot, player, player_rect, brightness)
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN and pause_rebinding_control is not None and paused and pause_state == "OPTIONS" and pause_options_state == "CONTROLS":
            controls[pause_rebinding_control] = pygame.key.name(event.key).title()
            control_keys[pause_rebinding_control] = event.key
            pause_rebinding_control = None
            update_settings_file()
            continue

        # ESC opens/closes the pause menu.
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if pause_state == "OPTIONS":
                if pause_options_state != "MAIN":
                    pause_options_state = "MAIN"
                else:
                    pause_state = "PAUSE"
            else:
                paused = not paused
            continue

        if event.type == pygame.KEYDOWN and event.key == pygame.K_F5:
            update_settings_file()
            save_game(save_slot, player, player_rect, brightness)
        # elif player_rect.right>total_map_w or player_rect.top <0 or player_rect.bottom> total_map_h:
        #     pygame.quit()
        #     sys.exit()
        # elif player_rect.left <0:
        #     player_rect.left = 1
        
        # Pause menu mouse controls
        if paused:
            mouse_x = event.pos[0] * base_res_x / screen_state_w if hasattr(event, "pos") else 0
            mouse_y = event.pos[1] * base_res_y / screen_state_h if hasattr(event, "pos") else 0

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if pause_state == "PAUSE":
                    pause_buttons = [
                        pygame.Rect(220, 105, 200, 38),
                        pygame.Rect(220, 150, 200, 38),
                        pygame.Rect(220, 195, 200, 38),
                        pygame.Rect(220, 240, 200, 38)
                    ]

                    if pause_buttons[0].collidepoint(mouse_x, mouse_y):
                        paused = False
                    elif pause_buttons[1].collidepoint(mouse_x, mouse_y):
                        pause_state = "OPTIONS"
                        pause_options_state = "MAIN"
                    elif pause_buttons[2].collidepoint(mouse_x, mouse_y):
                        update_settings_file()
                        save_game(save_slot, player, player_rect, brightness)
                    elif pause_buttons[3].collidepoint(mouse_x, mouse_y):
                        update_settings_file()
                        save_game(save_slot, player, player_rect, brightness)
                        pygame.quit()
                        subprocess.Popen([sys.executable, "main_menu.py"])
                        sys.exit()

                elif pause_state == "OPTIONS":
                    if pause_options_state == "MAIN":
                        option_cards = [
                            pygame.Rect(100, 95, 440, 40),
                            pygame.Rect(100, 150, 440, 40),
                            pygame.Rect(100, 205, 440, 40)
                        ]

                        if option_cards[0].collidepoint(mouse_x, mouse_y):
                            pause_options_state = "AUDIO"
                        elif option_cards[1].collidepoint(mouse_x, mouse_y):
                            pause_options_state = "VIDEO"
                        elif option_cards[2].collidepoint(mouse_x, mouse_y):
                            pause_options_state = "CONTROLS"
                        elif pygame.Rect(0, 310, base_res_x, 40).collidepoint(mouse_x, mouse_y):
                            pause_state = "PAUSE"

                    elif pause_options_state == "VIDEO":
                        if pygame.Rect(0, 310, base_res_x, 40).collidepoint(mouse_x, mouse_y):
                            pause_options_state = "MAIN"
                            pause_dropdown_open = False
                            pause_dragging_slider = None

                        resolution_rect = pygame.Rect(270, 112, 245, 36)
                        if resolution_rect.collidepoint(mouse_x, mouse_y):
                            pause_dropdown_open = not pause_dropdown_open

                        elif pause_dropdown_open:
                            for index, option in enumerate(resolution_options):
                                dropdown_rect = pygame.Rect(270, 145 + index * 30, 245, 30)
                                if dropdown_rect.collidepoint(mouse_x, mouse_y):
                                    selected_resolution = index
                                    pause_dropdown_open = False
                                    update_settings_file()
                                    window_w, window_h = resolution_options[index]
                                    if status == pygame.RESIZABLE:
                                        screen_state_w, screen_state_h = window_w, window_h
                                        screen = pygame.display.set_mode((screen_state_w, screen_state_h), status)
                                    break

                        fullscreen_rect = pygame.Rect(450, 157, 60, 36)
                        if fullscreen_rect.collidepoint(mouse_x, mouse_y):
                            fullscreen = not fullscreen
                            update_settings_file()
                            if fullscreen:
                                status = pygame.FULLSCREEN
                                screen_state_w, screen_state_h = display_w, display_h
                                screen = pygame.display.set_mode((display_w, display_h), status)
                            else:
                                status = pygame.RESIZABLE
                                screen_state_w, screen_state_h = window_w, window_h
                                screen = pygame.display.set_mode((screen_state_w, screen_state_h), status)

                        brightness_rect = pygame.Rect(270, 210, 220, 18)
                        if brightness_rect.collidepoint(mouse_x, mouse_y):
                            pause_dragging_slider = "brightness"
                            brightness = max(0, min(100, int((mouse_x - 270) / 220 * 100)))
                            brightness_surface = create_brightness_surface(brightness)
                            update_settings_file()

                    elif pause_options_state == "AUDIO":
                        if pygame.Rect(0, 310, base_res_x, 40).collidepoint(mouse_x, mouse_y):
                            pause_options_state = "MAIN"
                            pause_dragging_slider = None

                        audio_sliders = [("master", 130), ("music", 178), ("sfx", 226)]
                        for slider_name, slider_y in audio_sliders:
                            slider_rect = pygame.Rect(330, slider_y - 9, 190, 18)
                            if slider_rect.collidepoint(mouse_x, mouse_y):
                                pause_dragging_slider = slider_name
                                value = max(0, min(100, int((mouse_x - 330) / 190 * 100)))
                                if slider_name == "master":
                                    master_volume = value
                                elif slider_name == "music":
                                    music_volume = value
                                else:
                                    sfx_volume = value
                                break

                    elif pause_options_state == "CONTROLS":
                        if pygame.Rect(0, 310, base_res_x, 40).collidepoint(mouse_x, mouse_y):
                            pause_options_state = "MAIN"
                            pause_rebinding_control = None

                        control_rows = [
                            ("up", 105),
                            ("left", 137),
                            ("down", 169),
                            ("right", 201),
                            ("jump", 233)
                        ]

                        for control_name, row_y in control_rows:
                            control_rect = pygame.Rect(80, row_y - 15, 480, 30)
                            if control_rect.collidepoint(mouse_x, mouse_y):
                                pause_rebinding_control = control_name
                                break

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                pause_dragging_slider = None

            if event.type == pygame.MOUSEMOTION and pause_dragging_slider:
                if pause_dragging_slider == "brightness" and pause_options_state == "VIDEO":
                    brightness = max(0, min(100, int((mouse_x - 270) / 220 * 100)))
                    brightness_surface = create_brightness_surface(brightness)
                    update_settings_file()
                elif pause_dragging_slider in ("master", "music", "sfx") and pause_options_state == "AUDIO":
                    value = max(0, min(100, int((mouse_x - 330) / 190 * 100)))
                    if pause_dragging_slider == "master":
                        master_volume = value
                    elif pause_dragging_slider == "music":
                        music_volume = value
                    else:
                        sfx_volume = value
                    apply_audio_settings()
                    update_settings_file()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_F5:
                save_game(save_slot, player, player_rect, brightness)

            continue

        # *--KEY DETECTION--*

        # *--WINDOW CONTROLS--*
        if event.type == VIDEORESIZE and status == RESIZABLE:
                            window_w, window_h = event.w , event.h
                            screen_state_w, screen_state_h = window_w, window_h
                            screen = pygame.display.set_mode((screen_state_w, screen_state_h),status)

        if event.type == KEYDOWN:
            if event.key == K_F1:
                status = RESIZABLE
                screen_state_w, screen_state_h = window_w, window_h
                screen = pygame.display.set_mode((screen_state_w, screen_state_h), status)

            elif event.key == K_F11:
                status = FULLSCREEN
                screen_state_w, screen_state_h = display_w, display_h
                screen = pygame.display.set_mode((display_w,display_h), status)


            # *--KEY PRESSED--*
        if event.type == pygame.KEYDOWN:
            if event.key == control_keys["right"]: #pressing D (right)
                moving_right = True
            if event.key == control_keys["left"]: #pressing A (left)
                moving_left = True
            if event.key == control_keys["jump"]:
                press_space = True


            # *--KEY IS LET GO--*  
        if event.type == pygame.KEYUP:

            if event.key == control_keys["left"] and event.key == control_keys["right"] and event.key == control_keys["jump"]: #nothing is being touched
                mode = 0  
            if event.key == control_keys["up"]:#let go of W (up)
                moving_up = False
            if event.key == control_keys["down"]:#let go of S (down)
                moving_down = False
            if event.key == control_keys["right"]: #let go of D (right)
                moving_right = False
            if event.key == control_keys["left"]: #let go of A (left)
                moving_left = False

    # While paused, keep the last game frame visible and only draw the menu.
    if paused:
        display_canvas = canvas.copy()

        if brightness < 50:
            display_canvas.blit(brightness_surface, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
        elif brightness > 50:
            display_canvas.blit(brightness_surface, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

        pause_overlay = pygame.Surface((base_res_x, base_res_y), pygame.SRCALPHA)
        pause_overlay.fill((0, 0, 0, 150))
        display_canvas.blit(pause_overlay, (0, 0))

        mouse_pos = pygame.mouse.get_pos()
        mouse_x = mouse_pos[0] * base_res_x / screen_state_w
        mouse_y = mouse_pos[1] * base_res_y / screen_state_h

        if pause_state == "PAUSE":
            pause_title = font_pause_title.render("PAUSED", False, (240, 240, 240))
            display_canvas.blit(pause_title, pause_title.get_rect(center=(base_res_x / 2, 55)))

            pause_buttons = ["Resume", "Options", "Save", "Quit"]
            for index, option in enumerate(pause_buttons):
                button_rect = pygame.Rect(220, 105 + index * 45, 200, 38)
                selected_color = (235, 65, 40) if button_rect.collidepoint(mouse_x, mouse_y) else (240, 240, 240)
                option_text = font_pause.render(option, False, selected_color)
                display_canvas.blit(option_text, option_text.get_rect(center=button_rect.center))

        elif pause_state == "OPTIONS":
            options_panel = pygame.Surface((520, 285), pygame.SRCALPHA)
            options_panel.fill((15, 15, 20, 205))
            pygame.draw.rect(options_panel, (60, 60, 70, 255), options_panel.get_rect(), 2)
            display_canvas.blit(options_panel, (60, 45))

            if pause_options_state == "MAIN":
                options_title = font_pause_title.render("OPTIONS", False, (240, 240, 240))
                display_canvas.blit(options_title, options_title.get_rect(center=(base_res_x / 2, 65)))

                option_cards = ["Audio Settings", "Video Settings", "Controls"]
                for index, option in enumerate(option_cards):
                    card_rect = pygame.Rect(100, 95 + index * 55, 440, 40)
                    pygame.draw.rect(display_canvas, (25, 25, 30), card_rect, 2)
                    color = (235, 65, 40) if card_rect.collidepoint(mouse_x, mouse_y) else (240, 240, 240)
                    option_text = font_pause.render(option, False, color)
                    display_canvas.blit(option_text, option_text.get_rect(midleft=(card_rect.left + 20, card_rect.centery)))
                    arrow_text = font_pause.render(">", False, (235, 65, 40))
                    display_canvas.blit(arrow_text, arrow_text.get_rect(midright=(card_rect.right - 20, card_rect.centery)))

            elif pause_options_state == "VIDEO":
                title = font_pause_title.render("VIDEO", False, (240, 240, 240))
                display_canvas.blit(title, title.get_rect(center=(base_res_x / 2, 65)))

                res_label = font_pause.render("Resolution:", False, (240, 240, 240))
                display_canvas.blit(res_label, res_label.get_rect(midleft=(105, 120)))
                res_value = font_pause.render(f"{resolution_options[selected_resolution][0]}x{resolution_options[selected_resolution][1]}", False, (235, 65, 40))
                display_canvas.blit(res_value, res_value.get_rect(midright=(525, 120)))

                fs_label = font_pause.render("Fullscreen:", False, (240, 240, 240))
                display_canvas.blit(fs_label, fs_label.get_rect(midleft=(105, 165)))
                fs_value = font_pause.render("ON" if fullscreen else "OFF", False, (235, 65, 40))
                display_canvas.blit(fs_value, fs_value.get_rect(midright=(525, 165)))

                bright_label = font_pause.render("Brightness:", False, (240, 240, 240))
                display_canvas.blit(bright_label, bright_label.get_rect(midleft=(105, 220)))
                slider_x, slider_y, slider_width = 270, 210, 220
                pygame.draw.rect(display_canvas, (60, 60, 70), (slider_x, slider_y, slider_width, 14), 2)
                handle_x = slider_x + (brightness / 100 * slider_width)
                pygame.draw.rect(display_canvas, (235, 65, 40), (handle_x - 4, slider_y - 5, 8, 24))
                value_text = font_pause_small.render(f"{brightness}%", False, (235, 65, 40))
                display_canvas.blit(value_text, value_text.get_rect(midleft=(105, 255)))

                if pause_dropdown_open:
                    dropdown_rect = pygame.Rect(270, 145, 245, len(resolution_options) * 30)
                    pygame.draw.rect(display_canvas, (15, 15, 20), dropdown_rect)
                    pygame.draw.rect(display_canvas, (60, 60, 70), dropdown_rect, 2)
                    for index, option in enumerate(resolution_options):
                        option_text = font_pause_small.render(f"{option[0]}x{option[1]}", False, (240, 240, 240))
                        display_canvas.blit(option_text, option_text.get_rect(midleft=(dropdown_rect.left + 12, 160 + index * 30)))

            elif pause_options_state == "AUDIO":
                title = font_pause_title.render("AUDIO", False, (240, 240, 240))
                display_canvas.blit(title, title.get_rect(center=(base_res_x / 2, 65)))
                audio_settings = [("Master Volume", master_volume), ("Music Volume", music_volume), ("SFX Volume", sfx_volume)]
                for index, (label, value) in enumerate(audio_settings):
                    row_y = 120 + index * 48
                    label_text = font_pause.render(label, False, (240, 240, 240))
                    display_canvas.blit(label_text, label_text.get_rect(midleft=(105, row_y)))
                    slider_x, slider_y, slider_width = 330, row_y - 7, 190
                    pygame.draw.rect(display_canvas, (60, 60, 70), (slider_x, slider_y, slider_width, 14), 2)
                    handle_x = slider_x + (value / 100 * slider_width)
                    pygame.draw.rect(display_canvas, (235, 65, 40), (handle_x - 4, slider_y - 5, 8, 24))
                    value_text = font_pause_small.render(f"{value}%", False, (140, 140, 140))
                    display_canvas.blit(value_text, value_text.get_rect(midleft=(532, row_y)))

            elif pause_options_state == "CONTROLS":
                title = font_pause_title.render("CONTROLS", False, (240, 240, 240))
                display_canvas.blit(title, title.get_rect(center=(base_res_x / 2, 65)))
                control_rows = [
                    ("Move Up", controls.get("up", "W")),
                    ("Move Left", controls.get("left", "A")),
                    ("Move Down", controls.get("down", "S")),
                    ("Move Right", controls.get("right", "D")),
                    ("Jump", controls.get("jump", "Space"))
                ]
                for index, (action, key) in enumerate(control_rows):
                    row_y = 105 + index * 32
                    control_name = ["up", "left", "down", "right", "jump"][index]
                    if pause_rebinding_control == control_name:
                        key = "Press a key..."
                    action_text = font_pause.render(action, False, (240, 240, 240))
                    key_text = font_pause.render(key, False, (235, 65, 40))
                    display_canvas.blit(action_text, action_text.get_rect(midleft=(105, row_y)))
                    display_canvas.blit(key_text, key_text.get_rect(midright=(525, row_y)))

            back_text = font_pause.render("Back", False, (235, 65, 40) if pygame.Rect(0, 310, base_res_x, 40).collidepoint(mouse_x, mouse_y) else (240, 240, 240))
            display_canvas.blit(back_text, back_text.get_rect(center=(base_res_x / 2, 330)))

        scaled_resolution = pygame.transform.scale(display_canvas, (screen_state_w, screen_state_h))
        screen.blit(scaled_resolution, (0, 0))
        pygame.display.update()
        clock.tick(60)
        continue

    #chunk manager
    position_chunk_x , position_chunk_y = world_to_chunk(player_rect.centerx, player_rect.centery)
    needed_chunks = set()

    for chunk_y in range(position_chunk_y - render_distance, position_chunk_y + render_distance + 1):
        for chunk_x in range (position_chunk_x - render_distance, position_chunk_x + render_distance + 1):
            chunk_key = (chunk_x,chunk_y)
            needed_chunks.add(chunk_key)

            if chunk_key not in loaded_chunks:
                raw_data = generate_chunk_data(chunk_x,chunk_y)
                loaded_chunks[chunk_key] = TileMap(raw_data,sprites, tile_size)

    for chunk_key in list(loaded_chunks.keys()):
        if chunk_key not in needed_chunks:
            del loaded_chunks[chunk_key]

    tile_rect = []
    for (chunk_x,chunk_y), tile_map in loaded_chunks.items():
        chunk_world_x = chunk_x * chunk_pixel_w
        chunk_world_y = chunk_y * chunk_pixel_h
        tile_rect.extend(tile_map.get_rects(chunk_world_x,chunk_world_y))

    # *---------------------------------------------------------------------------

    # *--PLAYER HORIZONTAL MOVEMENT + COLLISIONS--*

    player_movement = [0,0]  

    #left and right movement
    if moving_right == True:
        player_movement[0]= 4
        player_rect.x += player_movement[0]

    if moving_left == True:
        player_movement[0]= -4
        player_rect.x += player_movement[0]

    #collisions
    for tile in tile_rect:    
        if player_rect.colliderect(tile):
            if player_movement[0] > 0:
                player_rect.right = tile.left

            if player_movement[0] < 0:
                player_rect.left = tile.right

#---------------------------------------------------------------------

    # *-- PLAYER VERTICAL MOVEMENT + VERTICAL COLLISIONS --*
    
    #PLAYER
    #gravity
    player_movement[1] = player_y_momentum
    
    player_y_momentum += 0.2
    if player_y_momentum > 10:
        player_y_momentum = 10

    if player_y_momentum >= 0 and player_y_momentum <= 1: #checks if player is in the air
        pass
    else:
        on_ground = False

    player_rect.y += player_movement[1]

    


    for tile in tile_rect:
        if player_rect.colliderect(tile):
            if player_movement[1] > 0:
                player_rect.bottom = tile.top
                player_y_momentum = 0 # <-- basically tells the game that i can stop falling now
                on_ground = True
        
            if player_movement[1] < 0:
                player_rect.top = tile.bottom
                player_y_momentum = 0 # <-- same with this


    #                    *--JUMP--*
    
    #positive y momentum is downward | negative y momentum is upward
    if press_space == True:
        if on_ground is True: #player touching ground
            jump = True
            air_jumps = max_air_jumps
        else: #player is in the air
            if air_jumps > 0: #if player has an extra jump, then jump then deduct from remaining jumps
                jump = True
                air_jumps -= 1
            else:
                pass
    else:
         pass

    press_space = False #just returns it back to the original state so it doesn't infintely jump

    if jump == True:
        player_y_momentum = -4.5

# *---------------------------------------ENTITIES---------------------------------------------------------*


    

    # 60*x frames to tell the game to change what action the zombies should be doing
    choice_count += 1
    if choice_count >= 120: #120 means every 2 seconds since 60x2=120
        choice_count = 0
        change_action = True
    else:
        change_action = False

    #IF 
    if change_action == True:
        zombie_move_choices = []
        for i in range(len(zombies)):
            #determining left and right movement
                action_pool = ['Left', 'Right', 'Still']
                action_weightage = [15,15,70]
                zombie_action = random.choices(action_pool, weights=action_weightage, k=1)[0]
                zombie_move_choices.append(zombie_action)
                

    #ZOMBIE MOVEMENT
    zombies_movements = []
    for i in range(len(zombies)):
        zombie_move = [0,0]

        
        if len(zombie_move_choices) != 0:
            #move right
            if zombie_move_choices[i] == 'Right':
                zombie_move[0] = 2
                zombies[i].x += zombie_move[0]

            #move left
            if zombie_move_choices[i] == 'Left':
                zombie_move[0]= -2
                zombies[i].x += zombie_move[0]

            #dont move
            if zombie_move_choices[i] == 'Still':
                pass

        else: 
            pass
        
        zombies_movements.append(zombie_move)

    

    #ZOMBIE HORIZONTAL MOVEMENT
    for tile in tile_rect:    
        for i in range(len(zombies)):
            if zombies[i].colliderect(tile):
                if zombies_movements[i][0] > 0:
                    zombies[i].right = tile.left

                if zombies_movements[i][0] < 0:
                    zombies[i].left = tile.right
            
    #ZOMBIE VERTICAL MOVEMENT AND GRAVITY + VERTICAL COLLISION

    zombies_y_momentums = []
    for i in range(len(zombies)):
        zombies_movements[i][1] = zombie_y_mom
        zombie_y_mom += 0.2
        if zombie_y_mom > 4.5:
            zombie_y_mom = 4.5
        
        zombies_y_momentums.append(zombie_y_mom)

        if zombies_y_momentums[i] >= 0 and zombies_y_momentums[i] <= 1: #checks if zombie is in the air
            pass
        else:
            zombie_on_ground = False

        zombies[i].y += zombies_movements[i][1]

        for tile in tile_rect:
            if zombies[i].colliderect(tile):
                if zombies_movements[i][1] > 0:
                    zombies[i].bottom = tile.top
                    zombies_y_momentums[i] = 0 # <-- basically tells the game that i can stop falling now
                    zombie_on_ground = True
            
                if zombies_movements[i][1] < 0:
                    zombies[i].top = tile.bottom
                    zombies_y_momentums[i] = 0 # <-- same with this


                                # *--ANIMATION--*
 #-----------------------------------------------------------------------------------------------------
    #chooses what type of action the player is doing to then determine animation playing

    if on_ground == False and player_y_momentum > 0: #falling animation
        mode = 3
    elif on_ground == False and player_y_momentum <= 0: #jumping animation
        mode = 2
    elif moving_right or moving_left:
        mode = 1
    else: #idle
        mode = 0


                                # *--RENDERING--*
 #----------------------------------------------------------------------------------------------------------

    # void
    if player_rect.y > 2000:
        player_rect.x, player_rect.y = 250,100
        player_y_momentum = 0


    # *--CAMERA MOVEMENT--*
    #these 2 centers the player within the base canvas
    camera_x = player_rect.centerx - (base_res_x // 2) 
    camera_y = player_rect.centery - (base_res_y // 2)

     #map clamping      
    # max_cam_x = total_map_w - base_res_x
    # max_cam_y = total_map_h - base_res_y

    # camera_x = max(0, min(camera_x, max_cam_x))
    # camera_y = max(0, min(camera_y, max_cam_y))



    canvas.fill((159, 215, 255))    #nice sky background
    # current_y= 0

    # #filtering through the top and bottom layer in maps
    # for row in maps:            
    #     current_x = 0
    #     #filtering through each screen in each row
    #     for tile_map in row:
    #         #drawing the map with respect to each offset
    #         tile_map.draw_map(canvas, camera_x, camera_y, offset_x = current_x, offset_y = current_y)
    #         #updating x offset
    #         current_x += tile_map.map_w
    #     #updating y offset
    #     current_y += row[0].map_h

    for (chunk_x,chunk_y), tile_map in loaded_chunks.items():
        chunk_world_x = chunk_x * chunk_pixel_w
        chunk_world_y = chunk_y * chunk_pixel_h
        tile_map.draw_map(canvas, camera_x, camera_y,offset_x=chunk_world_x,offset_y=chunk_world_y)

    player_render_pos = (player_rect.x - camera_x, player_rect.y - camera_y) #centers player on screen



    zombies_render_positions = []
    for i in range(len(zombies)):
        zombie_render_pos = (zombies[i].x - camera_x, zombies[i].y - camera_y)
        zombies_render_positions.append(zombie_render_pos)

    #flipping code
    
    if moving_left == True:
        x_flip = True
    elif moving_right == True:
        x_flip = False
    else:
         pass

 
    current_frames = update_action(mode) #determines the current type of animation playing
    count, index = update_player_frame(mode, index, count) #update frame played
    player_sprite = current_frames[index] #determines the image/sprite which will be displayed on player pos
    canvas.blit(pygame.transform.flip(player_sprite, x_flip, False), player_render_pos) 

    for i in range(len(zombies)):
        canvas.blit(zombie_sprite, (zombies_render_positions[i]))

     

    #^^ draws the player onto the location of its hitbox*
    # x_flip tells the game whether it should flip the direction of the sprite on the x axis or not.
    # all sprites are all originally drawn to the right side.

    # Apply brightness to a copy so the base game frame stays unchanged.
    display_canvas = canvas.copy()
    if brightness < 50:
        display_canvas.blit(brightness_surface, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
    elif brightness > 50:
        display_canvas.blit(brightness_surface, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    #scale the screen
    scaled_resolution = pygame.transform.scale(display_canvas, (screen_state_w, screen_state_h))

    screen.blit(scaled_resolution,(0,0))   #creates a window to be displayed

    pygame.display.update() #updates the screen
    clock.tick(60) #ensures framerate is consistently 60fps