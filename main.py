import random
import subprocess
import sys

import pygame
from perlin_noise import PerlinNoise
from pygame.locals import *

import hud
from entity import Orb, Player, Zombie, zombies
from save_system import load_game, save_game
from settings_system import load_settings, save_settings
from skill_tree import SkillTreeState, SkillTreeUI, apply_skill_effects
from spritesheet import Spritesheet
from tilemap import *
from world import *

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

# Text Wrapper Helper
def draw_text_wrapped(surface, text, color, rect, font, line_spacing=2):
    words = text.split(' ')
    lines = []
    current_line = []
    for word in words:
        test_line = ' '.join(current_line + [word])
        if font.size(test_line)[0] <= rect.width:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    lines.append(' '.join(current_line))
    
    y_offset = rect.y
    for line in lines:
        text_surf = font.render(line, True, color)
        surface.blit(text_surf, (rect.x, y_offset))
        y_offset += font.get_linesize() + line_spacing

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
    "jump": pygame.key.key_code(controls.get("jump", "Space").lower()),
    "dash": pygame.key.key_code(controls.get("dash", "Left Ctrl").lower()),
    "interact": pygame.key.key_code(controls.get("interact", "E").lower()),
    "skill_tree": pygame.key.key_code(controls.get("skill_tree", "K").lower())
}
attack_mouse_button_names = {
    "Mouse Left": 1,
    "Mouse Middle": 2,
    "Mouse Right": 3,
}
attack_mouse_button = attack_mouse_button_names.get(controls.get("attack", "Mouse Left"), 1)

#camera movement
camera_x=0 
camera_y=0 
x_camera_delay = 0
y_camera_delay = 0
camera_speed=5  


pygame.display.set_caption("Return To Sender") 
canvas = pygame.Surface((base_res_x, base_res_y))
screen = pygame.display.set_mode((screen_state_w, screen_state_h), status)

brightness_surface = create_brightness_surface(brightness)


clock = pygame.time.Clock() 

# Fonts
font_pause_title = pygame.font.Font("fonts/Press_Start_2P/PressStart2P.ttf", 24)
font_pause = pygame.font.Font("fonts/VT323/VT323.ttf", 34)
font_pause_small = pygame.font.Font("fonts/VT323/VT323.ttf", 26)
font_perk_title = pygame.font.Font("fonts/VT323/VT323.ttf", 18)
font_perk_desc = pygame.font.Font("fonts/VT323/VT323.ttf", 14)  
hud_font_main = pygame.font.Font("fonts/VT323/VT323.ttf", 24) 
hud_font_small = pygame.font.Font("fonts/VT323/VT323.ttf", 16)

dash_icon = pygame.image.load("dash_icon.png").convert_alpha()


# *------------------------------------------------------------------- PERKS -----------------------------------------------------------------------------------------*
PERKS = [
    {"name": "Ignition Edge", "desc": "Melee hits have a 30% chance to set zombies on fire, dealing 15 burn damage over 3 seconds.", "rarity": "Budget", "weight": 26, "cost": 15},
    {"name": "Conductive Blade", "desc": "Every 3rd melee swing releases a shockwave that arcs lightning to 2 nearby zombies for 50% damage.", "rarity": "Budget", "weight": 26, "cost": 15},
    {"name": "Heavy Cleave", "desc": "Increases your melee swing arc size by 35% and increases knockback force by 50%.", "rarity": "Mid", "weight": 8, "cost": 30},
    {"name": "Phantom Step", "desc": "Dodging through a zombie renders you briefly invulnerable and grants +25% move speed for 2.5s.", "rarity": "Mid", "weight": 8, "cost": 30},
    {"name": "Executioner", "desc": "+35% bonus damage against zombies that are burning, shocked, or below 30% HP.", "rarity": "Mid", "weight": 8, "cost": 30},
    {"name": "Blood Siphon", "desc": "Melee kills restore 4% Max HP. Parrying or blocking an attack heals 6 HP.", "rarity": "High", "weight": 1, "cost": 60},
    {"name": "Ironclad Guard", "desc": "Reduces incoming damage from behind by 40% and grants immunity.", "rarity": "High", "weight": 1, "cost": 60},
    {"name": "Retaliatory Pulse", "desc": "Taking damage releases a kinetic shockwave that knocks back all surrounding zombies & stuns them.", "rarity": "High", "weight": 1, "cost": 60},
    {"name": "Final Arsenal", "desc": "+15% raw melee damage. Converts into +35% Ranged Dmg & +50% Reload Speed when Gun is unlocked.", "rarity": "High", "weight": 1, "cost": 60}
]





# *------------------------------------------------------------------- MAP STUFF -----------------------------------------------------------------------------------------*
current_spritesheet = None
current_map_seed = None
zombie_count = 1

tile_size = 32
chunk_tiles_x = 16
chunk_tiles_y = 16
obstacles = []

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

screen_shake_x=0
screen_shake_y=0

# *-----------------------------------------------------------PLAYER STUFF---------------------------------------------------------------------*

player = Player(
    Name=None,
    rect = pygame.Rect(100, 200, 32, 32),
    attack_rect = None,
    critical_rect = None,
    shock_rect = None,
    retaliate_rect = None,
    movement=[0,0],
    moving_up = False,
    moving_down = False,
    moving_right = False,
    moving_left = False,
    dash = False,
    dashing = False,
    dash_buffer = 0,
    max_dash_buffer = 120, #120
    max_dash_charges = 2, #2
    dash_charges = 2,  #2
    dash_dis = 15,
    dash_counter = 0,
    press_space = False,
    hor_aim_list = [],
    vert_aim_list = [],
    holding_up = False,
    holding_down = False,
    aim_up = False,
    aim_down = False,
    aim_right = False,
    aim_left = False,
    y_momentum = 0,
    x_momentum = 0,
    max_air_jumps = 2, #50
    jump = False,
    jump_height = 4.5,
    on_ground = None,
    x_flip = False,
    all_frames = [],
    current_frames = [],
    frame_index = 0,
    animation_mode = 0,
    animation_count = 0,    
    max_HP = 100,
    i_counter = 0,
    invulnerable= False,
    damaged=False,
    base_ATK=5, 
    attacking = False,
    holding_attack = False,
    hit_landed = False,
    attack_count = 0,
    combo_stage = 1,
    combo_buffer= 0,
    zombies_hit = [],
    active_perks = [],
    CRIT_DMG=None, 
    CRIT_CHANCE=None, 
    LEVEL=None, 
    EXP=None, 
    DOLLARS=None, 
    S_COIN=None,
    ignition_edge=False,
    conductive_blade=False,
    heavy_cleave=False,
    phantom_step=False,
    executioner_stance=False,
    blood_siphon=False,
    ironclad_guard=False,
    retaliatory_pulse=False,
    final_arsenal=False,
    dash_speed_count = 150,
    increase_move_speed = False,
    retaliate = False
)

player_rect = player.rect
player.hor_aim_list.append('right')
player.hor_aim_list.append('right')
player.vert_aim_list.append('up')
player.vert_aim_list.append('up')



# *--------------------------------------------ENTITIES-------------------------------------------------------*

#ZOMBIES
choice_count = 0 #stores the amount of frames it has been to make a new choice

zombie_sheet = Spritesheet('animations/spritesheets/zombie_sheet.png')

all_zombie_frames = []

for i in range(23):
    filename = f'base_zombie {i}.aseprite'
    all_zombie_frames.append(zombie_sheet.parse_sprite(filename))


# *------------------------------ANIMATION------------------------------------------------------------------------

jimmy_sheet = Spritesheet('animations/spritesheets/jimmy_sheet.png')

#LOAD PLAYER ANIMATIONS:

#idle
for i in range(12):# 0:11, mode 0
    filename = f'idle_right_{i}'
    player.all_frames.append(jimmy_sheet.parse_sprite(filename))
for i in range(12):# 12:23, mode 1
    filename = f'idle_left_{i}'
    player.all_frames.append(jimmy_sheet.parse_sprite(filename))
#standing attack
for i in range(12):# 24:35, mode 2
    filename = f'attack_right_{i}'
    player.all_frames.append(jimmy_sheet.parse_sprite(filename))
for i in range(12):# 36:47, mode 3
    filename = f'attack_left_{i}'
    player.all_frames.append(jimmy_sheet.parse_sprite(filename))
#jumping/falling
for i in range(4):# 48:51, mode 4
    filename = f'jump_right_{i}'
    player.all_frames.append(jimmy_sheet.parse_sprite(filename))
for i in range(4):# 52:55, mode 5
    filename = f'jump_left_{i}'
    player.all_frames.append(jimmy_sheet.parse_sprite(filename))
#attacking while jumping
for i in range(12):# 56:67, mode 6
    filename = f'jump_attack_right_{i}'
    player.all_frames.append(jimmy_sheet.parse_sprite(filename))
for i in range(12):# 68:79, mode 7
    filename = f'jump_attack_left_{i}'
    player.all_frames.append(jimmy_sheet.parse_sprite(filename))
#attacking up while jumping
for i in range(4):# 80:83, mode 8
    filename = f'jump_upattack_right_{i}'
    player.all_frames.append(jimmy_sheet.parse_sprite(filename))
for i in range(4):# 84:87, mode 9
    filename = f'jump_upattack_left_{i}'
    player.all_frames.append(jimmy_sheet.parse_sprite(filename))
#attacking up while standing
for i in range(4):# 88:91, mode 10
    filename = f'upattack_right_{i}'
    player.all_frames.append(jimmy_sheet.parse_sprite(filename))
for i in range(4):# 92:95, mode 11
    filename = f'upattack_left_{i}'
    player.all_frames.append(jimmy_sheet.parse_sprite(filename))
#attacking down while jumping
for i in range(4):# 96:99, mode 12
    filename = f'jump_downattack_right_{i}'
    player.all_frames.append(jimmy_sheet.parse_sprite(filename))
for i in range(4):# 100:103, mode 13
    filename = f'jump_downattack_left_{i}'
    player.all_frames.append(jimmy_sheet.parse_sprite(filename))
#walking 
for i in range(6):# 104:109, mode 14
    filename = f'walk_right_{i}'
    player.all_frames.append(jimmy_sheet.parse_sprite(filename))
for i in range(6):# 110:115, mode 15
    filename = f'walk_left_{i}'
    player.all_frames.append(jimmy_sheet.parse_sprite(filename))
#dashing
for i in range(4):# 116:119, mode 16
    filename = f'dash_right_{i}'
    player.all_frames.append(jimmy_sheet.parse_sprite(filename))
for i in range(4):# 120:123, mode 17
    filename = f'dash_left_{i}'
    player.all_frames.append(jimmy_sheet.parse_sprite(filename))

# filename = 'damage_right'
# player.all_frames.append(jimmy_sheet.parse_sprite(filename))

# filename = 'damage_left'
# player.all_frames.append(jimmy_sheet.parse_sprite(filename))




# 0-5 idle, 6-10 walk, 11-14 jump, 15-17 fall
# -idle
# LOAD PLAYER ANIMATIONS      
# for i in range(6):
#     filename = f'idle_{i}'
#     player.all_frames.append(jimmy_sheet.parse_sprite(filename))

# # -walk
# for i in range(5):
#     filename = f'walk_{i}'
#     player.all_frames.append(jimmy_sheet.parse_sprite(filename))

# # -jump
# for i in range(4):
#     filename = f'jump_{i}'
#     player.all_frames.append(jimmy_sheet.parse_sprite(filename))

# # -fall
# for i in range(3):
#     filename = f'fall_{i}'
#     player.all_frames.append(jimmy_sheet.parse_sprite(filename))

# # -fall
# for i in range(3):
#     filename = f'attack_{i}'
#     player.all_frames.append(jimmy_sheet.parse_sprite(filename))

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
current_shop_perks = []
purchases_allowed = 1
current_purchases = 0
stage_map_random_states = {}
stage_map_configs = {}

spritesheet_pool = ['asset/grass_spritesheet.png','asset/cartoon_spritesheet.png','asset/plague_spritesheet.png','asset/exclusion_spritesheet.png']

def load_stage(stage_number, saved_seed=None, saved_spritesheet=None, reset_player=True):
    global current_stage, min_world_chunks, max_world_chunks, loaded_chunks, world, player_rect, current_spritesheet, spritesheet_pool, current_map_seed, spawned_chunks, stage_spawned_zombies, stage_dead_zombies, shop_active, shop_accessed, shop_timer, orbs, shop_message, bg, stage_map_random_states, stage_map_configs 

    current_stage = stage_number
    loaded_chunks.clear()
    spawned_chunks.clear()
    obstacles.clear()
    zombies.clear()
    orbs.clear()
    stage_spawned_zombies = 0
    stage_dead_zombies = 0
    shop_active = False
    shop_timer = 0.0
    shop_accessed = False
    shop_message = ""

    world.last_obstacle_col = -999

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
    elif stage_number == 3:
        map_index = random.randrange(len(spritesheet_pool))
        new_seed = random.randint(1,10000)
        current_spritesheet = Spritesheet(spritesheet_pool[map_index])
        spritesheet_pool.pop(map_index)
    elif stage_number == 4:
        map_index = random.randrange(len(spritesheet_pool))
        new_seed = random.randint(1,10000)
        current_spritesheet = Spritesheet(spritesheet_pool[map_index])
        spritesheet_pool.pop(map_index)
    elif stage_number == 5:
        new_seed = 69420
        current_spritesheet = Spritesheet('asset/castle_spritesheet.png')
    else:
        pygame.quit()
        sys.exit()


    current_map_seed = new_seed
    stage_map_configs[stage_number] = (new_seed, current_spritesheet.spritesheet)

    # Keep the exact random state used when this stage map starts generating.
    # On a retry, restoring it makes random-based map elements generate identically.
    if saved_seed is not None and saved_spritesheet is not None and stage_number in stage_map_random_states:
        random.setstate(stage_map_random_states[stage_number])
    else:
        stage_map_random_states[stage_number] = random.getstate()

    #*--------------------------------------------------------------PARALLAX----------------------------------------------------------------------*
    if current_spritesheet is not None:
        active_spritesheet = current_spritesheet.spritesheet
    bg = ParallaxBackground(base_res_x, base_res_y)

    if active_spritesheet == 'asset/cartoon_spritesheet.png':
        #ABANDONED CITY (CARTOON SPRITESHEET)

        bg.add_layer('asset/abandoned_city/abandoned_sky.png', scroll_factor=0.0)
        bg.add_layer('asset/abandoned_city/abandoned_building1.png', scroll_factor=0.2)
        bg.add_layer('asset/abandoned_city/abandoned_building2.png',scroll_factor=0.2)
        bg.add_layer('asset/abandoned_city/abandoned_building3.png',scroll_factor=0.2)

    elif active_spritesheet == 'asset/grass_spritesheet.png':
        #APOCALYPTIC CITY (GRASS SPRITESHEET)

        bg.add_layer('asset/apocalyptic_city/apocalyptic_sky.png', scroll_factor=0.0)
        bg.add_layer('asset/apocalyptic_city/apocalyptic_building1.png', scroll_factor=0.2)
        bg.add_layer('asset/apocalyptic_city/apocalyptic_building2.png',scroll_factor=0.2)
        bg.add_layer('asset/apocalyptic_city/apocalyptic_building3.png',scroll_factor=0.2)

    elif active_spritesheet == 'asset/plague_spritesheet.png':
        #GHOST TOWN (PLAGUE SPRITESHEET)

        bg.add_layer('asset/ghost_town/ghost_sky.png', scroll_factor=0.0)
        bg.add_layer('asset/ghost_town/ghost_town_folliage.png', scroll_factor=0.2)
        bg.add_layer('asset/ghost_town/ghost_town1.png',scroll_factor=0.267)
        bg.add_layer('asset/ghost_town/ghost_town2.png',scroll_factor=0.267)
        bg.add_layer('asset/ghost_town/ghost_town_trees.png',scroll_factor=0.367)
        
    elif active_spritesheet == 'asset/exclusion_spritesheet.png':

        bg.add_layer('asset/industrial/industrial_bg.png', scroll_factor=0.0)
        bg.add_layer('asset/industrial/industrial_far_buildings.png', scroll_factor=0.2)
        bg.add_layer('asset/industrial/industrial_building.png',scroll_factor=0.2)
        bg.add_layer('asset/industrial/industrial_foreground.png',scroll_factor=0.2)

    elif active_spritesheet == 'asset/castle_spritesheet.png':
        bg.add_layer('asset/station/station_bg.png', scroll_factor=0.0)
        bg.add_layer('asset/station/station_detail.png', scroll_factor=0.2)
        bg.add_layer('asset/station/station_train.png',scroll_factor=0.2)
        bg.add_layer('asset/station/station_underfloor.png',scroll_factor=0.2)
        bg.add_layer('asset/station/station_columns.png',scroll_factor=0.2)
        bg.add_layer('asset/station/station_infopost.png',scroll_factor=0.4)
        bg.add_layer('asset/station/station_wires.png',scroll_factor=0.2)


    print(
    "GENERATING WORLD:",
    "stage =", current_stage,
    "seed =", current_map_seed,
    "player =", (player.rect.x, player.rect.y)
    )

    #reinitialise perlin
    #Surface_Level
    world.noise1d = PerlinNoise(octaves=2, seed = int(new_seed))
    world.noise2d = PerlinNoise(octaves=3, seed = int(new_seed))

    if reset_player:
        player.rect.x = (stage_min_chunk_x + 1)*world.chunk_pixel_w + 64
        player.rect.y = 100

    return stage_min_chunk_x

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
        "controls": controls
    })



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



#note for rendering: whatever is first rendered in the loop will be behind while whatever is last rendered in the loop will be in the very front
#*--GAME LOOP--*
if isinstance(saved_stage, int) and saved_stage >= 1 and saved_seed is not None and saved_spritesheet:
    current_stage = saved_stage
    stage_min_chunk_x = load_stage(current_stage, saved_seed, saved_spritesheet, reset_player=False)
else:
    stage_min_chunk_x = load_stage(current_stage)


hit_freeze_timer = 0


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

        # Perks Card Selection Logic
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and shop_active:
            mouse_x = event.pos[0] * base_res_x / screen_state_w
            mouse_y = event.pos[1] * base_res_y / screen_state_h

            card_w, card_h = 120, 180
            shop_slots = len(current_shop_perks)
            start_x = (base_res_x - (shop_slots * card_w + (shop_slots - 1) * 30)) // 2
            card_y = 85

            for i in range(shop_slots):
                card_x = start_x + i * (card_w + 30)
                card_rect = pygame.Rect(card_x, card_y, card_w, card_h)
                
                if card_rect.collidepoint(mouse_x, mouse_y):
                    perk = current_shop_perks[i]
                    if perk is not None:
                        if (player.DOLLARS or 0) >= perk["cost"]:
                            player.DOLLARS = (player.DOLLARS or 0) - perk["cost"]
                            if not hasattr(player, 'active_perks'): 
                                player.active_perks = []
                                print(perk)
                            player.active_perks.append(perk)
                            current_shop_perks[i] = None 
                            current_purchases += 1
                            
                            if current_purchases >= purchases_allowed:
                                shop_active = False
                                shop_timer = 0.0
                    break

        if pause_rebinding_control is not None and paused and pause_state == "OPTIONS" and pause_options_state == "CONTROLS":
            if event.type == pygame.MOUSEBUTTONDOWN and pause_rebinding_control == "attack":
                if event.button in (1, 2, 3):
                    attack_mouse_button = event.button
                    controls["attack"] = {1: "Mouse Left", 2: "Mouse Middle", 3: "Mouse Right"}[event.button]
                    pause_rebinding_control = None
                    update_settings_file()
                continue
            if event.type == pygame.KEYDOWN and pause_rebinding_control != "attack":
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
        if event.type == pygame.KEYDOWN and event.key == control_keys["interact"] and not paused:
            if shop_active:
                shop_active = False
            else:
                player_vec = pygame.math.Vector2(player.rect.center)
                for orb in orbs[:]:
                    if not orb.consumed:
                        orb_vec = pygame.math.Vector2(orb.rect.center)

                        if player_vec.distance_to(orb_vec) <= 45:

                            if orb.guaranteed or random.random() < orb.chance:
                                shop_active = True
                                shop_timer = 15.0 
                                shop_accessed = True
                                shop_message = "Shop Unlocked!"
                                
                                # Setup Perk Selection parameters based on Skill Tree
                                num_slots = 3 + getattr(player, 'shop_slots', 0) 
                                purchases_allowed = 1 + getattr(player, 'purchase_limit', 0)
                                current_purchases = 0
                                current_shop_perks = []
                                
                                temp_perks = list(PERKS)
                                for _ in range(num_slots):
                                    if not temp_perks: break
                                    weights = [p['weight'] for p in temp_perks]
                                    chosen = random.choices(temp_perks, weights=weights, k=1)[0]
                                    current_shop_perks.append(chosen)
                                    temp_perks.remove(chosen)
                            else:
                                shop_message = "The Orb Exploded - No Shop Access!"

                            shop_msg_timer = 120
                            orb.consumed = True
                            orbs.remove(orb)
                            break

        if event.type == pygame.KEYDOWN and event.key == pygame.K_F5:
            update_settings_file()
            save_current_game()

        # K opens skill tree
        if event.type == pygame.KEYDOWN and event.key == control_keys["skill_tree"] and not paused and not shop_active:
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
            player.DOLLARS = (player.DOLLARS or 0) + 50 

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
                            pygame.Rect(100, 150, 440, 40)
                        ]

                        if option_cards[0].collidepoint(mouse_x, mouse_y):
                            pause_options_state = "VIDEO"
                        elif option_cards[1].collidepoint(mouse_x, mouse_y):
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

                    elif pause_options_state == "CONTROLS":
                        if pygame.Rect(0, 310, base_res_x, 40).collidepoint(mouse_x, mouse_y):
                            pause_options_state = "MAIN"
                            pause_rebinding_control = None

                        control_rows = [
                            ("up", 92),
                            ("left", 116),
                            ("down", 140),
                            ("right", 164),
                            ("jump", 188),
                            ("dash", 212),
                            ("attack", 236),
                            ("interact", 260),
                            ("skill_tree", 284)
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

            if event.type == pygame.KEYDOWN and event.key == pygame.K_F5:
                save_current_game()

            continue


        # *--KEY DETECTION--*

        # *--WINDOW CONTROLS--*

        
        if not shop_active:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == attack_mouse_button:
                player.holding_attack = True
            if event.type == pygame.MOUSEBUTTONUP and event.button == attack_mouse_button:
                player.holding_attack = False


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
        
        hor_recently_aimed = player.hor_aim_list[-1] #to prevent double input
        vert_recentely_aimed = player.vert_aim_list[-1] #to prevent double input

    

        if event.type == pygame.KEYDOWN and not shop_active:
            if event.key == control_keys["up"] and player: #pressing W (up)
                player.holding_up = True
                if 'up' not in vert_recentely_aimed:
                    player.vert_aim_list.append("up")

            if event.key == control_keys["left"]: #pressing A (left)
                player.moving_left = True
                if 'left' not in hor_recently_aimed:
                    player.hor_aim_list.append('left')

            if event.key == control_keys["down"]: #pressing S (down)
                player.holding_down = True
                if 'down' not in vert_recentely_aimed:
                    player.vert_aim_list.append("down")

               
            if event.key == control_keys["right"]: #pressing D (right)
                player.moving_right = True
                if 'right' not in hor_recently_aimed:
                    player.hor_aim_list.append('right')


            if event.key == control_keys["jump"]:
                player.press_space = True


            if event.key == control_keys["dash"]:
                player.dash = True
            

            # *--KEY IS LET GO--*  
        if event.type == pygame.KEYUP and not shop_active:


            if event.key == control_keys["up"]:#let go of W (up)
                player.holding_up = False

            if event.key == control_keys["left"]: #let go of A (left)
                player.moving_left = False
    
            if event.key == control_keys["down"]:#let go of S (down)
                player.holding_down = False
            
            if event.key == control_keys["right"]: #let go of D (right)
                player.moving_right = False

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

                option_cards = ["Video Settings", "Controls"]
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

            elif pause_options_state == "CONTROLS":
                title = font_pause_title.render("CONTROLS", False, (240, 240, 240))
                display_canvas.blit(title, title.get_rect(center=(base_res_x / 2, 65)))
                control_rows = [
                    ("Aim Up", controls.get("up", "W")),
                    ("Move Left", controls.get("left", "A")),
                    ("Aim Down", controls.get("down", "S")),
                    ("Move Right", controls.get("right", "D")),
                    ("Jump", controls.get("jump", "Space")),
                    ("Dash", controls.get("dash", "Left Ctrl")),
                    ("Attack", controls.get("attack", "Mouse Left")),
                    ("Interact / Shop", controls.get("interact", "E")),
                    ("Skill Tree", controls.get("skill_tree", "K"))
                ]
                for index, (action, key) in enumerate(control_rows):
                    row_y = 92 + index * 24
                    control_name = ["up", "left", "down", "right", "jump", "dash", "attack", "interact", "skill_tree"][index]
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
                tile_grid = world.generate_chunk_data(chunk_x,chunk_y)
                loaded_chunks[chunk_key] = TileMap(tile_grid,current_spritesheet, tile_size)

                new_obstacles, world.last_obstacle_col = world.generate_chunk_obstacles(chunk_x, chunk_y, tile_grid, world.last_obstacle_col)

                obstacles.extend(new_obstacles)

    for chunk_key in list(loaded_chunks.keys()):
        if chunk_key not in needed_chunks:
            del loaded_chunks[chunk_key]

    tile_rect = []
    for (chunk_x,chunk_y), tile_map in loaded_chunks.items():
        chunk_world_x = chunk_x * chunk_pixel_w
        chunk_world_y = chunk_y * chunk_pixel_h
        tile_rect.extend(tile_map.get_rects(chunk_world_x,chunk_world_y))

    collision_rects = tile_rect.copy()
    for obstacle in obstacles:
        if obstacle.solid:
            collision_rects.append(obstacle.rect)

    # *--------------------------SPAWNING/DESPAWNING ZOMBIES----------------------------------


    # DESPAWNING ZOMBIES
    despawn_distance = 4 * chunk_pixel_w
    for zombie in zombies[:] :
        if abs(zombie.rect.centerx - player.rect.centerx) > despawn_distance:
            # Keep the final stage zombie available so it can always be killed
            # and guarantee the stage's shop orb.
            if not getattr(zombie, "stage_final_zombie", False):
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
                    pygame.Rect(spawn_x, spawn_y, 32 ,32), [],0,0,0,None,
                    [0,0], 0 , 0 , 0, False, (0,0), False, 
                    'Still', False, random.randint(1,3),0,0, False,
                    False, False, False, 0, 45, False, 240,False, 120, int(current_stage*5 + 15), 
                    int(current_stage*2 + 5)
                )
                new_zombie.head_rect = new_zombie.generate_head_rect() #make head rect for critical hit
                new_zombie.stage_final_zombie = (stage_spawned_zombies + 1 == stage_max_zombies)
                zombies.append(new_zombie)
                stage_spawned_zombies += 1

    zombie_count = len(zombies)

    # *--------------------------------------------------------------------------- 
    # *--PLAYER AIM CODE--*
    
    #hard locks the player to face one direction:
    
    #ensures only 2 states are contained within each list as to not flood the memory
 
    if len(player.hor_aim_list) > 2:
        player.hor_aim_list.pop(0)

    if player.hor_aim_list[-1] == 'right':
        player.aim_right = True
        player.aim_left = False

    if player.hor_aim_list[-1] == 'left':
        player.aim_left = True
        player.aim_right = False


    if len(player.vert_aim_list) > 2:
        player.vert_aim_list.pop(0)

    if not player.attacking:
        # if player is not attacking, it will decide their vertical direction like normal
        player.aim_up = player.holding_up and player.vert_aim_list[-1] == 'up'
        player.aim_down = player.holding_down and player.vert_aim_list[-1] == 'down'
    else:
        # 0, 19, 39, and 59 represents the points where an animation is about to start/finished. meaning up and down only play when a full swing
        #is animated
        if player.attack_count in (0, 19, 39, 59):
            if player.holding_up and player.vert_aim_list[-1] == 'up':
                player.aim_up = True
                player.aim_down = False
            elif player.holding_down and player.vert_aim_list[-1] == 'down':
                player.aim_down = True
                player.aim_up = False
            else:
                player.aim_up = False
                player.aim_down = False



        

  
    


    
    # *---------------------------------------------------------------------------
    #                                       FREEZE FRAME
    
    if hit_freeze_timer == None:
        hit_freeze_timer = 0

    if hit_freeze_timer > 0:
        hit_freeze_timer -= 1
    else:

     

    # ---------------------------------PERKS------------------------------------------------------------------
    
        player.check_perks()

   # *---------------------------------------------------------------------------
        # *--PLAYER HORIZONTAL MOVEMENT + COLLISIONS--*

        player.init_dash()



        player.movement = [0,0]  
        if player.dashing is True:
            if player.aim_right is True:
                dash_force = player.dash_dis
                if abs(dash_force) > 0:
                    dash_force *= 0.85
                
                    if abs(dash_force) < 0.1: #if its near 0, its negligible so make it zero
                        dash_force = 0
                
                player.movement[0]=dash_force 
                player.rect.x += player.movement[0]

            if player.aim_left is True:
                dash_force = player.dash_dis
                if abs(dash_force) > 0:
                    dash_force *= 0.85
                
                    if abs(dash_force) < 0.1: #if its near 0, its negligible so make it zero
                        dash_force = 0
                
                player.movement[0]=-dash_force 
                player.rect.x += player.movement[0]
        else:

            #left and right movement   

            if player.increase_move_speed:
                x_speed_increase = 2
            else:
                x_speed_increase = 0

            if player.attacking is True: #slow down movement if the player is attacking
                if player.moving_right == True:
                    player.movement[0]= 1
                    player.rect.x += player.movement[0] + x_speed_increase

                if player.moving_left == True:
                    player.movement[0]= -1
                    player.rect.x += player.movement[0] - x_speed_increase
                    player.rect.x -= (player.hit_number % 3)*2

            else:
                if player.moving_right == True:
                    player.movement[0]= 4
                    player.rect.x += player.movement[0] + x_speed_increase

                if player.moving_left == True:
                    player.movement[0]= -4 - x_speed_increase
                    player.rect.x += player.movement[0]



        #collisions
        for tile in tile_rect:    
            if player.rect.colliderect(tile):
                if player.movement[0] > 0:
                    player.rect.right = tile.left

                if player.movement[0] < 0:
                    player.rect.left = tile.right

        for rect in collision_rects:
                    if player.rect.colliderect(rect):
                        if player.movement[0] > 0:
                            player.rect.right = rect.left
                        if player.movement[0]< 0:
                            player.rect.left = rect.right

        #clamping
        if player.rect.left < min_world_chunks:
            player.rect.left = min_world_chunks

        if player.rect.right > max_world_chunks:
            player.rect.right = max_world_chunks

        #next stage
        if player.rect.right >= max_world_chunks:
            player.DOLLARS = (player.DOLLARS or 0)
            player.S_COIN = (player.S_COIN or 0) + 8
            load_stage(current_stage+1)
            

    #---------------------------------------------------------------------

        # *-- PLAYER VERTICAL MOVEMENT + VERTICAL COLLISIONS --*
        
        #PLAYER
        #gravity
        if player.dashing is True:
            player.y_momentum = 0
            pass #ignore gravity while dashing
        else:
            player.movement[1] = player.y_momentum
            
            player.y_momentum += 0.2
            if player.y_momentum > 10:
                player.y_momentum = 10

            if player.y_momentum >= 0 and player.y_momentum <= 1: #checks if player is in the air
                pass
            else:
                player.on_ground = False

            player.rect.y += player.movement[1]

        


        for tile in tile_rect:
            if player.rect.colliderect(tile):
                if player.movement[1] > 0:
                    player.rect.bottom = tile.top
                    player.y_momentum = 0 # <-- basically tells the game that i can stop falling now
                    player.on_ground = True
            
                if player.movement[1] < 0:
                    player.rect.top = tile.bottom
                    player.y_momentum = 0 # <-- same with this
                
        for rect in collision_rects:
                if player.rect.colliderect(rect):
                    if player.movement[1] > 0:
                        player.rect.bottom = rect.top
                        player.y_momentum = 0 
                        player.on_ground = True
                
                    if player.movement[1] < 0:
                        player.rect.top = rect.bottom
                        player.y_momentum = 0 


        #                    *--JUMP--
        
        #positive y momentum is downward | negative y momentum is upward
        if player.dashing is True:
            player.y_momentum = 0
            pass #ignore while dashing
        else:
            if player.press_space == True:
                if player.on_ground is True: #player touching ground
                    player.jump = True
                    player.air_jump_count = player.max_air_jumps
                else: #player is in the air
                    if player.air_jump_count > 0: #if player has an extra jump, then jump then deduct from remaining jumps
                        player.jump = True
                        player.air_jump_count -= 1
                    else:
                        pass
            else:
                pass

            player.press_space = False #just returns it back to the original state so it doesn't infintely jump

            if player.jump == True:
                player.y_momentum = -player.jump_height

    # *---------------------------------------ENTITIES---------------------------------------------------------*

        #PLAYER ATTACKING ZOMBIES
        zomb_no = 0
        del_zomb = None
        player_damage = 0
        total_damage = 0

        player.check_cooldown()
        player.update_attack_hitbox()
        applied_damage, hit_freeze_timer = player.attack(zombies, hit_freeze_timer, current_stage) 

        for zombie in zombies:
            zombie.check_on_fire()
            zombie.check_shocked()
            zombie.check_staggered()    
            del_zomb = zombie.dead_check(zomb_no)
            if del_zomb is not None:
                zombies.pop(del_zomb)
                stage_dead_zombies += 1
                player.DOLLARS = (player.DOLLARS or 0) + 3

                print(f"Zombie killed: {stage_dead_zombies} | +$3")

                if getattr(zombie, "stage_final_zombie", False):
                            # The final zombie of the stage always drops the shop orb.
                            pass
                            print(f"Zombie killed: {stage_dead_zombies}")

                if player.blood_siphon:
                    siphoned_blood = (0.04*player.max_HP)
                    player.HP += siphoned_blood
                else:
                    pass

                if 7 <= stage_dead_zombies < 20:
                    if random.random() < 0.1:   # Orb drop chance
                        orbs.append(Orb(
                            pygame.Rect(zombie.rect.x, zombie.rect.y, 16, 16),
                            guaranteed=False,
                            chance=0.7  # RNG Shop
                        ))

                elif stage_dead_zombies == 20:
                    orbs.append(Orb(
                        pygame.Rect(zombie.rect.x, zombie.rect.y, 16, 16),
                        guaranteed=True,
                        chance=1.0
                    ))
                elif 7 <= stage_dead_zombies < stage_max_zombies:
                    if random.random() < 0.1:   # Orb drop chance
                        orbs.append(Orb(
                            pygame.Rect(zombie.rect.x, zombie.rect.y, 16, 16),
                            guaranteed=False,
                            chance=0.6   # Shop RNG
                        ))

                zomb_no += 1

            

        screen_shake_x, screen_shake_y = player.calculate_screen_shake(applied_damage, screen_shake_x, screen_shake_y)
        
            


        #ZOMBIES ATTACKING PLAYER
        for zombie in zombies:
            zombie.touch_player(player.rect)
            zombie.check_cooldown()
            if zombie.staggered == False:
                player.damaged = zombie.attack_player(player.damaged)

            hit_freeze_timer = player.receive_damage(zombie.ATK, hit_freeze_timer)

        player.retaliatory_rect_collision(zombies)

        current_stage = player.dead_check(current_stage, stage_min_chunk_x, world.chunk_pixel_w)

        if player.HP <= 0:
            print("Player died - resetting run")

            # Retry Stage 1 using the exact same map seed, spritesheet,
            # and random generation state from the original run.
            retry_map_seed, retry_map_spritesheet = stage_map_configs[1]

            player.DOLLARS = 0
            player.HP = player.max_HP
            player.active_perks = []
            player.y_momentum = 0
            player.x_momentum = 0
            player.dashing = False
            player.dash = False
            player.dash_buffer = 0
            player.dash_counter = 0
            player.damaged = False
            player.invulnerable = False
            player.attacking = False
            player.holding_attack = False
            player.hit_landed = False
            player.attack_count = 0
            player.combo_stage = 1
            player.combo_buffer = 0
            player.zombies_hit = []
            shop_active = False
            shop_timer = 0.0
            shop_accessed = False
            shop_message = ""
            shop_msg_timer = 0
            current_shop_perks = []
            current_purchases = 0
            load_stage(1, retry_map_seed, retry_map_spritesheet)

        
        
    
    # *---------------------------------------ENTITIES---------------------------------------------------------


        # 60*x frames to tell the game to change what action the zombies should be doing
        choice_count += 1
        if choice_count >= 120: #120 means every 2 seconds since 60x2=120
            choice_count = 0
            change_action = True
        else:
            change_action = False

        #IF 
        if change_action == True:
            for zombie in zombies:
                #determining left and right movement
                    action_pool = ['Left', 'Right', 'Still']
                    action_weightage = [15,15,70]
                    zombie.idle_move = random.choices(action_pool, weights=action_weightage, k=1)[0]
                    

        #ZOMBIE HORIZONTAL MOVEMENT

        for zombie in zombies:
            try:#because initially player_render_pos hasn't been defined yet
                zombie.aggro_player((player.rect.centerx, player.rect.centery)) 
            except NameError:
                pass
        

        
        for zombie in zombies: 

            zombie_chunk_x = zombie.rect.centerx // chunk_pixel_w # <-- what chunk the zombie is in 
            if abs(zombie_chunk_x - position_chunk_x) >= render_distance: #<-- if zombie is out of bounds, make them stand still
                zombie.idle_move = 'Still'
        
        
            zombie.movement = [0,0]

            if abs(zombie.x_push_momentum) > 0:#if there is any X_knockback applied to zombie then apply it

                zombie.x_push_momentum *= 0.85
                
                if abs(zombie.x_push_momentum) < 0.1: #if its near 0, its negligible so make it zero
                    zombie.x_push_momentum = 0 
                else:
                    zombie.movement[0] = zombie.x_push_momentum
                    zombie.rect.x += zombie.movement[0]
            else:

                if zombie.staggered == False: #if zombie is not staggered
                    if zombie.chase_player == True: #chase player

                        try:
                            if zombie.rect.centerx > player.rect.centerx:
                                if zombie.shocked:
                                    zombie.movement[0] = -zombie.chase_speed//2
                                    zombie.rect.x += zombie.movement[0]
                                else:
                                    zombie.movement[0] = -zombie.chase_speed
                                    zombie.rect.x += zombie.movement[0]


                            if zombie.rect.centerx < player.rect.centerx:
                                if zombie.shocked:
                                    zombie.movement[0] = zombie.chase_speed//2
                                    zombie.rect.x += zombie.movement[0]
                                else:
                                    zombie.movement[0] = zombie.chase_speed
                                    zombie.rect.x += zombie.movement[0]    


                        except NameError:
                            pass


                    else: #idle movement

                        speed_pool = [1, 2, 3]
                        speed_weightage = [70,25,5]
                        random_zomb_speed = random.choices(speed_pool, weights=speed_weightage, k=1)[0]    
                        
                        #move right
                        if zombie.idle_move == 'Right':
                            if zombie.shocked:
                                zombie.movement[0] = random_zomb_speed//2
                                zombie.rect.x += zombie.movement[0]
                            else:
                                zombie.movement[0] = random_zomb_speed
                                zombie.rect.x += zombie.movement[0]

                        #move left
                        if zombie.idle_move == 'Left':
                            if zombie.shocked:
                                zombie.movement[0] = -random_zomb_speed//2
                                zombie.rect.x += zombie.movement[0]
                            else:
                                zombie.movement[0] = -random_zomb_speed
                                zombie.rect.x += zombie.movement[0]

                        #dont move
                        if zombie.idle_move == 'Still':
                            pass
                else: #if zombie is staggered
                    zombie.movement = [0,0]
                
        #HORIZONTAL KNOCKBACK CODE



        #ZOMBIE HORIZONTAL COLLISIONS
        for tile in tile_rect:    
            for zombie in zombies:
                if zombie.rect.colliderect(tile):
                    if zombie.movement[0] > 0:
                        zombie.rect.right = tile.left

                    if zombie.movement[0] < 0:
                        zombie.rect.left = tile.right
                
        #ZOMBIE VERTICAL MOVEMENT AND GRAVITY + VERTICAL COLLISION



        for zombie in zombies:

            if abs(zombie.y_push_momentum) > 0: #if there is any Y_knockback applied to zombie then apply it

                zombie.y_push_momentum *= 0.85
                
                if abs(zombie.y_push_momentum) < 0.1: #if its near 0, its negligible so make it zero
                    zombie.y_push_momentum = 0 
                else:
                    zombie.movement[1] = zombie.y_push_momentum
                    zombie.rect.y += zombie.movement[1]


            zombie.movement[1] = zombie.y_momentum
            zombie.y_momentum += 0.2
            if zombie.y_momentum > 4.5:
                zombie.y_momentum = 4.5
            

            if zombie.y_momentum >= 0 and zombie.y_momentum <= 1: #checks if zombie is in the air
                pass
            else:
                zombie.on_ground = False

            zombie.rect.y += zombie.movement[1]



            
            for tile in tile_rect:
                if zombie.rect.colliderect(tile):
                    if zombie.movement[1] > 0:
                        zombie.rect.bottom = tile.top
                        zombie.y_momentum = 0 # <-- basically tells the game that the zombie can stop falling now
                        zombie.on_ground = True
                
                    if zombie.movement[1] < 0:
                        zombie.rect.top = tile.bottom
                        zombie.y_momentum = 0 # <-- same with this


        for zombie in zombies:
            zombie.update_head_rect()

                                    # *--ANIMATION--*
    #-----------------------------------------------------------------------------------------------------
        
        #PLAYER ANIMATIONS

        #dashing
        if player.dashing == True and player.aim_right: 
            player.animation_mode = 16

        #dashing
        elif player.dashing == True and player.aim_left: 
            player.animation_mode = 17


        #attacking up while falling
        elif player.on_ground == False and player.y_momentum > 0 and player.attacking and player.aim_up and player.aim_right:#right
            player.animation_mode = 8
        elif player.on_ground == False and player.y_momentum > 0 and player.attacking and player.aim_up and player.aim_left:#left
            player.animation_mode = 9
        
        #attacking down while falling
        elif player.on_ground == False and player.attacking and player.aim_down and player.aim_right:#right
            player.animation_mode = 12
        elif player.on_ground == False and player.attacking and player.aim_down and player.aim_left:#left
            player.animation_mode = 13

        #attacking while falling 
        elif player.on_ground == False and player.attacking and player.aim_right:#right
            player.animation_mode = 6
        elif player.on_ground == False and player.attacking and player.aim_left:#left
            player.animation_mode = 7

                
        #falling
        elif player.on_ground == False and player.y_momentum > 0 and player.aim_right: #right 
            player.animation_mode = 4
        elif player.on_ground == False and player.y_momentum > 0 and player.aim_left:#left
            player.animation_mode = 5

        #attacking up while jumping
        elif player.on_ground == False and player.y_momentum <= 0 and player.attacking and player.aim_up and player.aim_right:#right
            player.animation_mode = 8
        elif player.on_ground == False and player.y_momentum <= 0 and player.attacking and player.aim_up and player.aim_left:#left
            player.animation_mode = 9

        #attacking down while jumping
        elif player.on_ground == False and player.y_momentum <= 0 and player.attacking and player.aim_down and player.aim_right:#right
            player.animation_mode = 12
        elif player.on_ground == False and player.y_momentum <= 0 and player.attacking and player.aim_down and player.aim_left:#left
            player.animation_mode = 13
            
        #attacking while jumping 
        elif player.on_ground == False and player.attacking and player.aim_right:#right
            player.animation_mode = 6
        elif player.on_ground == False and player.attacking and player.aim_left:#left
            player.animation_mode = 7

    

        #jumping   
        elif player.on_ground == False and player.y_momentum <= 0 and player.aim_right:#right
            player.animation_mode = 4
        elif player.on_ground == False and player.y_momentum <= 0 and player.aim_left:#left
            player.animation_mode = 5

        #attacking up while standing
        elif player.attacking and player.aim_up and player.aim_right:#right
            player.animation_mode = 10
        elif player.attacking and player.aim_up and player.aim_left:#left
            player.animation_mode = 11
        

        #attacking horizontally while standing
        elif player.attacking and player.aim_right:#right
            player.animation_mode = 2
        elif player.attacking and player.aim_left:#left
            player.animation_mode = 3 

    
        #walking
        elif player.moving_right:#right
            player.animation_mode = 14
        elif player.moving_left:#left
            player.animation_mode = 15

        #idle
        elif player.aim_right:#right
            player.animation_mode = 0
        elif player.aim_left:#left
            player.animation_mode = 1

        else: 
            player.animation_mode = 0


        #ZOMBIE ANIMATIONS
        #walking
        for zombie in zombies:

            if zombie.attack_count > 0 and zombie.touched_player: 
                if zombie.x_flip == False: #attack right
                    zombie.animation_mode = 5
                elif zombie.x_flip == True: #attack left
                    zombie.animation_mode = 6

            elif zombie.chase_player == False:
                if zombie.movement[0] > 0 :# walk right
                    zombie.animation_mode = 1
                elif zombie.movement[0] < 0:#walk left
                    zombie.animation_mode = 2
            elif zombie.chase_player == True:
                if zombie.movement[0] > 0 :# chase right
                    zombie.animation_mode = 3
                elif zombie.movement[0] < 0:# chase left
                    zombie.animation_mode = 4
            else:
                zombie.animation_mode = 0




                                # *--RENDERING--*
 #----------------------------------------------------------------------------------------------------------



    # void
    if player.rect.y > 2000:
        player.rect.x, player.rect.y = 250,100
        player.y_momentum = 0


    # *--CAMERA MOVEMENT--*
    #these 2 centers the player within the base canvas

    camera_x = player.rect.centerx - (base_res_x // 2)
    camera_y = player.rect.centery - (base_res_y // 2) 

    
     #map clamping      
    max_camera_x = max_world_chunks - base_res_x - screen_shake_x - x_camera_delay
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

    
    effective_camera_x = camera_x + x_camera_delay
    effective_camera_y = camera_y + y_camera_delay

    if abs(screen_shake_x) > 0:
        screen_shake_x *= 0.85
        if abs(screen_shake_x) < 0.1:
            screen_shake_x = 0

    if abs(screen_shake_y) > 0:
        screen_shake_y *= 0.85
        if abs(screen_shake_y) < 0.5:
            screen_shake_y = 0

    bg.draw(canvas, effective_camera_x, effective_camera_y)


    for (chunk_x,chunk_y), tile_map in loaded_chunks.items():
        chunk_world_x = chunk_x * chunk_pixel_w
        chunk_world_y = chunk_y * chunk_pixel_h
        tile_map.draw_map(canvas, (camera_x + x_camera_delay + screen_shake_x), (camera_y + y_camera_delay + screen_shake_y) ,offset_x=chunk_world_x,offset_y=chunk_world_y)
    #                                        ^positive map delay                                     ^

    player_render_pos = ((player.rect.x - camera_x) - x_camera_delay, (player.rect.y - camera_y) - y_camera_delay)

     
    for obstacle in obstacles:   
        obstacle.update(tile_rect)
        
        obstacle.draw(canvas, camera_x, camera_y, x_camera_delay, y_camera_delay,screen_shake_x , screen_shake_y)
    
    # player_render_pos = ((player.rect.x- camera_x) - x_camera_delay - 48, (player.rect.y-  camera_y) - y_camera_delay -48) #centers player on screen
    # #                                                                                                   ^negative camera delay

    player_render_pos = (player.rect.centerx -64 - camera_x - x_camera_delay - screen_shake_x, player.rect.bottom - 80 - camera_y - y_camera_delay - screen_shake_y)

    #zombie render code
    for zombie in zombies:
        zombie.render_pos = ((zombie.rect.x - camera_x) - x_camera_delay - screen_shake_x, (zombie.rect.y - camera_y) - y_camera_delay - screen_shake_y) 
    #                                                                                                   ^negative camera delay
        #disables zombie gravity if out of range
        zombie_chunk_x = zombie.rect.centerx // chunk_pixel_w # <-- what chunk the zombie is in 
        if abs(zombie_chunk_x - position_chunk_x) >= render_distance: #<-- if the zombie is out of bounds, gravity is disabled
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

    
    player.current_frames = player.update_action() #determines the current type of animation playing only if the animation mode changes
    player.update_player_frame() #update frame played and returns the animation mode
    player_sprite = player.current_frames[player.frame_index] #determines the image/sprite which will be displayed on player pos
    canvas.blit(player_sprite, player_render_pos)
    if player.shock_rect is not None:
        shock_hitbox = pygame.Surface((player.shock_rect.width,player.shock_rect.height), pygame.SRCALPHA)
        shock_hitbox.fill((173, 216, 230, 128))
        canvas.blit(shock_hitbox, (player.shock_rect.x - camera_x - x_camera_delay - screen_shake_x, player.shock_rect.y - camera_y - y_camera_delay - screen_shake_y))


    if player.retaliate_rect is not None:
        retaliate_hitbox = pygame.Surface((player.retaliate_rect.width,player.retaliate_rect.height), pygame.SRCALPHA)
        retaliate_hitbox.fill((255, 0, 0, 128))
        canvas.blit(retaliate_hitbox, (player.retaliate_rect.x - camera_x - x_camera_delay - screen_shake_x, player.retaliate_rect.y - camera_y - y_camera_delay - screen_shake_y))

    # pygame.draw.rect(canvas, (255,0,0), player.attack_rect)
   
    # for zombie in zombies:
    #     pygame.draw.rect(canvas, (0,255, 255), (zombie.rect.x - camera_x - x_camera_delay, zombie.rect.y - camera_y -y_camera_delay, zombie.rect.width, zombie.rect.height))
    # for zombie in zombies:
    #     pygame.draw.rect(canvas, (0,0, 255), (zombie.head_rect.x - camera_x - x_camera_delay, zombie.head_rect.y - camera_y -y_camera_delay, zombie.head_rect.width, zombie.head_rect.height))
    

    # if player.attack_rect is not None:
    #     pygame.draw.rect(canvas, (255, 0, 0), (player.attack_rect.x - camera_x - x_camera_delay, player.attack_rect.y - camera_y -y_camera_delay, player.attack_rect.width, player.attack_rect.height), 2)
    # if player.critical_rect is not None:   
    #     pygame.draw.rect(canvas, (0, 255, 0), (player.critical_rect.x - camera_x - x_camera_delay, player.critical_rect.y - camera_y -y_camera_delay, player.critical_rect.width, player.critical_rect.height), 2)
    # # if player.shock_rect is not None:
    #     pygame.draw.rect(canvas, (0, 0, 255), (player.shock_rect.x - camera_x - x_camera_delay, player.shock_rect.y - camera_y -y_camera_delay, player.shock_rect.width, player.shock_rect.height), 2)
        
        
    #new player render code:
    # above this will be the code determining the sprite and rect
    # canvas.blit(player_sprite, player_render_pos)
    #                  ^ x_flip will be used in here not in the actual rendering

    for zombie in zombies:
        zombie_chunk_x = zombie.rect.centerx // chunk_pixel_w # <-- what chunk the zombie is in 
        if abs(zombie_chunk_x - position_chunk_x) <= render_distance: #<-- if the chunk distance between the zombie and player is less than the player render distance
            zombie.current_frames = zombie.update_action(all_zombie_frames) #determines the current type of animation playing only if the animation mode changes
            zombie.update_zombie_frame() #update frame played and returns the animation mode
            zombie_sprite = zombie.current_frames[zombie.frame_index] #determines the image/sprite which will be displayed on player pos

            if zombie.on_fire:
            #creating fire overlay
                fire_version = zombie_sprite.copy()
                fire_overlay = pygame.Surface(fire_version.get_size(), pygame.SRCALPHA)
                fire_overlay.fill((255, 165, 0)) 
                fire_version.blit(fire_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                zombie_sprite = fire_version
            else:
                pass

            if zombie.shocked:
                shocked_version = zombie_sprite.copy()
                shocked_overlay = pygame.Surface(shocked_version.get_size(), pygame.SRCALPHA)
                shocked_overlay.fill((0, 0, 139)) 
                shocked_version.blit(shocked_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                zombie_sprite = shocked_version
            else:
                pass
            if zombie.animation_mode != 0:
                canvas.blit(zombie_sprite, zombie.render_pos) 
            else:
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

    # HUD
    hud.draw_hud(
        surface=canvas, 
        player=player, 
        zombies=zombies, 
        camera_x=camera_x, 
        camera_y=camera_y, 
        screen_w=base_res_x, 
        screen_h=base_res_y, 
        stage_kill_count=stage_dead_zombies, 
        font=hud_font_main, 
        font_small=hud_font_small,
        dash_icon=dash_icon
    )

    # *-- RENDER SHOP OVERLAY UI (LEAGUE OF LEGENDS AUGMENTS STYLE) --*
    if shop_active:
        shop_overlay = pygame.Surface((base_res_x, base_res_y), pygame.SRCALPHA)
        shop_overlay.fill((0, 0, 0, 205))
        canvas.blit(shop_overlay, (0, 0))

        shop_title = font_pause_title.render("PERKS SHOP", True, (240, 240, 240))
        canvas.blit(shop_title, shop_title.get_rect(center=(base_res_x / 2, 30)))

        # DOLLARS Display restricted exclusively to shop UI
        dollars_text = font_pause_small.render(f"Dollars: ${player.DOLLARS or 0}", True, (50, 255, 50))
        canvas.blit(dollars_text, dollars_text.get_rect(center=(base_res_x / 2, 55)))

        card_w, card_h = 120, 180
        shop_slots = len(current_shop_perks)
        start_x = (base_res_x - (shop_slots * card_w + (shop_slots - 1) * 30)) // 2
        card_y = 85

        for i in range(shop_slots):
            card_x = start_x + i * (card_w + 30)
            card_rect = pygame.Rect(card_x, card_y, card_w, card_h)
            
            perk = current_shop_perks[i]
            
            # Handle purchased / empty slots
            if perk is None:
                pygame.draw.rect(canvas, (30, 30, 30), card_rect)
                pygame.draw.rect(canvas, (70, 70, 70), card_rect, 3)
                sold_out = font_pause_small.render("SOLD", True, (255, 50, 50))
                canvas.blit(sold_out, sold_out.get_rect(center=card_rect.center))
                continue
                
            # Render Base Card Background
            pygame.draw.rect(canvas, (10, 10, 15), card_rect)

            # Rarity Specific Visuals
            if perk['rarity'] == 'Budget':
                border_color = (150, 255, 150) # Light Green
            elif perk['rarity'] == 'Mid':
                border_color = (100, 150, 255) # Light Blue
            else:
                border_color = (255, 200, 50)  # Gold
                
            pygame.draw.rect(canvas, border_color, card_rect, 3)

            # Draw Perk Title
            name_text = font_perk_title.render(perk['name'], True, border_color)
            canvas.blit(name_text, name_text.get_rect(midtop=(card_rect.centerx, card_rect.y + 10)))
            
            # Draw Detailed Wrapped Text Description
            desc_rect = pygame.Rect(card_rect.x + 8, card_rect.y + 35, card_rect.width - 16, card_rect.height - 60)
            draw_text_wrapped(canvas, perk['desc'], (200, 200, 200), desc_rect, font_perk_desc)

            # Draw Cost at the bottom of the card
            cost_text = font_perk_desc.render(f"${perk['cost']}", True, (50, 255, 50))
            canvas.blit(cost_text, cost_text.get_rect(midbottom=(card_rect.centerx, card_rect.bottom - 10)))


        timer_string = f"TIME: {max(0, shop_timer):.1f}  |  Purchases Left: {purchases_allowed - current_purchases}"
        timer_text = font_pause_small.render(timer_string, True, (240, 240, 240))
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