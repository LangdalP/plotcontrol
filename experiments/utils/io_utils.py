import pygame
import sys
from pygame.locals import *
from pygame.joystick import *
from utils.colors import *

def init_and_create_window():
    pygame.init()
    windowSurface = pygame.display.set_mode((500, 400), 0, 32)
    pygame.display.set_caption('Joystick SVG')
    windowSurface.fill(WHITE)
    return windowSurface

def init_joystick():
    num_joysticks = pygame.joystick.get_count()
    print(f'Fant {num_joysticks} joysticks')

    my_joystick = None
    if (num_joysticks > 0):
        my_joystick = pygame.joystick.Joystick(0) # Vi skal bruke den "nullte" joysticken
        my_joystick.init()
    return my_joystick

def cleanup_and_exit():
    pygame.quit()
    sys.exit()
