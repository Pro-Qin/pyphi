import core
import pygame
import sys
import time
import data
import element
import math
import debug


pygame.init()

JSON_PATH = "resources/61895176/61895176.json"
# JSON_PATH = "resources/56769032/56769032.json"
# JSON_PATH = "resources/81907165/81907165.json"
pygame.mixer.init()
pygame.mixer.music.load("resources/61895176/61895176.mp3")

data.load_rpe(JSON_PATH)
evalPainter = element.EvalPainter()

screen = pygame.display.set_mode((core.WIDTH, core.HEIGHT))
surface = pygame.Surface((core.WIDTH, core.HEIGHT), pygame.SRCALPHA)

skip = 10
beat = core.BeatObject.get_value(skip/60)


def draw(beat):
    full_length = 2000
    at = 10
    end = 20
    duration = end - at
    above = True
    note_y = 100
    x = 0
    jx = 400
    jy = 300
    ja = 30
    alpha = 255
    
    if beat < at:
        length = full_length
        _y = note_y * (
            1 if above else -1
        )
    else:
        length = full_length * (end - beat) / duration
        _y = 0

    r = (x ** 2 + _y ** 2) ** 0.5
    if x > 0:
        angle = ja + math.degrees(math.atan(_y / x))
    elif x < 0:
        angle = ja + math.degrees(math.atan(_y / x)) + 180
    else:
        angle = ja + (90 if _y >= 0 else - 90)
    x = r * math.cos(math.radians(angle)) + jx
    y = -r * math.sin(math.radians(angle)) + jy

    x_in_surface = x
    y_in_surface = y

    if y_in_surface < 0 or y_in_surface > core.HEIGHT or \
            x_in_surface < 0 or x_in_surface > core.WIDTH:
        debug.mark(surface, x, y, color=(200, 50, 50), r=10)
        return 0

    length = -length if above else length
    _angle1 = math.radians(ja + math.degrees(math.atan(length / core.NOTE_WIDTH * 2)))
    _angle2 = math.radians(180 + ja - math.degrees(math.atan(length / core.NOTE_WIDTH * 2)))
    r = (length ** 2 + (core.NOTE_WIDTH / 2) ** 2) ** 0.5

    pygame.draw.polygon(surface, (10, 195, 255, alpha), [
        (x + core.NOTE_WIDTH / 2 * math.cos(math.radians(ja)),
         y - core.NOTE_WIDTH / 2 * math.sin(math.radians(ja))),
        (x - core.NOTE_WIDTH / 2 * math.cos(math.radians(ja)),
         y + core.NOTE_WIDTH / 2 * math.sin(math.radians(ja))),

        (x - r * math.cos(_angle1),
         y + r * math.sin(_angle1)),
        (x - r * math.cos(_angle2),
         y + r * math.sin(_angle2)),

    ])
    #
    # debug.mark(surface, x + r * math.cos(_angle2), y + r * math.sin(_angle), (0, 255, 255))
    #
    # _angle = math.radians(180 + ja - math.degrees(math.atan(length / core.NOTE_WIDTH * 2)))
    # debug.mark(surface, x + r * math.cos(_angle), y + r * math.sin(_angle), (255, 255, 0))

    debug.mark(surface, x, y, color=(200, 50, 50), r=10)


clock = pygame.time.Clock()
pygame.mixer.music.play(start=skip)
start = time.time()

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit(0)

    screen.fill((55, 55, 55))
    surface.fill((0, 0, 0, 0))

    draw(12)

    debug.mark(surface, 400, 300, )

    pygame.draw.line(
        surface, (255, 0, 0), (400, 300), (500, 243)
    )
    pygame.draw.line(
        surface, (255, 0, 0), (400, 300), (500, 357)
    )
    screen.blit(surface, (0, 0))
    pygame.display.flip()
    clock.tick(240)
