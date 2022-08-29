# exo 1.x版本字体
# Saira 2.x版本字体


import os
import sys
# import cv2
import time
from tkinter.messagebox import showerror
import pygame
import pygame.freetype

import readfile                     # 读取文件
import welcome as w                 # 欢迎界面
import easing                       # 缓动函数
import helper                       # def函数封装


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
tips = [
    "phigrOS正在加载中……",
    "等一下！请检查设备周围是否有水杯，要是碰到的话…嘶——",
    "长时间打歌会有引发腱鞘炎的风险哦，注意休息。",
    "玩久了，一定要记得闭上眼睛休息一会哦~",
    "如果打歌感到不舒畅，起身走走，然后回来，会好很多。",
    "如果不想被打断，那就去手机上的Phigros并且开免打扰吧！",
    "不知道如何解锁一些特定歌曲？拜托这里根本就没有！",
    "咕咕咕~如果你正开心，希望Phigros能让你笑颜常开哦！",
    "咕咕咕~如果你正糟心，希望Phigros能带你扬眉吐气哦！",
    "咕咕咕！请不要在任何无关场合提及Phigros哦！谢谢配合！咕咕咕！",
    "来唱歌！哼！哼！啊啊啊啊！",
    "帅鸽的话，只要像这样，dong~dong~dong~，就可以快速收歌哦，来，逝逝看！",
    "新版本请多多关照！发现bug请拨打：contact@pigeongames.cn或849806583@qq.com",
    "欢迎在B站 @Phigros官方账号 和 @Qin_zzq 关注我们!",
    "鸠和基诺会一直陪伴着你......只要你不卸载Python和Phigros的话！",
    "希望phigros能陪伴你们到天长地久，抱抱",
    "2.0啦，大家都长大啦ww",
    "鸽游的小鸽子们每天都在熬夜开发2.0版本，都快熬秃了头，生发水什么的可以来点吗……？",
    "我觉得生发剂不一定有用，得植发",
    "诶…防脱洗发水用完了…",
    "歌终有一收，而有些需要一点小小的帮助（指旋转设备",
    "铺面难度各有千秋，因人而异，因地力制宜（？",
    "给多押note镀层金，我就是这个谱面里最靓的仔",
    "这日子是越来越有判头了（指判定线",
    "假如，我是说假如，判定线能够自由地动起来…",
    "猜猜你要重新加载多少次才能再看到这条tip￣︶￣",
    "这是一条属于2.0版本的Tips！",
    "print(\"Hello tips2.0\");",
    "来猜猜看这边有几个有用的信息呢~",
    "你知道吗？其实tips全都是废话（确信",
    "啊！要给你看什么Tip好呢…(翻",
    "上次看到这条Tip还是在上次",
    "我相信你。",
    "不要在意他人对你说什么，你独一无二，你是你自己的光",
    "当你在三次觉得诸事不顺的时候，看看现在的打歌成绩，比起刚入坑的时候，是不是提高了很多？现在也是哦，你一直都在成长",
    "φ?拿来吧你!",
    "See You Next Time",
    "有一个人前来打歌",
    "阿鸠你又在反复看Tips了哦",
    "手持两把锟斤拷，口中疾呼烫烫烫",
    "热知识：这是一条…烫烫烫烫烫！的热知识。",
    "冷知识：这是一条…啊嚏！…冷知识！",
    "时间滴滴答答在走，这首歌你φ了没有？",
    "上次看到这条Tip还是在上次",
    "你AP了，就一定AP了吧！",
    "扉格晚五点，周五准时更新！",
    "对不起，你所拨打的电话号码是空号-Sorry, but JieGie don't come here~",
    "72788433374733678633778263464",
    "87164918361273612871264192346",
    "17812398762314891234986123479",
    "Let's! Get! Higher!!!",
    "One! Two! Three! Fire!!!",
    "高三党，现在，立刻，去给我学习！！！",
]
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()
nummark = "0000000"
PI = float('3.1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679')

# -------------------------------------------
w.welcome()  # 欢迎界面
Gamename = w.choose()  # 选择界面
w.loading()
info_data = readfile.lookfile(Gamename)
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
    progressBar = pygame.image.load("src/ProgressBar.png").convert_alpha()  # 进度条
    songsNameBar = pygame.image.load("src/SongsNameBar.png").convert_alpha()  # 歌曲名条
    pause = pygame.image.load("src/Pause.png").convert_alpha()  # 暂停
    clickRaw = pygame.image.load("src/clickRaw.png").convert_alpha()  # 点击特效
    tap = pygame.image.load("src/Tap.png").convert_alpha()  # Tap
    tap2 = pygame.image.load("src/Tap2.png").convert_alpha()  # Tap-BAD
    tapHL = pygame.image.load("src/TapHL.png").convert_alpha()  # Tap高亮
    drag = pygame.image.load("src/Drag.png").convert_alpha()  # Drag
    dragHL = pygame.image.load("src/DragHL.png").convert_alpha()  # Drag高亮
    holdHead = pygame.image.load("src/HoldHead.png").convert_alpha()  # Hold头部
    holdHeadHL = pygame.image.load("src/HoldHeadHL.png").convert_alpha()  # Hold头部高亮
    hold = pygame.image.load("src/Hold.png").convert_alpha()  # Hold身子
    holdHL = pygame.image.load("src/HoldHL.png").convert_alpha()  # Hold身子高亮
    holdEnd = pygame.image.load("src/HoldEnd.png").convert_alpha()  # Hold尾部
    flick = pygame.image.load("src/Flick.png").convert_alpha()  # Flick
    flickHL = pygame.image.load("src/FlickHL.png").convert_alpha()  # Flick高亮
    pic_LevelOver1 = pygame.image.load("src/LevelOver1.png").convert_alpha()  # LevelOver1中间成果条
    pic_LevelOver3 = pygame.image.load("src/LevelOver3.png").convert_alpha()  # LevelOver3等级背景
    pic_LevelOver4 = pygame.image.load("src/LevelOver4.png").convert_alpha()  # LevelOver4名字背景
    pic_LevelOver5 = pygame.image.load("src/LevelOver5.png").convert_alpha()  # LevelOver5名字左竖
    rank = pygame.image.load("src/Rank.png").convert_alpha()  # 等级图片
    continueButton = pygame.image.load("src/continue.png").convert_alpha()  # 继续
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
progressBar = pygame.transform.scale(progressBar, (WINDOW_X + 5, 5))  # 进度条儿调整大小
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
# 谱面识别！
datanum = 0
notedata = []
'''
格式：  
(1=Tap 2=Drag 3=Flick 4=Hold) int      int整数        float浮点数    float浮点数           bool布尔值         float浮点数
note类型                       note编号  note绑定的线儿  note出现时间   note在线的x相对位置    note是否正常掉落     note速度     
'''
for i in range(len(data[0])):  # 循环
    notedata.append(data[0][datanum][:-1])  # 把"\n"截掉
    datanum += 1

game_bpm = notedata[1][:][9:]  # bpm
print(notedata, '\n', game_bpm)
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
        ProgressX = -WINDOW_X - 5 + int(rate * WINDOW_X)  # 进度条X坐标(定位坐标在图像左上角，完成则为x0)(加载出图像需要时间)
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
    SongsName = f2.render_to(screen, [30, 503], info_data['other'][0][1:], fgcolor=(255, 255, 255), size=21)  # 歌曲名
    SongsLevel = f1.render_to(screen, [865, 507], info_data['other'][1], fgcolor=(255, 255, 255), size=18)  # 歌曲等级
    mark = f1.render_to(screen, [809, 25], str(nummark), fgcolor=(255, 255, 255), size=28)  # 分数
    try:
        otime = f1.render_to(screen, [0, 5],
                             '{}/{}'.format(time.strftime("%M:%S", time.localtime(less)), songlengthstr),
                             fgcolor=(255, 255, 255), size=12)
    except TypeError:
        otime = f1.render_to(screen, [0, 5], '{}/{}'.format(songlengthstr, songlengthstr), fgcolor=(255, 255, 255),
                             size=12)

    # ----------------------------------
    screen.blit(judgeLine, (0, WINDOW_Y / 2))
    # ----------------------------------

    mouse.update()  # 更新鼠标位置
    pygame.display.update()  # 更新屏幕
