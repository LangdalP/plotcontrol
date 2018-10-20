import pygame
from pygame.locals import *
from pygame.joystick import *
from utils.io_utils import *
from utils.colors import *
from utils.plotter_utils import *
import utils.gfx_utils as gfx
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
    PAUSE = 4

# Constants
DRAWING_PATH_DICT = {
    "DRAW_EYES": "drawings/eyes",
    "DRAW_NOSE": "drawings/nose",
    "DRAW_MOUTH": "drawings/mouth",
}

INSTRUKSJON_DICT = {
    "DRAW_EYES": "Trykk A når du vil tegne nesa",
    "DRAW_NOSE": "Trykk A når du vil tegne munnen",
    "DRAW_MOUTH": "Trykk A for å avslutte",
    "PAUSE": "Trykk A når du vil tegne øynene",
}

XBOX_A_BTN = 0
XBOX_B_BTN = 1
XBOX_X_BTN = 2
XBOX_BACK_BTN = 6

JOYSTICK_SPEED_MULTIPLIER = 0.5

PLOTTER_X_MIN = 2.5
PLOTTER_Y_MIN = 2.5
PLOTTER_X_MAX = 26.5
PLOTTER_Y_MAX = 18.5

PLOTTER_X_MID = (PLOTTER_X_MAX - PLOTTER_X_MIN) / 2 + PLOTTER_X_MIN
PLOTTER_Y_MID = (PLOTTER_Y_MAX - PLOTTER_Y_MIN) / 2 + PLOTTER_Y_MIN

# Var 50
DRAW_FACTOR = 20
PREVIEW_OFFSET_X = 500
PREVIEW_OFFSET_Y = 300

# Global state
plotter_x = PLOTTER_X_MIN
plotter_y = PLOTTER_Y_MIN
paths = []
relative_line_segments = []

# GFX
font_renderer = None
window_width = None
window_height = None

program_state = ProgramState.PAUSE

plotter = None

fname = uuid.uuid4().hex

def xy_filtered(x, y):
    radius = math.sqrt(x**2 + y**2)
    return (0, 0) if radius < 0.2 else (x, y)

def next_program_state():
    global program_state
    if program_state == ProgramState.DRAW_EYES:
        program_state = ProgramState.DRAW_NOSE
        print("draw nose")
    elif program_state == ProgramState.DRAW_NOSE:
        program_state = ProgramState.DRAW_MOUTH
        print("draw mouth")
    elif program_state == ProgramState.DRAW_MOUTH:
        program_state = ProgramState.PAUSE
        print("pause")
    elif program_state == ProgramState.PAUSE:
        program_state = ProgramState.DRAW_EYES
        print("draw eyes")

def reset_lines():
    global relative_line_segments
    relative_line_segments = []

def save_lines():
    global paths, relative_line_segments
    paths.append(relative_line_segments)
    relative_line_segments = []

def quit():
    print("Shutting down program")
    if plotter:
        plotter.moveto(0, 0)
        plotter.disconnect()
    cleanup_and_exit()

def save_svg():
    global relative_line_segments, paths, fname
    svg_paths = svg.create_full_paths(paths)

    if svg_paths:
        folder = DRAWING_PATH_DICT[program_state.name]
        svg.save_svg([svg_paths], folder + "/" + fname + ".svg")
        relative_line_segments = []
        paths = []

def draw_border():
    if plotter:
        plotter.moveto(PLOTTER_X_MIN, PLOTTER_Y_MIN)
        plotter.pendown()
        plotter.goto(PLOTTER_X_MIN, PLOTTER_Y_MAX)
        plotter.goto(PLOTTER_X_MAX, PLOTTER_Y_MAX)
        plotter.goto(PLOTTER_X_MAX, PLOTTER_Y_MIN)
        plotter.goto(PLOTTER_X_MIN, PLOTTER_Y_MIN)
        plotter.penup()

def reset(surface, plotter):
    global fname
    print("Resetting game state")
    fname = uuid.uuid4().hex
    gfx.clear(surface)
    relative_line_segments = []
    paths = []
    if plotter:
        draw_border()

def start_game_loop(surface, joystick, plotter):
    global plotter_x, plotter_y, relative_line_segments
    pygame.display.update()
    plotter_x = PLOTTER_X_MIN
    plotter_y = PLOTTER_Y_MIN
    reset(surface, plotter)

    pen_is_down = False

    while True:
        new_events = pygame.event.get()
        for event in new_events:
            if event.type == pygame.JOYBUTTONDOWN and event.button == XBOX_A_BTN:
                print("Pen down")
                pen_is_down = True
                if plotter:
                    plotter.pendown()
                if program_state != ProgramState.PAUSE:
                    reset_lines()
            if event.type == pygame.JOYBUTTONUP and event.button == XBOX_A_BTN:
                print("Pen up")
                pen_is_down = False
                if plotter:
                    plotter.penup()
                if program_state != ProgramState.PAUSE:
                    save_lines()
            # Gå til neste state
            if event.type == pygame.JOYBUTTONUP and event.button == XBOX_X_BTN: # TODO: Sjekk at dette faktisk er X
                if program_state != ProgramState.PAUSE:
                    # Må simulere pen-up
                    if pen_is_down:
                        pen_is_down = False
                        if plotter:
                            plotter.penup()
                        if program_state != ProgramState.PAUSE:
                            save_lines()
                    save_svg()
                
                if plotter:
                    # Let plotter do a "nod"
                    plotter.moveto(plotter_x+0.5, plotter_y)
                    plotter.moveto(plotter_x, plotter_y)

                next_program_state()

                if program_state == ProgramState.PAUSE:
                    if plotter:
                        plotter.penup()
                        plotter.moveto(PLOTTER_X_MIN, PLOTTER_Y_MIN)

                if program_state == ProgramState.DRAW_EYES:
                    reset(surface, plotter)
                    plotter_x = PLOTTER_X_MID
                    plotter_y = PLOTTER_Y_MID

                    if plotter:
                        plotter.goto(plotter_x, plotter_y)

                    pygame.display.update()
            if event.type == pygame.JOYBUTTONDOWN and event.button == XBOX_BACK_BTN:
                quit()
            if event.type == QUIT:
                quit()

        x_raw = -1 * joystick.get_axis(1)
        y_raw = joystick.get_axis(0)
        (x, y) = xy_filtered(x_raw, y_raw)
        (dx, dy) = (JOYSTICK_SPEED_MULTIPLIER*x, JOYSTICK_SPEED_MULTIPLIER*y)
        if not (dx == 0 and dy == 0):
            (old_plotter_x, old_plotter_y) = (plotter_x, plotter_y)
            plotter_x = min(max(plotter_x + dx, PLOTTER_X_MIN), PLOTTER_X_MAX)
            plotter_y = min(max(plotter_y + dy, PLOTTER_Y_MIN), PLOTTER_Y_MAX)

            relative_line_segments.append((plotter_x, plotter_y))

            if plotter:
                plotter.goto(plotter_x, plotter_y)
            
            color = RED if pen_is_down else BLUE
            gfx.draw_line(surface,
            old_plotter_x*DRAW_FACTOR + PREVIEW_OFFSET_X,
            old_plotter_y*DRAW_FACTOR + PREVIEW_OFFSET_Y,
            plotter_x*DRAW_FACTOR + PREVIEW_OFFSET_X,
            plotter_y*DRAW_FACTOR + PREVIEW_OFFSET_Y,
            color)
            print(f'Plotter: {plotter_x}, {plotter_y}')

        gfx.draw_border(surface,
            PLOTTER_X_MIN * DRAW_FACTOR + PREVIEW_OFFSET_X,
            PLOTTER_Y_MIN * DRAW_FACTOR + PREVIEW_OFFSET_Y,
            (PLOTTER_X_MAX - PLOTTER_X_MIN) * DRAW_FACTOR,
            (PLOTTER_Y_MAX -PLOTTER_X_MIN) * DRAW_FACTOR)
        instruksjon = INSTRUKSJON_DICT[program_state.name]
        text = font_renderer.render(instruksjon, False, (0, 0, 0))
        gfx.render_text(surface, text)
        pygame.display.update()


def main():
    global plotter, surface, font_renderer, window_width, window_height
    surface = init_and_create_window()
    font_renderer = init_font_rendering()
    window_width, window_height = surface.get_size()

    gfx.draw_pointer(surface, plotter_x*DRAW_FACTOR + PREVIEW_OFFSET_X, plotter_y*DRAW_FACTOR + PREVIEW_OFFSET_Y)
    gfx.draw_border(surface,
    PLOTTER_X_MIN * DRAW_FACTOR + PREVIEW_OFFSET_X,
    PLOTTER_Y_MIN * DRAW_FACTOR + PREVIEW_OFFSET_Y,
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
        quit()


if __name__ == '__main__':
    main()
