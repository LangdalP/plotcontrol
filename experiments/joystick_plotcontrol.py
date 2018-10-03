import pygame
from pygame.locals import *
from pygame.joystick import *
from utils.io_utils import *
from utils.colors import *
from utils.gfx_utils import *
from utils.plotter_utils import *
import utils.svg_utils as svg

import sys
import time
import math
import time

# Constants
JOYSTICK_POLL_INTERVAL = 0.00 # Seconds
JOYSTICK_SPEED_MULTIPLIER = 0.7

POINTER_START_X = 0
POINTER_START_Y = 0

PLOTTER_X_MIN = 1
PLOTTER_Y_MIN = 1
PLOTTER_X_MAX = 25
PLOTTER_Y_MAX = 17

# Global state
pointer_x = POINTER_START_X
pointer_y = POINTER_START_Y
relative_line_segments = []

plotter_x = 0
plotter_y = 0


def xy_filtered(x, y):
    radius = math.sqrt(x**2 + y**2)
    return (0, 0) if radius < 0.2 else (x, y)

def start_game_loop(surface, joystick, plotter):
    global pointer_x, pointer_y, relative_line_segments, plotter_x, plotter_y
    pygame.display.update()

    lastJoystickPollTime = time.time()
    while True:
        new_events = pygame.event.get()
        for event in new_events:
            if event.type == pygame.JOYBUTTONDOWN:
                print("Joystick button pressed.")
                plotter.pendown()
            if event.type == pygame.JOYBUTTONUP:
                print("Joystick button released.")
                plotter.penup()
            if event.type == QUIT:
                plotter.moveto(0, 0)
                plotter.disconnect()
                cleanup_and_exit()
        
        currentTime = time.time()
        timeSinceLastPoll = currentTime - lastJoystickPollTime
        if timeSinceLastPoll > JOYSTICK_POLL_INTERVAL:
            lastJoystickPollTime = time.time()
            x_raw = joystick.get_axis(0)
            y_raw = joystick.get_axis(1)
            (x, y) = xy_filtered(x_raw, y_raw)
            (dx, dy) = (JOYSTICK_SPEED_MULTIPLIER*x, JOYSTICK_SPEED_MULTIPLIER*y)
            if not (dx == 0 and dy == 0):
                plotter_x = min(max(plotter_x + dx, PLOTTER_X_MIN), PLOTTER_X_MAX)
                plotter_y = min(max(plotter_y + dy, PLOTTER_Y_MIN), PLOTTER_Y_MAX)
                plotter.goto(plotter_x, plotter_y)
                print(f'Plot moveto: {plotter_x}, {plotter_y}')
            if dx != 0 and dy != 0:
                relative_line_segments.append((dx, dy))

def main():
    surface = init_and_create_window()
    draw_pointer(surface, pointer_x, pointer_y)

    joystick = init_joystick()
    if joystick == None:
        cleanup_and_exit()

    plotter = init_plotter_interactive()
    if plotter == None:
        cleanup_and_exit()
    
    start_game_loop(surface, joystick, plotter)
    
if __name__ == '__main__':
    main()
