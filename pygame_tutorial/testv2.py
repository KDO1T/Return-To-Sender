from sys import exit
import pygame

pygame.init()

# --- WINDOW CONFIGURATION ---
width = 1280
height = 720
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Return To Sender")
clock = pygame.time.Clock()

# --- COLORS & FONTS ---
bg_colour = (15, 15, 20)
font_colour = (160, 160, 170)
title_colour = (240, 240, 240)
selected_colour = (235, 65, 40)

font_title = pygame.font.SysFont("Georgia", 56, bold=True)
font = pygame.font.SysFont("Arial", 28, bold=True)

# --- GAME STATE DATA ---
current_state = "MAIN"
main_options = ["Play", "Options", "Quit"]
selected_main = 0

play_options = ["Save Slot 1", "Save Slot 2", "Save Slot 3", "Skill Tree", "Back"]
selected_play = 0


# --- ACTION HANDLER ---
def handle_action(option):
    global current_state
    if current_state == "MAIN":
        if option == "Play":
            current_state = "PLAY"
        elif option == "Options":
            print("[ACTION] Options Screen Placeholder")
        elif option == "Quit":
            pygame.quit()
            exit()

    elif current_state == "PLAY":
        if option == "Back":
            current_state = "MAIN"
        elif "Save Slot" in option:
            print(f"[ACTION] Loading {option}...")
            current_state = "GAMEPLAY"  # Example: Switch to real gameplay!
        elif option == "Skill Tree":
            print("[ACTION] Skill Tree Opened")


# --- STATE RENDER FUNCTIONS (Single Frame Only) ---
def draw_main_menu():
    title_surface = font_title.render("RETURN TO SENDER", True, title_colour)
    screen.blit(title_surface, (80, 80))

    start_y = 260
    for index, option in enumerate(main_options):
        if index == selected_main:
            color = selected_colour
            display_text = f"> {option}"
        else:
            color = font_colour
            display_text = option

        text_surface = font.render(display_text, True, color)
        screen.blit(text_surface, (80, start_y + (index * 60)))


def draw_play_menu():
    title_surface = font_title.render("SELECT PROFILE", True, title_colour)
    screen.blit(title_surface, (80, 60))

    for i in range(3):
        box_rect = pygame.Rect(80, 160 + (i * 110), 450, 90)
        border_color = selected_colour if i == selected_play else (60, 60, 75)
        text_color = selected_colour if i == selected_play else font_colour

        pygame.draw.rect(screen, (30, 30, 40), box_rect, border_radius=8)
        pygame.draw.rect(screen, border_color, box_rect, width=2, border_radius=8)

        slot_title = font.render(f"Save Slot {i + 1}", True, text_color)
        screen.blit(slot_title, (box_rect.x + 20, box_rect.y + 15))

    bottom_options = [("Skill Tree", 3), ("Back", 4)]
    for text, index in bottom_options:
        color = selected_colour if selected_play == index else font_colour
        display_text = f"> {text}" if selected_play == index else text
        y_pos = 520 if text == "Skill Tree" else 580

        text_surface = font.render(display_text, True, color)
        screen.blit(text_surface, (80, y_pos))


def draw_gameplay():
    # Placeholder for when actual gameplay begins!
    game_text = font_title.render("GAMEPLAY SCREEN", True, title_colour)
    screen.blit(game_text, (80, 80))


# --- SINGLE CENTRAL MAIN LOOP ---
while True:
    mouse_pos = pygame.mouse.get_pos()

    # 1. EVENT HANDLING
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        elif event.type == pygame.MOUSEMOTION:
            if current_state == "MAIN":
                for index in range(len(main_options)):
                    if pygame.Rect(80, 260 + (index * 60), 300, 40).collidepoint(mouse_pos):
                        selected_main = index
            elif current_state == "PLAY":
                for i in range(3):
                    if pygame.Rect(80, 160 + (i * 110), 450, 90).collidepoint(mouse_pos):
                        selected_play = i
                if pygame.Rect(80, 520, 300, 40).collidepoint(mouse_pos):
                    selected_play = 3
                elif pygame.Rect(80, 580, 300, 40).collidepoint(mouse_pos):
                    selected_play = 4

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if current_state == "MAIN":
                handle_action(main_options[selected_main])
            elif current_state == "PLAY":
                handle_action(play_options[selected_play])

        elif event.type == pygame.KEYDOWN:
            if current_state == "MAIN":
                if event.key in (pygame.K_UP, pygame.K_w):
                    selected_main = (selected_main - 1) % len(main_options)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    selected_main = (selected_main + 1) % len(main_options)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    handle_action(main_options[selected_main])

            elif current_state == "PLAY":
                if event.key in (pygame.K_UP, pygame.K_w):
                    selected_play = (selected_play - 1) % len(play_options)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    selected_play = (selected_play + 1) % len(play_options)
                elif event.key == pygame.K_ESCAPE:
                    current_state = "MAIN"
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    handle_action(play_options[selected_play])

            elif current_state == "GAMEPLAY":
                if event.key == pygame.K_ESCAPE:
                    current_state = "MAIN"

    # 2. RENDERING ROUTER
    screen.fill(bg_colour)

    if current_state == "MAIN":
        draw_main_menu()
    elif current_state == "PLAY":
        draw_play_menu()
    elif current_state == "GAMEPLAY":
        draw_gameplay()

    pygame.display.update()
    clock.tick(60)