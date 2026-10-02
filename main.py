import random
import subprocess
import sys

import pygame
from perlin_noise import PerlinNoise
from pygame.locals import *

from entity import Orb, Player, Zombie, zombies
from save_system import load_game, save_game
from settings_system import load_settings, save_settings
from skill_tree import SkillTreeState, SkillTreeUI, apply_skill_effects
from spritesheet import Spritesheet
from tilemap import *
from world import World_Generation

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
x_camera_delay = 0
y_camera_delay = 0
camera_speed=5 #will make this the difference in current player coordinates 


#1. initiliaze pygame, 2. names the window, 3. sets the window size and sets its paramaters
pygame.display.set_caption("Return To Sender") 
canvas = pygame.Surface((base_res_x, base_res_y))
screen = pygame.display.set_mode((screen_state_w, screen_state_h), status)

brightness_surface = create_brightness_surface(brightness)


clock = pygame.time.Clock() #assigning the clock function to a variable to use for the fps in the gameloop


font_pause_title = pygame.font.Font("fonts/Press_Start_2P/PressStart2P.ttf", 24)
font_pause = pygame.font.Font("fonts/VT323/VT323.ttf", 34)
font_pause_small = pygame.font.Font("fonts/VT323/VT323.ttf", 26)

# *------------------------------------------------------------------- MAP STUFF -----------------------------------------------------------------------------------------*
current_spritesheet = None
current_map_seed = None
zombie_count = 1

tile_size = 32
chunk_tiles_x = 16
chunk_tiles_y = 16

chunk_pixel_w = chunk_tiles_x*tile_size
chunk_pixel_h = chunk_tiles_y*tile_size

set_seed = random.randint(1,10000)

world = World_Generation(
    tile_size = tile_size,
    chunk_tiles_x = chunk_tiles_x,
    chunk_tiles_y= chunk_tiles_y,
    noise1d=PerlinNoise(octaves=2, seed = int(set_seed)),
    noise2d=PerlinNoise(octaves=3, seed = int(set_seed))
)

render_distance = 2

# *-----------------------------------------------------------PLAYER STUFF---------------------------------------------------------------------*

player = Player(
    Name=None,
    rect = pygame.Rect(100, 200, 32, 32),
    movement=[0,0],
    moving_up = False,
    moving_down = False,
    moving_right = False,
    moving_left = False,
    press_space = False,
    aim_up = False,
    aim_down = False,
    aim_right = False,
    aim_left = False,
    y_momentum = 0,
    max_air_jumps = 2,
    jump = False,
    jump_height = 4.5,
    on_ground = None,
    x_flip = False,
    all_frames = [],
    current_frames = [],
    frame_index = 0,
    animation_mode = 0,
    animation_count = 0,    
    max_HP = 50,
    damaged=False,
    base_ATK=5, 
    attack_dir = None,
    first_hit_count = 0,
    combo_tick = 0,
    combo_stage = 0,
    first_hit_cooldown = 120,
    combo_cooldown = 20,
    combo_window = 0,
    max_combo_window = 25,
    attacking = False,
    attacked = False,
    CRIT_DMG=None, 
    CRIT_CHANCE=None, 
    LEVEL=None, 
    EXP=None, 
    DOLLARS=None, 
    S_COIN=None
)

player_rect = player.rect

# *--------------------------------------------ENTITIES-------------------------------------------------------*

choice_count = 0
zombie_sprite = pygame.image.load('animations/base_zombie.png')

# *------------------------------ANIMATION------------------------------------------------------------------------

jimmy_sheet = Spritesheet('animations/spritesheets/red_jimmy_sheet2.png')

for i in range(6):
    filename = f'idle_{i}'
    player.all_frames.append(jimmy_sheet.parse_sprite(filename))

for i in range(5):
    filename = f'walk_{i}'
    player.all_frames.append(jimmy_sheet.parse_sprite(filename))

for i in range(4):
    filename = f'jump_{i}'
    player.all_frames.append(jimmy_sheet.parse_sprite(filename))

for i in range(3):
    filename = f'fall_{i}'
    player.all_frames.append(jimmy_sheet.parse_sprite(filename))

for i in range(3):
    filename = f'attack_{i}'
    player.all_frames.append(jimmy_sheet.parse_sprite(filename))

#*---------------------------------------------------------------STAGES & SHOP SYSTEM------------------------------------------------------------------------*
current_stage = 1
stage_length = 8
min_world_chunks = 0
max_world_chunks = 0
loaded_chunks = {}
spawned_chunks = set()
stage_spawned_zombies = 0
stage_dead_zombies = 0
stage_max_zombies = 20
shop_active = False
shop_timer = 0.0
shop_accessed = False
orbs = []
shop_message = ""
shop_msg_timer = 0

spritesheet_pool = ['grass_spritesheet.png','cartoon_spritesheet.png']

def load_stage(stage_number, saved_seed=None, saved_spritesheet=None, reset_player=True):
    global current_stage, min_world_chunks, max_world_chunks, loaded_chunks, world, player_rect, current_spritesheet, spritesheet_pool, current_map_seed, spawned_chunks, stage_spawned_zombies, stage_dead_zombies, shop_active, shop_accessed, shop_timer, orbs, shop_message

    current_stage = stage_number
    loaded_chunks.clear()
    spawned_chunks.clear()
    zombies.clear()
    orbs.clear()
    stage_spawned_zombies = 0
    stage_dead_zombies = 0
    shop_active = False
    shop_timer = 0.0
    shop_accessed = False
    shop_message = ""

    stage_min_chunk_x = ((stage_number-1)*stage_length) - 1
    stage_max_chunk_x = stage_min_chunk_x + stage_length

    min_world_chunks = stage_min_chunk_x*world.chunk_pixel_w
    max_world_chunks = (stage_max_chunk_x+1)*world.chunk_pixel_w    

    if saved_seed is not None and saved_spritesheet is not None:
        new_seed = saved_seed
        current_spritesheet = Spritesheet(saved_spritesheet)
    elif stage_number == 1:
        map_index = random.randrange(len(spritesheet_pool))
        new_seed = random.randint(1,10000)
        current_spritesheet = Spritesheet(spritesheet_pool[map_index])
        spritesheet_pool.pop(map_index)
    elif stage_number == 2:
        map_index = random.randrange(len(spritesheet_pool))
        new_seed = random.randint(1,10000)
        current_spritesheet = Spritesheet(spritesheet_pool[map_index])
        spritesheet_pool.pop(map_index)
    else:
        new_seed = 69420
        current_spritesheet = Spritesheet('plague_spritesheet.png')

    current_map_seed = new_seed

    world.noise1d = PerlinNoise(octaves=2, seed = int(new_seed))
    world.noise2d = PerlinNoise(octaves=3, seed = int(new_seed))

    if reset_player:
        player.rect.x = (stage_min_chunk_x + 1)*world.chunk_pixel_w + 64
        player.rect.y = 100

"""------------------------------------------------------- In-Game Pause Menu ---------------------------------------------------------------"""

paused = False
pause_state = "PAUSE"
pause_options_state = "MAIN"
pause_dragging_slider = None
pause_dropdown_open = False
pause_rebinding_control = None
skills_opened_with_hotkey = False

DEBUG_SOUL_COINS = True

brightness, saved_world = load_game(save_slot, player, player_rect, brightness)
brightness_surface = create_brightness_surface(brightness)

skill_tree = SkillTreeState(player)
apply_skill_effects(player, skill_tree, heal_on_gain=False)
skill_ui = SkillTreeUI(skill_tree, base_res_x, base_res_y)

def pause_button_rects():
    return [pygame.Rect(220, 100 + index * 42, 200, 38) for index in range(5)]


def close_skill_tree():
    global pause_state, paused
    pause_state = "PAUSE"
    if skills_opened_with_hotkey:
        paused = False

saved_stage = saved_world.get("current_stage")
saved_seed = saved_world.get("map_seed")
saved_spritesheet = saved_world.get("spritesheet")
saved_zombie_count = saved_world.get("zombie_count")
if isinstance(saved_zombie_count, int) and saved_zombie_count >= 0:
    zombie_count = saved_zombie_count


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
    if pygame.mixer.get_init():
        pygame.mixer.music.set_volume((master_volume / 100) * (music_volume / 100))


apply_audio_settings()


def save_current_game():
    spritesheet_name = None
    if current_spritesheet is not None:
        spritesheet_name = current_spritesheet.spritesheet

    save_game(
        save_slot,
        player,
        player_rect,
        brightness,
        current_stage,
        current_map_seed,
        spritesheet_name,
        zombie_count
    )


if isinstance(saved_stage, int) and saved_stage >= 1 and saved_seed is not None and saved_spritesheet:
    current_stage = saved_stage
    load_stage(current_stage, saved_seed, saved_spritesheet, reset_player=False)
else:
    load_stage(current_stage)

while True: 

    dt = clock.get_time() / 1000.0
    player.jump = False

    # *--INPUT DETECTION--*
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            update_settings_file()
            save_current_game()
            pygame.quit()
            sys.exit()

        # Clicking an augment card selects it and immediately closes the shop.
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and shop_active:
            mouse_x = event.pos[0] * base_res_x / screen_state_w
            mouse_y = event.pos[1] * base_res_y / screen_state_h

            card_w, card_h = 120, 180
            start_x = (base_res_x - (3 * card_w + 2 * 30)) // 2
            card_y = 85

            for i in range(3):
                card_x = start_x + i * (card_w + 30)
                card_rect = pygame.Rect(card_x, card_y, card_w, card_h)
                if card_rect.collidepoint(mouse_x, mouse_y):
                    shop_active = False
                    shop_timer = 0.0
                    break

        if event.type == pygame.KEYDOWN and pause_rebinding_control is not None and paused and pause_state == "OPTIONS" and pause_options_state == "CONTROLS":
            controls[pause_rebinding_control] = pygame.key.name(event.key).title()
            control_keys[pause_rebinding_control] = event.key
            pause_rebinding_control = None
            update_settings_file()
            continue

        # ESC opens/closes pause menu or shop
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if shop_active:
                shop_active = False
            elif paused and pause_state == "SKILLS":
                close_skill_tree()
            elif pause_state == "OPTIONS":
                if pause_options_state != "MAIN":
                    pause_options_state = "MAIN"
                else:
                    pause_state = "PAUSE"
            else:
                paused = not paused
            continue

        # Interacting with Shop Orbs or toggling shop UI via 'E' key
        if event.type == pygame.KEYDOWN and event.key == pygame.K_e and not paused:
            if shop_active:
                shop_active = False
            else:
                player_vec = pygame.math.Vector2(player.rect.center)
                for orb in orbs[:]:
                    if not orb.consumed:
                        orb_vec = pygame.math.Vector2(orb.rect.center)
                        if player_vec.distance_to(orb_vec) <= 45:
                            # Roll RNG chance (or guaranteed if all zombies are killed)
                            shop_active = True
                            shop_timer = 7.0
                            shop_accessed = True
                            shop_message = "Shop Unlocked!"
                                
                            
                            shop_msg_timer = 120
                            orb.consumed = True
                            orbs.remove(orb)
                            break

        if event.type == pygame.KEYDOWN and event.key == pygame.K_F5:
            update_settings_file()
            save_current_game()

        # K opens skill tree
        if event.type == pygame.KEYDOWN and event.key == pygame.K_k and not paused and not shop_active:
            paused = True
            pause_state = "SKILLS"
            skills_opened_with_hotkey = True
            player.moving_left = player.moving_right = False
            player.aim_left = player.aim_right = player.aim_up = player.aim_down = False
            player.attacking = False
            skill_ui.open()
            continue

        if DEBUG_SOUL_COINS and event.type == pygame.KEYDOWN and event.key == pygame.K_F6:
            player.S_COIN = (player.S_COIN or 0) + 0

        # Pause menu mouse controls
        if paused:
            mouse_x = event.pos[0] * base_res_x / screen_state_w if hasattr(event, "pos") else 0
            mouse_y = event.pos[1] * base_res_y / screen_state_h if hasattr(event, "pos") else 0

            if pause_state == "SKILLS":
                skill_result = skill_ui.handle_event(event, (mouse_x, mouse_y))
                if skill_result == "purchased":
                    apply_skill_effects(player, skill_tree, heal_on_gain=True)
                    update_settings_file()
                    save_current_game()
                elif skill_result == "close":
                    close_skill_tree()
                continue

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if pause_state == "PAUSE":
                    pause_buttons = pause_button_rects()

                    if pause_buttons[0].collidepoint(mouse_x, mouse_y):
                        paused = False
                    elif pause_buttons[1].collidepoint(mouse_x, mouse_y):
                        pause_state = "SKILLS"
                        skills_opened_with_hotkey = False
                        skill_ui.open()
                    elif pause_buttons[2].collidepoint(mouse_x, mouse_y):
                        pause_state = "OPTIONS"
                        pause_options_state = "MAIN"
                    elif pause_buttons[3].collidepoint(mouse_x, mouse_y):
                        update_settings_file()
                        save_current_game()
                    elif pause_buttons[4].collidepoint(mouse_x, mouse_y):
                        update_settings_file()
                        save_current_game()
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
                save_current_game()

            continue

        if not shop_active:
            if event.type == pygame.MOUSEBUTTONDOWN:
                player.attacking = True
            if event.type == pygame.MOUSEBUTTONUP:
                player.attacking = False

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

        if event.type == pygame.KEYDOWN and not shop_active:
            if event.key == control_keys["up"]:
                player.aim_up = True
            if event.key == control_keys["left"]:
                player.moving_left = True
                player.aim_left = True
            if event.key == control_keys["down"]:
                player.aim_down = True
            if event.key == control_keys["right"]:
                player.moving_right = True
                player.aim_right = True
            if event.key == control_keys["jump"]:
                player.press_space = True

        if event.type == pygame.KEYUP and not shop_active:
            if event.key == control_keys["left"] and event.key == control_keys["right"] and event.key == control_keys["jump"]:
                player.animation_mode = 0  
            if event.key == control_keys["up"]:
                player.aim_up = False
            if event.key == control_keys["left"]:
                player.moving_left = False
                player.aim_left = False
            if event.key == control_keys["down"]:
                player.aim_down = False
            if event.key == control_keys["right"]:
                player.moving_right = False
                player.aim_right = False

    # Shop timer
    if shop_active:
        shop_timer -= dt

        if shop_timer <= 0:
            shop_timer = 0
            shop_active = False

    if paused:
        display_canvas = canvas.copy()


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
            display_canvas.blit(pause_title, pause_title.get_rect(center=(base_res_x / 2, 50)))

            pause_buttons = ["Resume", "Skill Tree", "Options", "Save", "Quit"]
            for index, option in enumerate(pause_buttons):
                button_rect = pause_button_rects()[index]
                selected_color = (235, 65, 40) if button_rect.collidepoint(mouse_x, mouse_y) else (240, 240, 240)
                option_text = font_pause.render(option, False, selected_color)
                display_canvas.blit(option_text, option_text.get_rect(center=button_rect.center))

        elif pause_state == "SKILLS":
            skill_ui.draw(display_canvas, (mouse_x, mouse_y))

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
    position_chunk_x , position_chunk_y = world.world_to_chunk(player.rect.centerx, player.rect.centery)
    needed_chunks = set()

    for chunk_y in range(position_chunk_y - render_distance, position_chunk_y + render_distance + 1):
        for chunk_x in range (position_chunk_x - render_distance, position_chunk_x + render_distance + 1):
            chunk_key = (chunk_x,chunk_y)
            needed_chunks.add(chunk_key)

            if chunk_key not in loaded_chunks:
                raw_data = world.generate_chunk_data(chunk_x,chunk_y)
                loaded_chunks[chunk_key] = TileMap(raw_data,current_spritesheet, tile_size)

    for chunk_key in list(loaded_chunks.keys()):
        if chunk_key not in needed_chunks:
            del loaded_chunks[chunk_key]

    tile_rect = []
    for (chunk_x,chunk_y), tile_map in loaded_chunks.items():
        chunk_world_x = chunk_x * chunk_pixel_w
        chunk_world_y = chunk_y * chunk_pixel_h
        tile_rect.extend(tile_map.get_rects(chunk_world_x,chunk_world_y))

    # DESPAWNING ZOMBIES
    despawn_distance = 4 * chunk_pixel_w
    for zombie in zombies[:] :
        if abs(zombie.rect.centerx - player.rect.centerx) > despawn_distance:
            zombies.remove(zombie)

    if player.moving_right:
        target_chunk_x = position_chunk_x + 1
    elif player.moving_left:
        target_chunk_x = position_chunk_x - 1
    else:
        target_chunk_x = position_chunk_x - 1

    target_chunk_position = (target_chunk_x, position_chunk_y)

    if target_chunk_position in loaded_chunks and target_chunk_position not in spawned_chunks:
        if stage_spawned_zombies < stage_max_zombies:
            spawned_chunks.add(target_chunk_position)

            chunk_min_x = target_chunk_x * chunk_pixel_w
            chunk_max_x = chunk_min_x + chunk_pixel_w - 32

            # SPAWNING ZOMBIES
            for _ in range(3):
                if stage_spawned_zombies >= stage_max_zombies:
                    break

                spawn_x = random.randint(chunk_min_x, chunk_max_x)
                spawn_y = 100

                new_zombie = Zombie(
                    pygame.Rect(spawn_x, spawn_y, 32 ,32),
                    [0,0], 0 , 0 , 0, False, (0,0), False, 
                    'Still', False, random.randint(1,3), 0,
                    False, False, False, 0, 45, int(current_stage*5 + 15), 
                    int(current_stage*2 + 5)
                )
                zombies.append(new_zombie)
                stage_spawned_zombies += 1

    zombie_count = len(zombies)

    # *--PLAYER HORIZONTAL MOVEMENT + COLLISIONS--*
    if not shop_active:
        player.movement = [0,0]  

        if player.moving_right == True:
            player.movement[0]= player.move_speed
            player.rect.x += player.movement[0]

        if player.moving_left == True:
            player.movement[0]= -player.move_speed
            player.rect.x += player.movement[0]

        for tile in tile_rect:    
            if player.rect.colliderect(tile):
                if player.movement[0] > 0:
                    player.rect.right = tile.left
                if player.movement[0] < 0:
                    player.rect.left = tile.right

        if player.rect.left < min_world_chunks:
            player.rect.left = min_world_chunks

        if player.rect.right > max_world_chunks:
            player.rect.right = max_world_chunks

        if player.rect.right >= max_world_chunks:
            load_stage(current_stage+1)

        # *-- PLAYER VERTICAL MOVEMENT + VERTICAL COLLISIONS --*
        player.movement[1] = player.y_momentum
        player.y_momentum += 0.2
        if player.y_momentum > 10:
            player.y_momentum = 10

        if not (0 <= player.y_momentum <= 1):
            player.on_ground = False

        player.rect.y += player.movement[1]

        for tile in tile_rect:
            if player.rect.colliderect(tile):
                if player.movement[1] > 0:
                    player.rect.bottom = tile.top
                    player.y_momentum = 0
                    player.on_ground = True
                if player.movement[1] < 0:
                    player.rect.top = tile.bottom
                    player.y_momentum = 0

        if player.press_space == True:
            if player.on_ground is True:
                player.jump = True
                player.air_jump_count = player.max_air_jumps
            else:
                if player.air_jump_count > 0:
                    player.jump = True
                    player.air_jump_count -= 1

        player.press_space = False

        if player.jump == True:
            player.y_momentum = -player.jump_height

    # *---------------------------------------ENTITIES & ZOMBIE DEATH---------------------------------------------------------*

    # PLAYER ATTACKING ZOMBIES
    player_damage = 0
    player.check_cooldown()

    for zombie in zombies[:]:
        zombie.damaged, applied_damage = player.attack(zombie.damaged, zombie.rect, player_damage)
        zombie.receive_damage(applied_damage)
        zombie.calculate_knockback(player.mom_force, player.x_flip, player.rect)
        zombie.check_staggered()
        
        if zombie.HP <= 0:
            stage_dead_zombies += 1
            zombies.remove(zombie)

            print(f"Zombie killed: {stage_dead_zombies}")

            if 7 <= stage_dead_zombies < 20:
                if random.random() < 0.1:
                    orbs.append(Orb(
                        pygame.Rect(zombie.rect.x, zombie.rect.y, 16, 16),
                        guaranteed=True,
                        chance=1.0
                    ))

            elif stage_dead_zombies == 20:
                orbs.append(Orb(
                    pygame.Rect(zombie.rect.x, zombie.rect.y, 16, 16),
                    guaranteed=True,
                    chance=1.0
                ))

    # ZOMBIES ATTACKING PLAYER
    for zombie in zombies:
        zombie.touch_player(player.rect)
        if not zombie.staggered:
            if zombie.attack_player(player.HP):
                player.damaged = True
        player.receive_damage(zombie.ATK)
        player.dead_check()

    choice_count += 1
    if choice_count >= 120:
        choice_count = 0
        change_action = True
    else:
        change_action = False

    if change_action:
        for zombie in zombies:
            action_pool = ['Left', 'Right', 'Still']
            action_weightage = [15,15,70]
            zombie.idle_move = random.choices(action_pool, weights=action_weightage, k=1)[0]

    # ZOMBIE HORIZONTAL MOVEMENT
    for zombie in zombies:
        try:
            zombie.aggro_player(player_render_pos) 
        except NameError:
            pass

    for zombie in zombies: 
        if zombie.render_pos[0] < position_chunk_x or zombie.render_pos[0] > position_chunk_x:
            zombie.idle_move = 'Still'

        zombie.movement = [0,0]

        if abs(zombie.x_push_momentum) > 0:
            zombie.x_push_momentum *= 0.85
            if abs(zombie.x_push_momentum) < 0.1:
                zombie.x_push_momentum = 0 
            else:
                zombie.movement[0] = zombie.x_push_momentum
                zombie.rect.x += zombie.movement[0]
        else:
            if not zombie.staggered:
                if zombie.chase_player:
                    try:
                        if zombie.render_pos > player_render_pos:
                            zombie.movement[0] = -zombie.chase_speed
                            zombie.rect.x += zombie.movement[0]
                        if zombie.render_pos < player_render_pos:
                            zombie.movement[0] = zombie.chase_speed
                            zombie.rect.x += zombie.movement[0]
                    except NameError:
                        pass
                else:
                    speed_pool = [1, 2, 3]
                    speed_weightage = [70,25,5]
                    random_zomb_speed = random.choices(speed_pool, weights=speed_weightage, k=1)[0]    
                    
                    if zombie.idle_move == 'Right':
                        zombie.movement[0] = random_zomb_speed
                        zombie.rect.x += zombie.movement[0]
                    if zombie.idle_move == 'Left':
                        zombie.movement[0] = -random_zomb_speed
                        zombie.rect.x += zombie.movement[0]
            else:
                zombie.movement = [0,0]

    # ZOMBIE COLLISIONS
    for tile in tile_rect:    
        for zombie in zombies:
            if zombie.rect.colliderect(tile):
                if zombie.movement[0] > 0:
                    zombie.rect.right = tile.left
                if zombie.movement[0] < 0:
                    zombie.rect.left = tile.right

    for zombie in zombies:
        if abs(zombie.y_push_momentum) > 0:
            zombie.y_push_momentum *= 0.85
            if abs(zombie.y_push_momentum) < 0.1:
                zombie.y_push_momentum = 0 
            else:
                zombie.movement[1] = zombie.y_push_momentum
                zombie.rect.y += zombie.movement[1]

        zombie.movement[1] = zombie.y_momentum
        zombie.y_momentum += 0.2
        if zombie.y_momentum > 4.5:
            zombie.y_momentum = 4.5

        if not (0 <= zombie.y_momentum <= 1):
            zombie.on_ground = False

        zombie.rect.y += zombie.movement[1]

        for tile in tile_rect:
            if zombie.rect.colliderect(tile):
                if zombie.movement[1] > 0:
                    zombie.rect.bottom = tile.top
                    zombie.y_momentum = 0
                    zombie.on_ground = True
                if zombie.movement[1] < 0:
                    zombie.rect.top = tile.bottom
                    zombie.y_momentum = 0

    # ANIMATIONS
    if player.attacking:
        player.animation_mode = 4
    elif not player.on_ground and player.y_momentum > 0:
        player.animation_mode = 3
    elif not player.on_ground and player.y_momentum <= 0:
        player.animation_mode = 2
    elif player.moving_right or player.moving_left:
        player.animation_mode = 1
    else:
        player.animation_mode = 0

    # VOID CHECK
    if player.rect.y > 2000:
        player.rect.x, player.rect.y = 250,100
        player.y_momentum = 0

    # CAMERA
    camera_x = player.rect.centerx - (base_res_x // 2) 
    camera_y = player.rect.centery - (base_res_y // 2)

    max_camera_x = max_world_chunks - base_res_x
    camera_x = max(min_world_chunks, min(camera_x, max_camera_x))

    canvas.fill((159, 215, 255))

    if abs(player.movement[0]) > 0:
        if player.movement[0] > 0:
            if x_camera_delay < 0:
                x_camera_delay += 0.8 
            else:
                x_camera_delay += 0.4
                if x_camera_delay >= 20:
                    x_camera_delay = 20
        if player.movement[0] < 0:
            if x_camera_delay > 0:
                x_camera_delay -= 0.8
            else:
                x_camera_delay -= 0.4
                if x_camera_delay <= -20:
                    x_camera_delay = -20
    else:
        if x_camera_delay > 0:
            x_camera_delay -= 1.0
            if x_camera_delay <= 0:
                x_camera_delay = 0
        if x_camera_delay < 0:
            x_camera_delay += 1.0
            if x_camera_delay >= 0:
                x_camera_delay = 0

    if not player.on_ground and abs(player.movement[1]) > 0:
        if player.movement[1] > 0:
            if y_camera_delay < 0:
                y_camera_delay += 0.8 
            else:
                y_camera_delay += 0.4
                if y_camera_delay >= 20:
                    y_camera_delay = 20
        if player.movement[1] < 0:
            if y_camera_delay > 0:
                y_camera_delay -= 0.8
            else:
                y_camera_delay -= 0.4
                if y_camera_delay <= -20:
                    y_camera_delay = -20
    else:
        if y_camera_delay > 0:
            y_camera_delay -= 1.0
            if y_camera_delay <= 0:
                y_camera_delay = 0
        if y_camera_delay < 0:
            y_camera_delay += 1.0
            if y_camera_delay >= 0:
                y_camera_delay = 0

    for (chunk_x,chunk_y), tile_map in loaded_chunks.items():
        chunk_world_x = chunk_x * chunk_pixel_w
        chunk_world_y = chunk_y * chunk_pixel_h
        tile_map.draw_map(canvas, (camera_x + x_camera_delay), (camera_y + y_camera_delay) ,offset_x=chunk_world_x,offset_y=chunk_world_y)

    player_render_pos = ((player.rect.x - camera_x) - x_camera_delay, (player.rect.y - camera_y) - y_camera_delay)

    for zombie in zombies:
        zombie.render_pos = ((zombie.rect.x - camera_x) - x_camera_delay, (zombie.rect.y - camera_y) - y_camera_delay)
        if zombie.render_pos[0] < position_chunk_x:
            zombie.y_momentum = 0

    if player.moving_left:
        player.x_flip = True
    elif player.moving_right:
        player.x_flip = False

    for zombie in zombies:
        if zombie.movement[0] > 0:
            zombie.x_flip = False
        elif zombie.movement[0] < 0:
            zombie.x_flip = True

    player.current_frames = player.update_action()
    player.update_player_frame()
    player_sprite = player.current_frames[player.frame_index]
    canvas.blit(pygame.transform.flip(player_sprite, player.x_flip, False), player_render_pos) 

    for zombie in zombies:
        canvas.blit(pygame.transform.flip(zombie_sprite, zombie.x_flip, False), (zombie.render_pos))

    # *-- RENDER SHOP ORBS --*
    player_vec = pygame.math.Vector2(player.rect.center)
    for orb in orbs:
        if not orb.consumed:
            orb.draw(canvas, camera_x, camera_y, x_camera_delay, y_camera_delay)
            orb_vec = pygame.math.Vector2(orb.rect.center)
            if player_vec.distance_to(orb_vec) <= 45:
                render_x = orb.rect.x - camera_x - x_camera_delay
                render_y = orb.rect.y - camera_y - y_camera_delay
                prompt = font_pause_small.render("Press 'E'", True, (255, 255, 255))
                canvas.blit(prompt, (render_x - 12, render_y - 20))

    # Display shop result message banner
    if shop_msg_timer > 0:
        shop_msg_timer -= 1
        msg_color = (100, 255, 100) if "Unlocked" in shop_message else (255, 90, 90)
        msg_surf = font_pause_small.render(shop_message, True, msg_color)
        canvas.blit(msg_surf, msg_surf.get_rect(center=(base_res_x / 2, 30)))

    # *-- RENDER SHOP OVERLAY UI (LEAGUE OF LEGENDS AUGMENTS STYLE) --*
    if shop_active:
        shop_overlay = pygame.Surface((base_res_x, base_res_y), pygame.SRCALPHA)
        shop_overlay.fill((0, 0, 0, 205))
        canvas.blit(shop_overlay, (0, 0))

        shop_title = font_pause_title.render("AUGMENT SHOP", True, (240, 240, 240))
        canvas.blit(shop_title, shop_title.get_rect(center=(base_res_x / 2, 45)))

        card_w, card_h = 120, 180
        start_x = (base_res_x - (3 * card_w + 2 * 30)) // 2
        card_y = 85

        for i in range(3):
            card_x = start_x + i * (card_w + 30)
            card_rect = pygame.Rect(card_x, card_y, card_w, card_h)
            
            # Static black augment card background
            pygame.draw.rect(canvas, (0, 0, 0), card_rect)
            # Card border
            pygame.draw.rect(canvas, (70, 70, 90), card_rect, 3)

            card_num = font_pause_small.render(f"Card {i+1}", True, (120, 120, 120))
            canvas.blit(card_num, card_num.get_rect(center=card_rect.center))

        timer_text = font_pause_small.render(f"TIME: {max(0, shop_timer):.1f}", True, (240, 240, 240))
        canvas.blit(timer_text, timer_text.get_rect(center=(base_res_x / 2, 310)))

    # Apply brightness & final render
    display_canvas = canvas.copy()
    if brightness < 50:
        display_canvas.blit(brightness_surface, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
    elif brightness > 50:
        display_canvas.blit(brightness_surface, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    scaled_resolution = pygame.transform.scale(display_canvas, (screen_state_w, screen_state_h))
    screen.blit(scaled_resolution,(0,0))
    pygame.display.update()
    clock.tick(60)