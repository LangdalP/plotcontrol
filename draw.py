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
import uuid
from enum import Enum

# TODO
# - Teste at dette funkar som vi forventar
# - Kor skal nye paths starte? Kan dei starte p 0, 0?
# - Finne ut: Skal folk kunne tegne ansikt p avgrensa kvadrantar p eit ark
# - Finne ut: M dei som styrer standen bytte til eit clean ark nr plotteren skal i tegn-sjlv-modus?

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

JOYSTICK_POLL_INTERVAL = 0.03 # Seconds
JOYSTICK_SPEED_MULTIPLIER = 0.5

PLOTTER_X_MIN = 1
PLOTTER_Y_MIN = 1
PLOTTER_X_MAX = 25
PLOTTER_Y_MAX = 17

DRAW_FACTOR = 50

# Global state
plotter_x = PLOTTER_X_MIN
plotter_y = PLOTTER_Y_MIN
paths = []
relative_line_segments = []

program_state = ProgramState.DRAW_EYES

plotter = None
pen_is_down = False

fname = uuid.uuid4().hex

def xy_filtered(x, y):
    radius = math.sqrt(x**2 + y**2)
    return (0, 0) if radius < 0.2 else (x, y)

def next_program_state():
    global program_state
    if program_state == ProgramState.DRAW_EYES:
        program_state = ProgramState.DRAW_NOSE
    elif program_state == ProgramState.DRAW_NOSE:
        program_state = ProgramState.DRAW_MOUTH
    elif program_state == ProgramState.DRAW_MOUTH:
        program_state = ProgramState.DRAW_EYES

def toggle_pen_up_down():
    global plotter, pen_is_down, relative_line_segments
    pen_is_down = not pen_is_down
    if pen_is_down:
        print("pendown")
        relative_line_segments = []
        if plotter:
            plotter.pendown()
    else:
        print("penup")
        paths.append(relative_line_segments)
        relative_line_segments = []
        if plotter:
            plotter.penup()

def x_box_a_button_is_pressed(event):
     return event.type == pygame.JOYBUTTONDOWN and event.button == 0

def x_box_b_button_is_pressed(event):
  return event.type == pygame.JOYBUTTONDOWN and event.button == 1

def x_box_y_button_is_pressed(event):
    return event.type == pygame.JOYBUTTONDOWN and event.button == 2

def quit():
    if plotter:
        plotter.moveto(0, 0)
        plotter.disconnect()
    cleanup_and_exit()

def save_svg():
    global relative_line_segments, program_state, paths, fname
    svg_paths = svg.create_full_paths(paths)

    folder = DRAWING_PATH_DICT[program_state.name]
    svg.save_svg([svg_paths], folder + "/" + fname + ".svg")
    relative_line_segments = []
    paths = []

def reset(surface, plotter):
    global fname, plotter_x, plotter_y
    print("reset")
    fname = uuid.uuid4().hex
    clear(surface)
    relative_line_segments = []
    paths = []
    if plotter:
        plotter.moveto(PLOTTER_X_MIN, PLOTTER_Y_MIN)
    plotter_x = PLOTTER_X_MIN
    plotter_y = PLOTTER_Y_MIN


def start_game_loop(surface, joystick, plotter):
    global plotter_x, plotter_y, relative_line_segments, pen_is_down
    pygame.display.update()
    lastJoystickPollTime = time.time()
    plotter_x = PLOTTER_X_MIN
    plotter_y = PLOTTER_Y_MIN


    if plotter:
        plotter.goto(plotter_x, plotter_y)

    while True:
        new_events = pygame.event.get()
        for event in new_events:
            if x_box_a_button_is_pressed(event):
                toggle_pen_up_down()
            if x_box_b_button_is_pressed(event):
                paths.append(relative_line_segments)
                save_svg()
                next_program_state()
                if program_state == ProgramState.DRAW_EYES:
                    reset(surface, plotter)

                    pygame.display.update()
            if event.type == QUIT:
                quit()

        currentTime = time.time()
        timeSinceLastPoll = currentTime - lastJoystickPollTime
        if timeSinceLastPoll > JOYSTICK_POLL_INTERVAL:
            x_raw = joystick.get_axis(0)
            y_raw = joystick.get_axis(1)
            (x, y) = xy_filtered(x_raw, y_raw)
            (dx, dy) = (JOYSTICK_SPEED_MULTIPLIER*x, JOYSTICK_SPEED_MULTIPLIER*y)
            if not (dx == 0 and dy == 0):
                # svg

                (old_plotter_x, old_plotter_y) = (plotter_x, plotter_y)
                plotter_x = min(max(plotter_x + dx, PLOTTER_X_MIN), PLOTTER_X_MAX)
                plotter_y = min(max(plotter_y + dy, PLOTTER_Y_MIN), PLOTTER_Y_MAX)


                (dx, dy) = (plotter_x - old_plotter_x, plotter_y - old_plotter_y)
                if not (dx == 0 and dy == 0):
                    relative_line_segments.append((plotter_x, plotter_y))


                    if plotter:
                        plotter.goto(plotter_x, plotter_y)
                    color = RED if pen_is_down else BLUE
                    draw_line(surface,
                    old_plotter_x*DRAW_FACTOR,
                    old_plotter_y*DRAW_FACTOR,
                    plotter_x*DRAW_FACTOR,
                    plotter_y*DRAW_FACTOR,
                    color)
                    pygame.display.update()
                    print(f'Plot moveto: {plotter_x}, {plotter_y}')
                    lastJoystickPollTime = time.time()


def main():
    global plotter, surface
    surface = init_and_create_window()
    draw_pointer(surface, plotter_x*DRAW_FACTOR, plotter_y*DRAW_FACTOR)
    draw_border(surface,
    PLOTTER_X_MIN * DRAW_FACTOR,
    PLOTTER_Y_MIN * DRAW_FACTOR,
    (PLOTTER_X_MAX - PLOTTER_X_MIN) * DRAW_FACTOR,
    (PLOTTER_Y_MAX -PLOTTER_X_MIN) * DRAW_FACTOR)

    joystick = init_joystick()
    if joystick == None:
        cleanup_and_exit()

    plotter = init_plotter_interactive()


    try:
        start_game_loop(surface, joystick, plotter)
    except Exception as e:
        print(e)
        if plotter:
            plotter.moveto(0, 0)
            plotter.disconnect()
        cleanup_and_exit()


if __name__ == '__main__':
    main()
