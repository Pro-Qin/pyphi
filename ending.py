from tkinter import *
import pygame
import sys
import pygame.freetype  #文本
import random
import time
import platform
import core as cor
from PIL import Image, ImageFilter, ImageEnhance
import data

debug = True

if debug:
    data.load_zip("preset/WeAreHardcore.zip")
    # cor.IMAGE

def is_chinese(string):
    """
    检查整个字符串是否包含中文
    :param string: 需要检查的字符串
    :return: bool
    """
    for ch in string:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True

    return False

if len(cor.ENDLIST) <= 1:
    cor.ENDLIST = {
        'score':1000000,#.zfill(7) 前面补0
        'perfect':1145,
        'maxcombo':1145,
        'acc':1,#b1 = float(b) * 100;b2 = f"{b1}%" 转化为百分数
        'good':0,
        'bad':0,
        'miss':0,
        'early':0,
        'late':0,
        'level':'FM Lv.0',
        'name':'Test',
        'username':'Guest',
        }
alist = cor.ENDLIST
score = int(alist['score'])

#等级判定 顺序不可变！
if score == 0:grade = "" 
elif 1000000 <= score:grade = "phi"
elif alist['bad'] == 0 and alist['miss'] == 0:grade = "V-FC"
elif score < 699999 and score != 0:grade = "F" 
elif 700000 <= score and score <= 819999:grade = "C" 
elif 820000 <= score and score <= 879999:grade = "B" 
elif 880000 <= score and score <= 919999:grade = "A" 
elif 920000 <= score and score <= 959999:grade = "S" 
elif 960000 <= score and score <= 999999:grade = "V" 

levelstring = alist['level'].split(' ')[0]
# print(alist['level'],levelstring)
if levelstring == 'EZ':playLevel=0
elif levelstring == 'HD':playLevel=1
elif levelstring == 'IN':playLevel=2
elif levelstring == 'AT':playLevel=3
else:playLevel=3

#使用pygame之前必须初始化
pygame.init()
pygame.mixer.init()
pygame.font.init()

window_x = cor.WIDTH
window_y = cor.HEIGHT
WHITE = (255,255,255)
BLACK = (0,0,0)
FPS = 60

pygame.mixer.music.load('resources/audio/mute.ogg')#静音
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play()

screen = pygame.display.set_mode((window_x, window_y))                  #设置主屏窗口
screen.fill((0,0,0))                                                    #填充主窗口的背景颜色，参数值RGB（颜色元组）
keep_going = True                                                       #循环标志
pygame.display.set_caption(cor.TITLE)                        #设置窗口标题

font_EN=pygame.font.Font(r"resources/Saira-Medium.ttf",38) 
font_EN_title=pygame.font.Font(r"resources/Saira-Medium.ttf",35)
font_EN_subtitle=pygame.font.Font(r"resources/Saira-Medium.ttf",16)
font_EN_s=pygame.font.Font(r"resources/Saira-Medium.ttf",24) 
font_EN_ss=pygame.font.Font(r"resources/Saira-Medium.ttf",12) 
font_EN_sss=pygame.font.Font(r"resources/Saira-Medium.ttf",8) 
font_2=pygame.font.Font(r"resources/Exo-Regular.pfb.ttf",12) 
font_pf=pygame.freetype.Font(r"resources/PingFang.ttf",15) 
font_pfs=pygame.freetype.Font(r"resources/PingFang.ttf",11) 
font_Pfs=pygame.font.Font(r"resources/PingFang.ttf",24) 

#背景图片
image_surface = pygame.image.load('./cache/bg_b_b.jpg').convert()      #加载背景
image_surface.scroll(0,0)
image_surface = pygame.transform.scale(image_surface, (window_x,window_y))

image_replay = pygame.image.load('resources/texture/replay.png').convert_alpha()# 重开按钮
image_replay = pygame.transform.scale(image_replay, (203/3,130/3))

# image_user = cor.cutimage('resources/texture/Introduction.png',15,"cache/Introduction_.png",(105,61))#切割为平行四边形
image_useroffset = cor.cutimage_rect('resources/texture/Introduction.png',(105,61),"cache/Introduction_.png")
image_user = pygame.image.load('cache/Introduction_.png').convert_alpha()# 用户头像
# image_user = pygame.transform.scale(image_user, (105,61))

#[size,0+pas],[w,0+pas],[w-size,h-pas],[0,h-pas]
# pygame.draw.polygon(screen, (0, 0, 0), [(100, 100), (150, 50), (200, 100), (250, 50)], 0)
image_bar = pygame.image.load('resources/texture/EndingInfoBar.png').convert_alpha()# 右上角信息背景平行四边形
# image_bar = pygame.transform.scale(image_user, (image_user.get_width()/2,image_user.get_height()/2))

# print(cor.IMAGE)
# image_song = cor.cutimage(cor.IMAGE,21,"cache/Song_.png",(417 ,313))#切割为平行四边形
# image_songoffset = cor.cutimage_rect(cor.IMAGE,(417 ,313),"cache/Song_.png")
image_songoffset = (0,0)
image_song = pygame.image.load(cor.IMAGE).convert_alpha()# 左边曲绘
image_song_ = pygame.transform.scale(image_song, (417 ,313))
# image_songoffset = cor.cutimage(image_song,cor.IMAGE,84,"cache/Song_.png",(417,313))
# image_song_ = pygame.image.load("cache/Song_.png").convert_alpha()# 左边曲绘

image_rect1 = pygame.image.load('resources/texture/EndingRect1.png').convert_alpha()# 右边上方大bar
image_rect2 = pygame.image.load('resources/texture/EndingRect2.png').convert_alpha()# 右边上方大bar

# print(grade)
image_level = pygame.image.load('resources/texture/level/{}.png'.format(grade)).convert_alpha()# 等级图

image_scb = pygame.image.load('resources/texture/EndSongCoverBlack.png').convert_alpha()# 歌曲遮盖黑色渐变图

image_continue = pygame.image.load('resources/texture/continue.png').convert_alpha()# 继续按钮
image_continue = pygame.transform.scale(image_continue, (203/3,130/3))


pygame.mixer.music.load("resources"+"/audio/LevelOver" + str(playLevel) + ".ogg")#resources/audio/LevelOver0.ogg
pygame.mixer.music.set_volume(0.5)
# print(playLevel)
pygame.mixer.music.play(-1)

#文字类
text_username   = font_Pfs.render(alist['username'],True,'#FFFFFF')#用户名
text_score      = font_EN.render(str(score).zfill(7),True,'#FFFFFF')#分数
text_maxcombonum= font_EN_s.render(str(alist['maxcombo']),True,'#FFFFFF')# maxcombo值
text_maxcombostr= font_EN_ss.render('Max Combo',True,'#FFFFFF')# maxcombo文字
text_accnum     = font_EN_s.render(f"{float(alist['acc']) * 100}%",True,'#FFFFFF')# acc值
text_accstr     = font_EN_ss.render('Accuracy',True,'#FFFFFF')# acc文字
text_perfectnum = font_EN_s.render(str(alist['perfect']),True,'#FFFFFF')# Perfect值
text_perfectstr = font_EN_sss.render('Perfect',True,'#FFFFFF')# Perfect文字
text_goodnum    = font_EN_s.render(str(alist['good']),True,'#FFFFFF')# Good值
text_goodstr    = font_EN_sss.render('Good',True,'#FFFFFF')# Good文字
text_badnum     = font_EN_s.render(str(alist['bad']),True,'#FFFFFF')# Bad值
text_badstr     = font_EN_sss.render('Bad',True,'#FFFFFF')# Bad文字
text_missnum    = font_EN_s.render(str(alist['miss']),True,'#FFFFFF')# Miss值
text_missstr    = font_EN_sss.render('Miss',True,'#FFFFFF')# Miss文字
text_earlynum   = font_EN_ss.render(str(alist['early']),True,'#FFFFFF')# early值
text_earlystr   = font_EN_ss.render('Early',True,'#FFFFFF')# early文字
text_latenum    = font_EN_ss.render(str(alist['miss']),True,'#FFFFFF')# late值
text_latestr    = font_EN_ss.render('Late',True,'#FFFFFF')# late文字
text_songname   = font_EN_title.render(alist['name'],True,'#FFFFFF')# 歌曲名
text_songlevel  = font_EN_subtitle.render(alist['level'],True,'#FFFFFF')# 歌曲等级

#鼠标类
class Mouse(pygame.sprite.Sprite):
    def __init__(self):
        self.image = pygame.Surface((5,5))
        self.image.fill('#E758E9')
        self.rect = self.image.get_rect()
        self.rect.center = pygame.mouse.get_pos()#初始位置到鼠标指针
    def update(self):
        self.rect.center = pygame.mouse.get_pos()#移到鼠标指针位置
        screen.blit(self.image, self.rect)

#创建鼠标精灵
mouse = Mouse()
pygame.display.flip()#刷新屏幕
time_begin = int(time.time())
# 如果没有下列主循环代码，运行结果会一闪而过
active = True
while active:  
    now = int(time.time())
    less = now-time_begin
    clock = pygame.time.Clock()  
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            #卸载所有模块
            pygame.quit()
            #终止程序
            sys.exit()
        if event.type==pygame.MOUSEBUTTONDOWN:
            if event.button==1:
                #pos[0] = x       pos[1] = y
                if event.pos[0] <= image_replay.get_size()[0] and 6 < event.pos[1] <= image_replay.get_size()[1]:#重开
                    #卸载所有模块
                    pygame.quit()
                    #终止程序
                    sys.exit()
                elif cor.WIDTH-image_continue.get_size()[0] < event.pos[0] <= cor.WIDTH and cor.HEIGHT-image_continue.get_size()[1]-6 < event.pos[1] <= cor.HEIGHT-6:#继续
                    # print('已按下')
                    active = False
    
    screen.blit(image_surface, (0, 0))#背景
    screen.blit(image_replay, (0, 6))#重开按钮
    screen.blit(image_bar, (cor.WIDTH-image_bar.get_rect().w, 7))
    screen.blit(image_user, (cor.WIDTH-image_user.get_rect().w-46-image_useroffset[0], 9-image_useroffset[1]-5))
    screen.blit(image_song_, (51-10-image_songoffset[0],113-image_songoffset[1]))
    screen.blit(image_rect1, (525-10,113))
    screen.blit(image_rect2, (504-10,292))
    screen.blit(image_rect2, (484-10,368))
    screen.blit(image_level, (789-38,150-13))
    screen.blit(image_scb, (51-10-image_songoffset[0],113-5-image_songoffset[1]))
    screen.blit(image_continue, (cor.WIDTH-image_continue.get_size()[0],cor.HEIGHT-image_continue.get_size()[1]-6))

    screen.blit(text_username, (780-text_username.get_size()[0]-10,19))
    screen.blit(text_score, (560,185))
    screen.blit(text_maxcombonum, (522,295))
    screen.blit(text_maxcombostr, (522,295+30))
    screen.blit(text_accnum, (845-text_accnum.get_size()[0]-10,295))
    screen.blit(text_accstr, (845-text_accstr.get_size()[0]-10,295+30))
    screen.blit(text_perfectnum, (531-text_perfectnum.get_size()[0]/2-10,372))
    screen.blit(text_perfectstr, (531-text_perfectstr.get_size()[0]/2-10,372+30))
    screen.blit(text_goodnum, (601-text_goodnum.get_size()[0]/2-10,372))
    screen.blit(text_goodstr, (601-text_goodstr.get_size()[0]/2-10,372+30))
    screen.blit(text_badnum, (651-text_badnum.get_size()[0]/2-10,372))
    screen.blit(text_badstr, (651-text_badstr.get_size()[0]/2-10,372+30))
    screen.blit(text_missnum, (701-text_missnum.get_size()[0]/2-10,372))
    screen.blit(text_missstr, (701-text_missstr.get_size()[0]/2-10,372+30))
    screen.blit(text_earlynum, (745+75-text_earlynum.get_size()[0]-10,380))
    screen.blit(text_earlystr, (745-10,380))
    screen.blit(text_latenum, (745+75-text_earlynum.get_size()[0]-10,380+15))
    screen.blit(text_latestr, (745-10,380+15))
    screen.blit(text_songname, (80-10,380-10))
    screen.blit(text_songlevel, (400-10,400-10))
                
    mouse.update()   
    pygame.display.update()#更新屏幕
# print('脱离主线程')
import main
