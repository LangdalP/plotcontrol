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
from enum import Enum

# TODO
# - Teste at dette funkar som vi forventar
# - Kor skal nye paths starte? Kan dei starte på 0, 0?
# - Finne ut: Skal folk kunne tegne ansikt på avgrensa kvadrantar på eit ark
# - Finne ut: Må dei som styrer standen bytte til eit clean ark når plotteren skal i tegn-sjølv-modus?

class ProgramState(Enum):
    DRAW_EYES = 1
    DRAW_NOSE = 2
    DRAW_MOUTH = 3

# Constants
DRAWING_PATH_DICT = {
    "DRAW_EYES": "drawings/eyes",
    "DRAW_NOSE": "drawings/nose",
    "DRAW_MOUTH": "drawings/mouth",
}

JOYSTICK_SPEED_MULTIPLIER = 0.5

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
    pen_should_be_down = False
    program_state = ProgramState.DRAW_EYES

    while True:
        new_events = pygame.event.get()
        for event in new_events:
            if event.type == pygame.JOYBUTTONDOWN and event.button == 0: # XBOX A
                pen_is_down = not pen_is_down
                if pen_should_be_down:
                    plotter.pendown()
                else:
                    plotter.penup()
            if event.type == pygame.JOYBUTTONDOWN and event.button == 1: # XBOX B
                path = svg.create_path(POINTER_START_X, POINTER_START_Y, relative_line_segments)
                fname = uuid.uuid4().hex
                folder = DRAWING_PATH_DICT[program_state.name]
                svg.save_svg([path], folder + "/" + fname + ".svg")
                relative_line_segments = []
                
                if program_state == ProgramState.DRAW_EYES:
                    program_state = ProgramState.DRAW_NOSE
                elif program_state == ProgramState.DRAW_NOSE:
                    program_state = ProgramState.DRAW_MOUTH
                elif program_state == ProgramState.DRAW_MOUTH:
                    program_state = ProgramState.DRAW_EYES
            if event.type == QUIT:
                plotter.moveto(0, 0)
                plotter.disconnect()
                cleanup_and_exit()
        
        x_raw = joystick.get_axis(0)
        y_raw = joystick.get_axis(1)
        (x, y) = xy_filtered(x_raw, y_raw)
        (dx, dy) = (JOYSTICK_SPEED_MULTIPLIER*x, JOYSTICK_SPEED_MULTIPLIER*y)
        if not (dx == 0 and dy == 0):
            relative_line_segments.append((dx, dy))
            plotter_x = min(max(plotter_x + dx, PLOTTER_X_MIN), PLOTTER_X_MAX)
            plotter_y = min(max(plotter_y + dy, PLOTTER_Y_MIN), PLOTTER_Y_MAX)
            plotter.goto(plotter_x, plotter_y)
            print(f'Plot moveto: {plotter_x}, {plotter_y}')

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
