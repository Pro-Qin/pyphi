import pygame
import core


pygame.init()


def mark(surface, x, y, color=(50, 200, 50), r=5):
    if core.DEBUG:
        pygame.draw.circle(surface, color, (x, y), radius=r)

