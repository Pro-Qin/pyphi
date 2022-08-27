import math
import pygame
import typing as T
import os


if not os.path.exists("./cache"):
    os.makedirs("./cache")


pygame.init()
pygame.mixer.init()


class Eval:
    GOOD = '0'
    PERFECT = '1'

    def __init__(self):
        self.goods = [
            pygame.image.load(f"./resources/texture/img-{i}_good.png") for i in range(1, 31)
        ]
        self.perfects = [
            pygame.image.load(f"./resources/texture/img-{i}_perfect.png") for i in range(1, 31)
        ]

        for index in range(len(self.goods)):
            self.goods[index] = pygame.transform.smoothscale(
                self.goods[index], (self.goods[index].get_width() / 1.5, self.goods[index].get_height() / 1.5)
            )

        for index in range(len(self.perfects)):
            self.perfects[index] = pygame.transform.smoothscale(
                self.perfects[index], (self.perfects[index].get_width() / 1.5, self.perfects[index].get_height() / 1.5)
            )

    def __getitem__(self, item: T.Tuple[str, int]):
        """
        获取反馈图像
        :param item: (TYPE, INDEX)
        :return: EvalImg Surface Object
        """

        return (self.goods if item[0] == Eval.GOOD else self.perfects)[item[1]]


class Texture:
    Tap = 0
    TapHL = 1
    Drag = 2
    DragHL = 3
    Flick = 4
    FlickHL = 5
    Hold = 6
    Line = 7
    EvalImg = 8

    def __init__(self):
        self.id2texture = {
            Texture.Tap: pygame.image.load("./resources/texture/Tap2.png"),
            Texture.TapHL: pygame.image.load("./resources/texture/Tap2HL.png"),
            Texture.Drag: pygame.image.load("./resources/texture/Drag2.png"),
            Texture.DragHL: pygame.image.load("./resources/texture/DragHL.png"),
            Texture.Flick: pygame.image.load("./resources/texture/Flick2.png"),
            Texture.FlickHL: pygame.image.load("./resources/texture/Flick2HL.png"),
            Texture.Hold: pygame.image.load("./resources/texture/Hold2.png"),
            Texture.Line: pygame.image.load("./resources/texture/line.png"),
            Texture.EvalImg: Eval()
        }

        for key in self.id2texture:
            if key in [Texture.EvalImg, Texture.Line, Texture.Hold]:
                continue

            self.id2texture[key] = pygame.transform.smoothscale(
                self.id2texture[key], (self.id2texture[key].get_width() / 8, self.id2texture[key].get_height()/8)
            )

    def __getitem__(self, item: int):
        """
        获取反馈图像
        :param item: (TYPE, INDEX)
        :return: EvalImg Surface Object
        """

        return self.id2texture[item]


Texture = Texture()

DEBUG = False
NO_CACHE = False
ENABLE_SOUND = True

DEBUG_K = 1
DEBUG_N = 1

LINE_LENGTH = 4000
WIDTH = 854
HEIGHT = 481

NOTE_WIDTH = 110
NOTE_HEIGHT = 12
NOTE_R = (NOTE_HEIGHT ** 2 + NOTE_WIDTH ** 2) ** 0.5 / 2
NOTE_THETA = math.degrees(math.atan(NOTE_HEIGHT/NOTE_WIDTH))

BAR_WIDTH = 22

TAP_SOUND = pygame.mixer.Sound("./resources/audio/tap.wav")
DRAG_SOUND = pygame.mixer.Sound("./resources/audio/drag.wav")
FLICK_SOUND = pygame.mixer.Sound("./resources/audio/flick.wav")

NOTE_X_SCALE = 220 / 300 * WIDTH / 1000
LINE_X_SCALE = 0.8 * WIDTH / 1000
LINE_Y_SCALE = -38 / 50 * HEIGHT / 700
SPEED_SCALE = 25

NOTE_NUM = 0

DURATION = 0
NAME = ''
ARTIST = ''
CHART = ''
LEVEL = ''
IMAGE: os.PathLike
SONG: os.PathLike

BeatObject: object  # 提供秒转拍服务

OFFSET = 0

PREPARE_DURATION = 3
END_DURATION_1 = 3
END_DURATION_2 = 0.8

judge_line_list = []

if __name__ == '__main__':
    print(Texture[Texture.EvalImg][Eval.GOOD, 25])
