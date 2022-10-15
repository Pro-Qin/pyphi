# import core
# import pygame
# import sys
# import time
# import math
# import debug
#
# pygame.init()
#
#
# screen = pygame.display.set_mode((1000, 700), )
#
# WIDTH = 1000
# HEIGHT = 700
# LINE_LENGTH = 2000
# UP = 0
# DOWN = 1
# LEFT = 2
# RIGHT = 3
#
# angle = 0
# x = -300
# y = 50
# alpha = 255
# beat = 0
#
# meta_line_texture = pygame.image.load("./resources/texture/metaLine.png")
#
# # 以画面左上方为原点，建立平面直角坐标系
#
#
#
#
#
# start = time.time()
# clock = pygame.time.Clock()
# line_surface = pygame.surface.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
#
# while 1:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             sys.exit(0)
#
#     screen.fill((0, 200, 200))
#     line_surface.fill((0, 0, 0, 0))
#
#     if points:
#         pygame.draw.line(line_surface, (255, 255, 255, 100), points[0], points[1], width=5)
#
#     screen.blit(line_surface, (0, 0))
#
#     pygame.display.flip()
#     clock.tick(24000)
#     angle = (time.time() - start) * 30 - 60
#     print(clock.get_fps())

