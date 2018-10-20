import pygame
import sys
from pygame.locals import *
from pygame.joystick import *
from utils.colors import *

def init_and_create_window():
    pygame.init()
    pygame.font.init()
    windowSurface = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
    pygame.display.set_caption('Joystick SVG')
    windowSurface.fill(WHITE)
    return windowSurface

def init_font_rendering():
    pygame.font.init()
    textfont = pygame.font.SysFont('Helvetica', 70)
    return textfont

def init_joystick():
    num_joysticks = pygame.joystick.get_count()
    print(f'Fant {num_joysticks} joysticks')

    my_joystick = None
    if (num_joysticks > 0):
        my_joystick = pygame.joystick.Joystick(0) # Vi skal bruke den "nullte" joysticken
        my_joystick.init()
        num_buttons = my_joystick.get_numbuttons()
        print(f'Fant {num_buttons} knapper')
    return my_joystick

def cleanup_and_exit():
    pygame.quit()
    sys.exit()
