# exo 1.x版本字体
# Saira 2.x版本字体


import pygame  # 游戏引擎
from PIL import Image  # 图片处理
import zipfile  # 解压文件
import readfile  # 读取文件
import sys  # 退出操作
import os  # 文件操作
# import cv2              #图像操作
import time  # 时间操作
from tkinter.messagebox import showinfo, showwarning, showerror, askyesno
# 消息框
import random  # 随机
from pydub import AudioSegment
# 音频格式转化
import pygame.freetype  # 文本
import eyed3  # 音频文件处理
import welcome as w
from readchart import *

os.system('clear')  # 清屏
# -------------------------------------------

# 当前问题：
# 2.不能读取铺面

# -------------------------------------------
window_x = 1920/2
window_y = 1080/2
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FPS = 60
combo = 0
maxcombo = 0
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()
nummark = "0000000"

# -------------------------------------------
w.welcome()  # 欢迎界面
Gamename = w.choose()  # 选择界面
w.loading()
info_data = readfile.lookfile(Gamename)
data = chart.init(Gamename)

# --------------------------------------------


# 使用pygame之前必须初始化
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.mixer.init()
pygame.init()


#clock = pygame.time.Clock()

screen = pygame.display.set_mode((window_x, window_y))  # 设置主屏窗口
screen.fill((30, 30, 30))  # 填充主窗口的背景颜色，参数值RGB（颜色元组）
keep_going = True  # 循环标志
pygame.display.set_caption('Phigros for Python')  # 设置窗口标题
# -----------------------------------------------
blackpic = pygame.image.load("src/black.png").convert()
blackpic.set_alpha(1)


def darken_screen(qwok):
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


def get_voice_time_secs(file_name):
    """
    获取音频文件时长
    :param file_data 文件的二进制流
    :param file_name 文件名
    """
    # 先把文件保存在本地，我试过很多包，都需要先把文件保存在本地后才能获取音频长度，初步猜测是因为这些包的代码读取的是文件本地的信息
    # with open(file_name, 'w+') as f:
    #    f.write(file_data)
    # 加载本地文件
    voice_file = eyed3.load(file_name)
    # 获取音频时长
    secs = int(voice_file.info.time_secs)
    return secs

# -----------------------------------------------


try:  # 检测父文件
    JudgeLine = pygame.image.load("src/JudgeLine.png").convert_alpha()  # 判定线
    ProgressBar = pygame.image.load(
        "src/ProgressBar.png").convert_alpha()  # 进度条
    SongsNameBar = pygame.image.load(
        "src/SongsNameBar.png").convert_alpha()  # 歌曲名条
    Pause = pygame.image.load("src/Pause.png").convert_alpha()  # 暂停
    clickRaw = pygame.image.load("src/clickRaw.png").convert_alpha()  # 点击特效
    Tap = pygame.image.load("src/Tap.png").convert_alpha()  # Tap
    Tap2 = pygame.image.load("src/Tap2.png").convert_alpha()  # Tap-BAD
    TapHL = pygame.image.load("src/TapHL.png").convert_alpha()  # Tap高亮
    Drag = pygame.image.load("src/Drag.png").convert_alpha()  # Drag
    DragHL = pygame.image.load("src/DragHL.png").convert_alpha()  # Drag高亮
    HoldHead = pygame.image.load("src/HoldHead.png").convert_alpha()  # Hold头部
    HoldHeadHL = pygame.image.load(
        "src/HoldHeadHL.png").convert_alpha()  # Hold头部高亮
    Hold = pygame.image.load("src/Hold.png").convert_alpha()  # Hold身子
    HoldHL = pygame.image.load("src/HoldHL.png").convert_alpha()  # Hold身子高亮
    HoldEnd = pygame.image.load("src/HoldEnd.png").convert_alpha()  # Hold尾部
    Flick = pygame.image.load("src/Flick.png").convert_alpha()  # Flick
    FlickHL = pygame.image.load("src/FlickHL.png").convert_alpha()  # Flick高亮
    Pic_LevelOver1 = pygame.image.load(
        "src/LevelOver1.png").convert_alpha()  # LevelOver1中间成果条
    Pic_LevelOver3 = pygame.image.load(
        "src/LevelOver3.png").convert_alpha()  # LevelOver3等级背景
    Pic_LevelOver4 = pygame.image.load(
        "src/LevelOver4.png").convert_alpha()  # LevelOver4名字背景
    Pic_LevelOver5 = pygame.image.load(
        "src/LevelOver5.png").convert_alpha()  # LevelOver5名字左竖
    Rank = pygame.image.load("src/Rank.png").convert_alpha()  # 等级图片
    ContinueButton = pygame.image.load(
        "src/continue.png").convert_alpha()  # 继续
    RestartButton = pygame.image.load("src/restart.png").convert_alpha()  # 重启
    StopButton = pygame.image.load("src/stop.png").convert_alpha()  # 退出
    # -------------------------------------------------------------------------------------
    mute = pygame.mixer.music.load("src/mute.ogg")  # 静音
    HitSong0 = pygame.mixer.music.load("src/HitSong0.ogg")  # 打击音效1-Tap
    HitSong1 = pygame.mixer.music.load("src/HitSong1.ogg")  # 打击音效2-Drag
    HitSong2 = pygame.mixer.music.load("src/HitSong2.ogg")  # 打击音效3-Flick
    Music_LevelOver = pygame.mixer.music.load("src/LevelOver3_v2.ogg")  # 结束音效
except FileNotFoundError:
    showerror('读取出错：未发现父文件')


#background_image = cv2.GaussianBlur(src, (15, 15), 0)
# im = Image.open(info_data["picture"]).point(lambda p = p * 0.5)
image_surface = pygame.image.load(info_data["picture"]).convert()  # 加载背景
image_surface.scroll(0, 0)
image_surface = pygame.transform.scale(image_surface, (window_x, window_y))


pygame.mixer.music.load(info_data["music"])  # 加载歌曲
songlength = get_voice_time_secs(info_data["music"])
# songlength=1
# pygame.mixer.music.play() # 播放

datanum = 0
with open(info_data["chart"]) as f:  # 读取铺面
    line = f.readline()
    data.append(line)
    datanum += 1
f.close()

# if info_data['音乐'][-4:] == 'ogg':#检测音乐格式
#    print('读取音乐文件格式正确!')
# else:
#    print('读取出错：发现音乐类型非.ogg')

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

SongsNameBar = pygame.transform.scale(SongsNameBar, (4, 21))  # 歌曲名条调整大小
ProgressBar = pygame.transform.scale(ProgressBar, (window_x+5, 5))  # 进度条儿调整大小
Pause = pygame.transform.scale(Pause, (20, 20))  # 暂停按钮调整大小
blackpic = pygame.transform.scale(blackpic, (window_x, window_y))
JudgeLine = pygame.transform.scale(JudgeLine, (window_y*2.5, 5))

ProgressX = -window_x+10  # 进度条X坐标(定位坐标在图像左上角，完成则为x0)(加载出图像需要时间)
ProgressMoveX = songlength / window_x  # 进度条移动速度
# print(info_data,'\n',data)
ContinueButton.set_alpha(100)
RestartButton.set_alpha(100)
StopButton.set_alpha(100)
# -----------------------------------------------
# 谱面识别！


# -----------------------------------------------
# 如果没有下列主循环代码，运行结果会一闪而过
darken_screen(150)
time_begin = int(time.time())
songlengthstr = time.strftime("%M:%S", time.localtime(songlength))
while 1:
    0/0
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
                if pos[0] >= 20 and pos[0] <= 20+20 and event.pos[1] >= 21 and event.pos[1] <= 21+20:
                    exitnow = int(time.time())
                    if pos[0] >= 20 and pos[0] <= 20+20 and event.pos[1] >= 21 and event.pos[1] <= 21+20 and int(time.time())-exitnow <= 1:
                        sys.exit()

    if pygame.mixer.music.get_busy():  # 播放BGM
        # 获取当前播放的时间
        current = pygame.mixer.music.get_pos() / 1000  # 毫秒
        current %= songlength  # 如果循环播放，需要处理
        rate = current / songlength
        # 进度条X坐标(定位坐标在图像左上角，完成则为x0)(加载出图像需要时间)
        ProgressX = -window_x - 5 + int(rate * window_x)
        less = now-time_begin
    else:
        less = str(less)
        less = songlengthstr

    # 更新屏幕内容
    screen.blit(Tap, data["LineList"][0][pos])
    screen.blit(image_surface, (0, 0))  # 背景
    screen.blit(blackpic, (0, 0))  # 黑色掩盖
    screen.blit(Pause, (20, 21))  # 暂停按钮
    screen.blit(SongsNameBar, (20, 500))  # 歌曲名条
    screen.blit(ProgressBar, (ProgressX, 0))  # 进度条儿
    # screen.bilt(ContinueButton,(window_x/3-12,window_y/4))                                      #继续
    # screen.bilt(RestartButton,(window_x/3*2-12*2,window_y/4*2))                                 #重启
    # screen.bilt(StopButton,(window_x/2*3-12*3,window_y/4*3))                                    #退出
    SongsName = f2.render_to(
        screen, [30, 503], info_data['other'][0], fgcolor=WHITE, size=21)  # 歌曲名
    SongsLevel = f1.render_to(
        screen, [865, 507], info_data['other'][1], fgcolor=WHITE, size=18)  # 歌曲等级
    mark = f1.render_to(screen, [809, 25], str(
        nummark), fgcolor=WHITE, size=28)  # 分数
    # ----------------------------------------------------调试显示区
    ts_mousexy = f1.render_to(screen, [80, 5], 'MousePos:{}'.format(
        pygame.mouse.get_pos()), fgcolor=WHITE, size=12)
    ts_music = f1.render_to(screen, [220, 5], 'Music:{}'.format(
        pygame.mixer.music.get_busy()), fgcolor=WHITE, size=12)
    ts_numnote = f1.render_to(screen, [320, 5], 'NumOfNote:{}'.format(
        numOfNotes), fgcolor=WHITE, size=12)
    # ----------------------------------------------------调试显示区
    try:
        otime = f1.render_to(screen, [0, 5], '{}/{}'.format(time.strftime(
            "%M:%S", time.localtime(less)), songlengthstr), fgcolor=WHITE, size=12)
    except TypeError:
        otime = f1.render_to(screen, [
                             0, 5], '{}/{}'.format(songlengthstr, songlengthstr), fgcolor=WHITE, size=12)

    # ----------------------------------
    screen.blit(JudgeLine, (0, window_y/2))
    # ----------------------------------

    mouse.update()  # 更新鼠标位置
    pygame.display.update()  # 更新屏幕
