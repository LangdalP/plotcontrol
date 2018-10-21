import pygame
from pygame.locals import *
from pygame.joystick import *
from utils.io_utils import *
from utils.colors import *
from utils.plotter_utils import *
from utils.facemaker import generate_face
import utils.gfx_utils as gfx
import utils.svg_utils as svg

import sys
import time
import math
import time
import uuid
from enum import Enum

class ProgramState(Enum):
    DRAW_EYES = 1
    DRAW_NOSE = 2
    DRAW_MOUTH = 3
    PAUSE = 4
    GENERATIVE = 5

# Constants
DRAWING_PATH_DICT = {
    "DRAW_EYES": "input/eyes",
    "DRAW_NOSE": "input/nose",
    "DRAW_MOUTH": "input/mouth",
}

INSTRUKSJON_DICT = {
    "DRAW_EYES_1": "Tegn øyne",
    "DRAW_EYES_2": "Trykk X når du vil gå videre",
    "DRAW_NOSE_1": "Tegn en nese",
    "DRAW_NOSE_2": "Trykk X når du vil gå videre",
    "DRAW_MOUTH_1": "Tegn en munn",
    "DRAW_MOUTH_2": "Trykk X for å avslutte",
    "PAUSE_1": "Fri modus",
    "PAUSE_2": "Sett i blankt ark og trykk X for å tegne ansikt",
    "GENERATIVE_1": "Harry Plotter tegner ansikter basert",
    "GENERATIVE_2": "på hva andre har tegnet tidligere i dag",
}

XBOX_A_BTN = 0
XBOX_B_BTN = 1
XBOX_X_BTN = 2
XBOX_BACK_BTN = 6

JOYSTICK_SPEED_MULTIPLIER = 0.5

ORIGIN_OFFSET = 1 # 1 cm in both directions from true (0, 0) to paper's (0, 0)
PLOTTER_X_MIN = 2.5 + ORIGIN_OFFSET
PLOTTER_Y_MIN = 2.5 + ORIGIN_OFFSET
PLOTTER_X_MAX = 26.5 + ORIGIN_OFFSET
PLOTTER_Y_MAX = 18.5 + ORIGIN_OFFSET

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
    return (0, 0) if radius < 0.3 else (x, y)

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
        plotter.moveto(1.5, 1.5)
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

speed_pen_down = 10
speed_pen_up = 90

def draw_border():
    global spd
    if plotter:
        plotter.options.speed_pendown = 90
        plotter.update()
        plotter.moveto(PLOTTER_X_MIN, PLOTTER_Y_MIN)
        plotter.pendown()
        plotter.goto(PLOTTER_X_MIN, PLOTTER_Y_MAX)
        plotter.goto(PLOTTER_X_MAX, PLOTTER_Y_MAX)
        plotter.goto(PLOTTER_X_MAX, PLOTTER_Y_MIN)
        plotter.goto(PLOTTER_X_MIN, PLOTTER_Y_MIN)
        plotter.penup()
        plotter.options.speed_pendown = speed_pen_down
        plotter.update()

def reset(surface, plotter, should_draw_border=True):
    global fname
    print("Resetting game state")
    fname = uuid.uuid4().hex
    gfx.clear(surface)
    relative_line_segments = []
    paths = []
    if plotter and should_draw_border:
        draw_border()

def start_game_loop(surface, joystick, plotter):
    global plotter_x, plotter_y, relative_line_segments, program_state
    pygame.display.update()
    plotter_x = PLOTTER_X_MIN
    plotter_y = PLOTTER_Y_MIN
    if plotter:
        plotter.moveto(plotter_x, plotter_y)
    reset(surface, plotter, False)

    pen_is_down = False

    while True:
        new_events = pygame.event.get()
        for event in new_events:
            if event.type == pygame.KEYUP and event.key == pygame.K_g and program_state == ProgramState.PAUSE:
                program_state = ProgramState.GENERATIVE
                print("Entered generative mode")
                if plotter:
                    plotter.moveto(0, 0)
                    disconnect_serial(plotter)
            if event.type == pygame.KEYUP and event.key == pygame.K_RETURN and program_state == ProgramState.GENERATIVE:
                generated_svg_path = generate_face()
                if plotter:
                    start_svg_plot(plotter, generated_svg_path)
            if event.type == pygame.KEYUP and event.key == pygame.K_i and program_state == ProgramState.GENERATIVE:
                program_state = ProgramState.PAUSE
                if plotter:
                    go_back_to_interactive_mode(plotter)
                    plotter.moveto(PLOTTER_X_MIN, PLOTTER_Y_MIN)
                    plotter_x = PLOTTER_X_MIN
                    plotter_y = PLOTTER_Y_MIN

                reset(surface, plotter, False)
                print("Entered interactive mode and pause state")
            if event.type == pygame.JOYBUTTONDOWN and event.button == XBOX_A_BTN and program_state != ProgramState.GENERATIVE:
                print("Pen down")
                pen_is_down = True
                if plotter:
                    plotter.pendown()
                if program_state != ProgramState.PAUSE:
                    reset_lines()
            if event.type == pygame.JOYBUTTONUP and event.button == XBOX_A_BTN and program_state != ProgramState.GENERATIVE:
                print("Pen up")
                pen_is_down = False
                if plotter:
                    plotter.penup()
                if program_state != ProgramState.PAUSE:
                    save_lines()
            # Gå til neste state
            if event.type == pygame.JOYBUTTONUP and event.button == XBOX_X_BTN and program_state != ProgramState.GENERATIVE:
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
            if event.type == pygame.JOYBUTTONDOWN and event.button == XBOX_BACK_BTN and program_state != ProgramState.GENERATIVE:
                quit()
            if event.type == QUIT:
                quit()

        if program_state == ProgramState.GENERATIVE:
            gfx.clear(surface)
            text1 = font_renderer.render(INSTRUKSJON_DICT["GENERATIVE_1"], False, (0, 0, 0))
            text2 = font_renderer.render(INSTRUKSJON_DICT["GENERATIVE_2"], False, (0, 0, 0))
            gfx.render_text(surface, text1, 500)
            gfx.render_text(surface, text2, 600)
            pygame.display.update()
        else:
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
                old_plotter_y*DRAW_FACTOR + 500,
                -1*old_plotter_x*DRAW_FACTOR + 870,
                plotter_y*DRAW_FACTOR + 500,
                -1*plotter_x*DRAW_FACTOR + 870,
                color)
                print(f'Plotter: {plotter_x}, {plotter_y}')

            gfx.draw_border(surface,
                PLOTTER_X_MIN * DRAW_FACTOR + PREVIEW_OFFSET_X,
                (PLOTTER_Y_MAX - PLOTTER_X_MIN) * DRAW_FACTOR,
                PLOTTER_Y_MIN * DRAW_FACTOR + PREVIEW_OFFSET_Y,
                (PLOTTER_X_MAX - PLOTTER_X_MIN) * DRAW_FACTOR)

            instruksjon1 = INSTRUKSJON_DICT[program_state.name + "_1"]
            instruksjon2 = INSTRUKSJON_DICT[program_state.name + "_2"]
            text1 = font_renderer.render(instruksjon1, False, (0, 0, 0))
            text2 = font_renderer.render(instruksjon2, False, (0, 0, 0))
            gfx.draw_text_background(surface)
            gfx.render_text(surface, text1, 100)
            gfx.render_text(surface, text2, 180)
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

    plotter = init_plotter_interactive(speed_pen_down, speed_pen_up)


    try:
        start_game_loop(surface, joystick, plotter)
    except Exception as e:
        print(e)
        quit()


if __name__ == '__main__':
    main()
