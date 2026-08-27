import pygame, sys
from pygame.locals import *
from spritesheet import Spritesheet
from tilemap import *
pygame.init()

clock = pygame.time.Clock()

#grab resolution for the users monitor
resolution = pygame.display.get_desktop_sizes()
#baseline resolution
base_res_x, base_res_y = 640, 360        

display_w , display_h = resolution[0]   #index 0 for the first monitor   
window_w, window_h = 1280,720
screen_state_w, screen_state_h = window_w, window_h

#camera movement
camera_x=0
camera_y=0
camera_speed=5

#base window status
status = RESIZABLE

canvas = pygame.Surface((base_res_x, base_res_y))
screen = pygame.display.set_mode((screen_state_w, screen_state_h), status)


#map
sprites = Spritesheet('spritesheet.png')
map_files = ['screen1.csv', 'screen2.csv','screen3.csv'] #passes the csv file and the png file into the map variable

maps = [TileMap(file,sprites) for file in map_files]

#combine both map
total_map_w = sum(m.map_w  for m in maps)   #loops through maps list
total_map_h = max(m.map_h for m in maps)

while True:

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

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

    key_input = pygame.key.get_pressed()
    if key_input[K_a]:
        camera_x -=camera_speed
    if key_input[K_d]:
        camera_x +=camera_speed

    #map clamping      
    max_cam_x = total_map_w - base_res_x
    max_cam_y = total_map_h - base_res_y

    camera_x = max(0, min(camera_x, max_cam_x))
    camera_y = max(0, min(camera_y, max_cam_y))

    canvas.fill((159, 215, 255))    #nice sky background
    current_offset_x = 0
    for tile_map in maps:
        tile_map.draw_map(canvas, camera_x, camera_y, offset_x = current_offset_x)
        current_offset_x += tile_map.map_w

    #scale the screen
    scaled_resolution = pygame.transform.scale(canvas, (screen_state_w, screen_state_h))

    screen.blit(scaled_resolution,(0,0))   #creates a window to be displayed
    pygame.display.update()
    clock.tick(60)