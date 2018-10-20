import pygame
from utils.colors import *

def draw_pointer(surface, x, y):
    pygame.draw.circle(surface, BLUE, (int(x), int(y)), 4, 0)


def draw_line(surface, x, y, dx, dy, color):
    pygame.draw.line(surface, color, (int(x), int(y)), (int(dx), int(dy)), 4)

def draw_border(surface, a,b,c,d):
    padding = 4
    pygame.draw.rect(surface, BLACK, (int(a - padding), int(b - padding), int(c + 2*padding), int(d + 2*padding)), 2)

def clear(surface):
    surface.fill(WHITE)
