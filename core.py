import math
import pygame
import typing as T
import os
from PIL import Image
import os
import cv2
import time
import matplotlib.pyplot as plt


if not os.path.exists("./cache"):
    os.makedirs("./cache")


pygame.init()
# pygame.mixer.init()


import numpy as np
import cv2
 

def scale_pg(fji,bili):
    '''按比例缩放
    :: fji = pygame.Surface
    :: bili = int'''
    bili = int(bili)
    def1_output = pygame.transform.scale(fji, (fji.get_size()[0]/100*bili, fji.get_size()[1]/100*bili)) # 按比例缩放
    return def1_output

def scale_wpg(fji,width):
    '''按目标智能缩放,要求宽度
    :: fji = pygame.Surface
    :: width = int'''
    width = int(width)
    w = fji.get_size()[0]
    h = fji.get_size()[1]
    sakdj = width / w * 100
    def1_output = pygame.transform.scale(fji, (fji.get_size()[0]/100*sakdj, fji.get_size()[1]/100*sakdj)) # 按比例缩放
    return def1_output

def cutimage(image:pygame.Surface,imagepath:str,size,endpath,sizeer:tuple):
    # image = pygame.image.load(imagepath).convert_alpha()
    # image = scale_wpg(image,417)
    w,h = image.get_rect().size
    ew,eh=sizeer
    pas = ew/w*h #ew/w 求比例 *h应用在高上
    # 读取图像
    img = cv2.imread(imagepath)
    # 坐标点points
    # pts = np.array([[size,0+pas],[w,0+pas],[w-size,h-pas],[0,h-pas]])
    pts = np.array([[size,pas],[w,pas],[w-size,h-pas],[0,h-pas]])
    pts = np.array([pts])
    # 和原始图像一样大小的0矩阵，作为mask
    mask = np.zeros(img.shape[:2], np.uint8)
    # 在mask上将多边形区域填充为白色
    cv2.polylines(mask, pts, True, (0,0,0))    # 描绘边缘
    cv2.fillPoly(mask, pts, 255)    # 填充
    # 逐位与，得到裁剪后图像，此时是黑色背景
    dst = cv2.bitwise_and(img, img, mask=mask)
    # 添加白色背景
    bg = np.ones_like(img, np.uint8) * 255
    cv2.bitwise_not(bg, bg, mask=mask)  # bg的多边形区域为0，背景区域为255
    dst_white = bg + dst
    # cv2.imwrite("cache/Introduction_.jpg", dst)

    tmp = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)
    _, alpha = cv2.threshold(tmp, 0, 255, cv2.THRESH_BINARY)
    b, g, r = cv2.split(dst)
    rgba = [b, g, r, alpha]
    dst = cv2.merge(rgba, 4)

    # 注意保存成png格式！！！jpg的话还是黑色背景(255)
    cv2.imwrite(endpath, dst)

    # endimage = pygame.image.load(endpath).convert_alpha()
    # endimage = pygame.transform.scale(endimage, sizeer)
    # return endimage

def cutimage_rect(imagepath,size:tuple,endpath):
    ew,eh=size
    image = pygame.image.load(imagepath).convert_alpha()
    image = scale_wpg(image,ew)
    w,h = image.get_rect().size

    # pas = ew/w*h #ew/w 求比例 *h应用在高上
    # 读取图像
    img = cv2.imread(imagepath)
    # img.size
    # 坐标点points
    # pts = np.array([[size,0+pas],[w,0+pas],[w-size,h-pas],[0,h-pas]])
    pts = np.array([[(w-ew)/2,(h-eh)/2],[(w-ew)/2,(h-eh)/2+eh],[(w-ew)/2+ew,(h-eh)/2+eh],[(w-ew)/2+ew,(h-eh)/2]])
    pts = np.int32([pts])# pts = np.array([pts])
    # 和原始图像一样大小的0矩阵，作为mask
    mask = np.zeros(img.shape[:2], np.uint8)
    # 在mask上将多边形区域填充为白色
    cv2.polylines(mask, np.int32(pts), True, (0,0,0))    # 描绘边缘
    cv2.fillPoly(mask, np.int32(pts), 255)    # 填充
    # 逐位与，得到裁剪后图像，此时是黑色背景
    dst = cv2.bitwise_and(img, img, mask=mask)
    # 添加白色背景
    bg = np.ones_like(img, np.uint8) * 255
    cv2.bitwise_not(bg, bg, mask=mask)  # bg的多边形区域为0，背景区域为255
    dst_white = bg + dst
    # cv2.imwrite("cache/Introduction_.jpg", dst

    tmp = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)
    _, alpha = cv2.threshold(tmp, 0, 255, cv2.THRESH_BINARY)
    b, g, r = cv2.split(dst)
    rgba = [b, g, r, alpha]
    dst = cv2.merge(rgba, 4)

    cv2.imwrite(endpath, dst)
    return ((w-ew)/2,(h-eh)/2)

def getnum_str(strdata):
    a = ''
    for i in strdata:    # 将字符串进行遍历
        if str.isdigit(i):    # 判断i是否为数字，如果“是”返回True，“不是”返回False
            a += i   # 如果i是数字格式，将i以字符串格式加到a上
        else:
            pass  # 如果i不是数字格式则省略
    return int(a)



class Eval:
    GOOD = '0'
    PERFECT = '1'

    def __init__(self):
        self.goods = [
            pygame.image.load(f"resources/texture/img-{i}_good.png") for i in range(1, 31)
        ]
        self.perfects = [
            pygame.image.load(f"resources/texture/img-{i}_perfect.png") for i in range(1, 31)
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
            Texture.Tap: pygame.image.load("resources/texture/Tap2.png"),#resources/texture/Tap2.png
            Texture.TapHL: pygame.image.load("resources/texture/Tap2HL.png"),
            Texture.Drag: pygame.image.load("resources/texture/Drag2.png"),
            Texture.DragHL: pygame.image.load("resources/texture/DragHL.png"),
            Texture.Flick: pygame.image.load("resources/texture/Flick2.png"),
            Texture.FlickHL: pygame.image.load("resources/texture/Flick2HL.png"),
            Texture.Hold: pygame.image.load("resources/texture/Hold2.png"),
            Texture.Line: pygame.image.load("resources/texture/line.png"),
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
WIDTH = int(1920 / 2)
HEIGHT = int(1080 / 2)

NOTE_WIDTH = 100
NOTE_HEIGHT = 12
NOTE_R = (NOTE_HEIGHT ** 2 + NOTE_WIDTH ** 2) ** 0.5 / 2
NOTE_THETA = math.degrees(math.atan(NOTE_HEIGHT/NOTE_WIDTH))

BAR_WIDTH = 20

TITLE = 'Phigros for Python Max'

pygame.mixer.init()

TAP_SOUND = pygame.mixer.Sound("resources/audio/tap.wav")
DRAG_SOUND = pygame.mixer.Sound("resources/audio/drag.wav")
FLICK_SOUND = pygame.mixer.Sound("resources/audio/flick.wav")


NOTE_X_SCALE = 220 / 300 * WIDTH / 1000
LINE_X_SCALE = 0.8 * WIDTH / 1000
LINE_Y_SCALE = -38 / 50 * HEIGHT / 700
SPEED_SCALE = 35

NOTE_NUM = 0

DURATION = 0
NAME = ''
ARTIST = ''
CHART = ''
LEVEL = ''
# global IMAGE
IMAGE: os.PathLike
SONG: os.PathLike
BPMLIST: dict
BeatObject: object  # 提供秒转拍服务

OFFSET = 0

ENDLIST:dict = {}

judge_line_list = []

if __name__ == '__main__':
    print(Texture[Texture.EvalImg][Eval.GOOD, 25])
