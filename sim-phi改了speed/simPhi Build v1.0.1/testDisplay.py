import core
import pygame
import sys
import time

import data
import element

pygame.init()

screen = pygame.display.set_mode((core.WIDTH, core.HEIGHT))

beat = 0
start = time.time()
clock = pygame.time.Clock()
data.load_beatmap("exampleBeatmap.xml")

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit(0)

    if beat > 150:
        continue
    screen.fill((55, 55, 55))

    for jl in core.judge_line_list:
        jl.upgrade(screen, beat)

    pygame.display.flip()
    clock.tick(240)
    # print(clock.get_fps())
    beat = (time.time() - start) * 2
