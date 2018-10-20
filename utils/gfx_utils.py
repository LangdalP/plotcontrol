import pygame
from utils.colors import *

def draw_pointer(surface, x, y):
    pygame.draw.circle(surface, BLUE, (int(x), int(y)), 4, 0)


def draw_line(surface, x, y, dx, dy, color):
    pygame.draw.line(surface, color, (int(x), int(y)), (int(dx), int(dy)), 4)

def draw_border(surface, a,b,w,h):
    padding = 4
    pygame.draw.rect(surface, BLACK, (int(a - padding), int(b - padding), int(w + 2*padding), int(h + 2*padding)), 2)

def render_text(surface, text):
    # Lets assume 1920 x 1080
    textRect = text.get_rect()
    textRect.centerx = 960
    textRect.centery = 120

    # Draw background
    pygame.draw.rect(surface, WHITE, (0, 0, 1920, 280))
    # Draw text
    surface.blit(text, textRect)

def clear(surface):
    surface.fill(WHITE)
