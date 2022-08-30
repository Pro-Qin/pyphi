# exo 1.x版本字体
# Saira 2.x版本字体


import os
import sys
# import cv2
import time
from tkinter.messagebox import showerror
import pygame
import pygame.freetype
from PIL import Image, ImageFilter, ImageEnhance
import tinytag
from pydub import *

import easing                       # 缓动函数
import element
import core
import readfile                     # 读取文件
import welcome as w                 # 欢迎界面
import easing                       # 缓动函数
import helper                       # def函数封装
import readchart                    # 读取谱面


os.system('clear')  # 清屏
# -------------------------------------------

# 当前问题：
# 2.不能读取铺面

# -------------------------------------------
WINDOW_X = 1920 / 2
WINDOW_Y = 1080 / 2
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FPS = 60
combo = 0
maxcombo = 0
data = []  # 初始化铺面数据
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()
nummark = "0000000"

# -------------------------------------------
w.welcome()  # 欢迎界面
gamename = w.choose()  # 选择界面
w.loading()
info_data = readfile.lookfile(gamename)
# --------------------------------------------


# 使用pygame之前必须初始化
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.mixer.init()
pygame.init()

# clock = pygame.time.Clock()

screen = pygame.display.set_mode((WINDOW_X, WINDOW_Y))  # 设置主屏窗口
screen.fill((30, 30, 30))  # 填充主窗口的背景颜色，参数值RGB（颜色元组）
keep_going = True  # 循环标志
pygame.display.set_caption('Phigros for Python')  # 设置窗口标题
# -----------------------------------------------
blackpic = pygame.image.load("src/black.png").convert()
blackpic.set_alpha(1)


def darken_screen(qwok):
    '''
    设置背景暗度
    '''
    blackpic.set_alpha(qwok)


def trans_music(name, filepath, hz):
    song = AudioSegment.from_mp3(filepath)
    song.export(name+str(hz), format=str(hz))

# 鼠标类


class Mouse(pygame.sprite.Sprite):
    def __init__(self):
        self.image = pygame.Surface((2, 2))
        self.image.fill('#D655C7')
        self.rect = self.image.get_rect()
        self.rect.center = pygame.mouse.get_pos()  # 初始位置到鼠标指针

    def update(self):
        self.rect.center = pygame.mouse.get_pos()  # 移到鼠标指针位置
        screen.blit(self.image, self.rect)


# 创建鼠标精灵
mouse = Mouse()

# -----------------------------------------------

try:  # 检测父文件
    judgeLine = pygame.image.load("src/JudgeLine.png").convert_alpha()  # 判定线
    progressBar = pygame.image.load(
        "src/ProgressBar.png").convert_alpha()  # 进度条
    songsNameBar = pygame.image.load(
        "src/SongsNameBar.png").convert_alpha()  # 歌曲名条
    pause = pygame.image.load("src/Pause.png").convert_alpha()  # 暂停
    clickRaw = pygame.image.load("src/clickRaw.png").convert_alpha()  # 点击特效
    tap = pygame.image.load("src/Tap.png").convert_alpha()  # Tap
    tap2 = pygame.image.load("src/Tap2.png").convert_alpha()  # Tap-BAD
    tapHL = pygame.image.load("src/TapHL.png").convert_alpha()  # Tap高亮
    drag = pygame.image.load("src/Drag.png").convert_alpha()  # Drag
    dragHL = pygame.image.load("src/DragHL.png").convert_alpha()  # Drag高亮
    holdHead = pygame.image.load("src/HoldHead.png").convert_alpha()  # Hold头部
    holdHeadHL = pygame.image.load(
        "src/HoldHeadHL.png").convert_alpha()  # Hold头部高亮
    hold = pygame.image.load("src/Hold.png").convert_alpha()  # Hold身子
    holdHL = pygame.image.load("src/HoldHL.png").convert_alpha()  # Hold身子高亮
    holdEnd = pygame.image.load("src/HoldEnd.png").convert_alpha()  # Hold尾部
    flick = pygame.image.load("src/Flick.png").convert_alpha()  # Flick
    flickHL = pygame.image.load("src/FlickHL.png").convert_alpha()  # Flick高亮
    pic_LevelOver1 = pygame.image.load(
        "src/LevelOver1.png").convert_alpha()  # LevelOver1中间成果条
    pic_LevelOver3 = pygame.image.load(
        "src/LevelOver3.png").convert_alpha()  # LevelOver3等级背景
    pic_LevelOver4 = pygame.image.load(
        "src/LevelOver4.png").convert_alpha()  # LevelOver4名字背景
    pic_LevelOver5 = pygame.image.load(
        "src/LevelOver5.png").convert_alpha()  # LevelOver5名字左竖
    rank = pygame.image.load("src/Rank.png").convert_alpha()  # 等级图片
    continueButton = pygame.image.load(
        "src/continue.png").convert_alpha()  # 继续
    restartButton = pygame.image.load("src/restart.png").convert_alpha()  # 重启
    stopButton = pygame.image.load("src/stop.png").convert_alpha()  # 退出
    # -------------------------------------------------------------------------------------
    mute = pygame.mixer.Sound("src/mute.ogg")
    hitSong0 = pygame.mixer.Sound("src/HitSong0.ogg")  # 打击音效1-Tap
    hitSong1 = pygame.mixer.Sound("src/HitSong1.ogg")  # 打击音效2-Drag
    hitSong2 = pygame.mixer.Sound("src/HitSong2.ogg")  # 打击音效3-Flick
    music_LevelOver = pygame.mixer.Sound("src/LevelOver3_v2.ogg")  # 结束音效
except FileNotFoundError:
    showerror('读取出错：未发现父文件')

# background_image = cv2.GaussianBlur(src, (15, 15), 0)
# im = Image.open(info_data["picture"]).point(lambda p = p * 0.5)
image_surface = pygame.image.load(info_data["picture"]).convert()  # 加载背景
image_surface.scroll(0, 0)
image_surface = pygame.transform.scale(image_surface, (WINDOW_X, WINDOW_Y))
# 初始化图像


pygame.mixer.music.load(info_data["music"])  # 加载歌曲
songlength = helper.get_voice_time_secs()(info_data["music"])
# songlength=1
# pygame.mixer.music.play() # 播放

datanum = 0
with open(info_data["chart"]) as f:  # 读取铺面
    line = f.readlines()
    data.append(line)
# if info_data['音乐'][-4:] == 'ogg':#检测音乐格式
#    print('读取音乐文件格式正确!')
# else:
#    print('读取出错：发现音乐类型非.ogg')x

# -----------------------------------------------

# darken_screen()
if pygame.mixer.music.get_busy() == False:  # 播放BGM
    pygame.mixer.music.load(info_data["music"])
    pygame.mixer.music.play()
# 引入字体类型
f1 = pygame.freetype.Font(r"src/Exo-Regular.pfb.ttf", 12)
f2 = pygame.freetype.Font(r"src/Saira-Medium.ttf", 12)
font_title = pygame.freetype.Font(r"src/Saira-Medium.ttf", 14)
# f1rect=f1.render_to(screen,[30,500],info_data["名称"],fgcolor=(255,255,255),size=25)

# -----------------------------------------------

songsNameBar = pygame.transform.scale(songsNameBar, (4, 21))  # 歌曲名条调整大小
progressBar = pygame.transform.scale(
    progressBar, (WINDOW_X + 5, 5))  # 进度条儿调整大小
pause = pygame.transform.scale(pause, (20, 20))  # 暂停按钮调整大小
blackpic = pygame.transform.scale(blackpic, (WINDOW_X, WINDOW_Y))
judgeLine = pygame.transform.scale(judgeLine, (WINDOW_Y * 2.5, 5))

progressX = -WINDOW_X + 10  # 进度条X坐标(定位坐标在图像左上角，完成则为x0)(加载出图像需要时间)
progressMoveX = songlength / WINDOW_X  # 进度条移动速度
# print(info_data,'\n',data)
continueButton.set_alpha(100)
restartButton.set_alpha(100)
stopButton.set_alpha(100)
# -----------------------------------------------
readchart.init(gamename)
# -----------------------------------------------

# 如果没有下列主循环代码，运行结果会一闪而过
darken_screen(150)
time_begin = int(time.time())
songlengthstr = time.strftime("%M:%S", time.localtime(songlength))
while 1:

    now = int(time.time())
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # 卸载所有模块
            pygame.quit()
            # 终止程序
            sys.exit()
        if event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            if event.button == 1:
                if 20 <= pos[0] <= 20 + 20 and 21 <= event.pos[1] <= 21 + 20:
                    exitnow = int(time.time())
                    if 20 <= pos[0] <= 20 + 20 and 21 <= event.pos[1] <= 21 + 20 and int(
                            time.time()) - exitnow <= 1:
                        sys.exit()

    if pygame.mixer.music.get_busy():  # 播放BGM
        # 获取当前播放的时间
        current = pygame.mixer.music.get_pos() / 1000  # 毫秒
        current %= songlength  # 如果循环播放，需要处理
        rate = current / songlength
        # 进度条X坐标(定位坐标在图像左上角，完成则为x0)(加载出图像需要时间)
        ProgressX = -WINDOW_X - 5 + int(rate * WINDOW_X)
        less = now - time_begin
    else:
        less = str(less)
        less = songlengthstr

    # 更新屏幕内容

    screen.blit(image_surface, (0, 0))  # 背景
    screen.blit(blackpic, (0, 0))  # 黑色掩盖
    screen.blit(pause, (20, 21))  # 暂停按钮
    screen.blit(songsNameBar, (20, 500))  # 歌曲名条
    screen.blit(progressBar, (progressX, 0))  # 进度条儿
    # screen.bilt(ContinueButton,(WINDOW_X/3-12,WINDOW_Y/4))                                      #继续
    # screen.bilt(RestartButton,(WINDOW_X/3*2-12*2,WINDOW_Y/4*2))                                 #重启
    # screen.bilt(StopButton,(WINDOW_X/2*3-12*3,WINDOW_Y/4*3))                                    #退出
    SongsName = f2.render_to(screen, [30, 503], info_data['other'][0][1:], fgcolor=(
        255, 255, 255), size=21)  # 歌曲名
    SongsLevel = f1.render_to(screen, [865, 507], info_data['other'][1], fgcolor=(
        255, 255, 255), size=18)  # 歌曲等级
    mark = f1.render_to(screen, [809, 25], str(
        nummark), fgcolor=(255, 255, 255), size=28)  # 分数
    try:
        otime = f1.render_to(screen, [0, 5],
                             '{}/{}'.format(time.strftime("%M:%S",
                                            time.localtime(less)), songlengthstr),
                             fgcolor=(255, 255, 255), size=12)
    except TypeError:
        otime = f1.render_to(screen, [0, 5], '{}/{}'.format(songlengthstr, songlengthstr), fgcolor=(255, 255, 255),
                             size=12)

    # ----------------------------------
    screen.blit(judgeLine, (0, WINDOW_Y / 2))
    # ----------------------------------

    mouse.update()  # 更新鼠标位置
    pygame.display.update()  # 更新屏幕
