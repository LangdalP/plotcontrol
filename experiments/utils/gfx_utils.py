import pygame
from utils.colors import *

def draw_pointer(surface, x, y):
    pygame.draw.circle(surface, BLUE, (int(x), int(y)), 4, 0)
