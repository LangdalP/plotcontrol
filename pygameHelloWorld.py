import pygame, sys
from pygame.locals import *
from pygame.joystick import *

# set up pygame
pygame.init()

# set up the window
windowSurface = pygame.display.set_mode((500, 400), 0, 32)
pygame.display.set_caption('Hello world!')

# set up the colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# set up fonts
basicFont = pygame.font.SysFont(None, 48)

# set up the text
text = basicFont.render('Hello world!', True, WHITE, BLUE)
textRect = text.get_rect()
textRect.centerx = windowSurface.get_rect().centerx
textRect.centery = windowSurface.get_rect().centery

# draw the white background onto the surface
windowSurface.fill(WHITE)

# draw a green polygon onto the surface
pygame.draw.polygon(windowSurface, GREEN, ((146, 0), (291, 106), (236, 277), (56, 277), (0, 106)))

# draw some blue lines onto the surface
pygame.draw.line(windowSurface, BLUE, (60, 60), (120, 60), 4)
pygame.draw.line(windowSurface, BLUE, (120, 60), (60, 120))
pygame.draw.line(windowSurface, BLUE, (60, 120), (120, 120), 4)

# draw a blue circle onto the surface
pygame.draw.circle(windowSurface, BLUE, (300, 50), 20, 0)

# draw a red ellipse onto the surface
pygame.draw.ellipse(windowSurface, RED, (300, 250, 40, 80), 1)

# draw the text's background rectangle onto the surface
pygame.draw.rect(windowSurface, RED, (textRect.left - 20, textRect.top - 20, textRect.width + 40, textRect.height + 40))

# get a pixel array of the surface
pixArray = pygame.PixelArray(windowSurface)
pixArray[480][380] = BLACK
del pixArray

# draw the text onto the surface
windowSurface.blit(text, textRect)

# draw the window onto the screen
pygame.display.update()

####################################
# pygame.joystick er ein del av pygame core, og blir automatisk initialisert av pygame.init().
# Når ein joystick er initialized vil den generere events som kjem i pygame si event-kø.
# Den kan lage følgande events: JOYAXISMOTION JOYBALLMOTION JOYBUTTONDOWN JOYBUTTONUP JOYHATMOTION
# Meir dokumentasjon: https://www.pygame.org/docs/ref/joystick.html#pygame.joystick.get_init

num_joysticks = pygame.joystick.get_count()
print(f'Fant {num_joysticks} joysticks')

my_joystick = None
num_axes = None
if (num_joysticks > 0):
    my_joystick = pygame.joystick.Joystick(0) # Vi skal bruke den "nullte" joysticken
    my_joystick.init()
    num_axes = my_joystick.get_numaxes()
####################################

# run the game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.JOYAXISMOTION:
            print("Joystick axis motion.")
            for i in range(num_axes):
                print(f'Akse {i}: {my_joystick.get_axis(i)}')
        if event.type == pygame.JOYBUTTONDOWN:
            print("Joystick button pressed.")
        if event.type == pygame.JOYBUTTONUP:
            print("Joystick button released.")

        if event.type == QUIT:
            pygame.quit()

            sys.exit()
