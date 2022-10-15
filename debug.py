import pygame
import core as cor


pygame.init()


def mark(surface, x, y, color=(50, 200, 50), r=5):
    if cor.DEBUG:
        pygame.draw.circle(surface, color, (x, y), radius=r)

