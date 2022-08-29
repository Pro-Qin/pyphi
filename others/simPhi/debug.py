import pygame
import core
import math


pygame.init()


def mark(surface, x, y, color=(50, 200, 50), r=5):
    if core.DEBUG:
        pygame.draw.circle(surface, color, (x, y), radius=r)


def show_angle(surface, x, y, angle, length=100, width=5, color=(50, 200, 50)):
    if core.DEBUG:
        pygame.draw.line(surface, color,
                         [x, y],
                         [x + length * math.cos(math.radians(angle)), y - length*math.sin(math.radians(angle))],
                         width=width)
