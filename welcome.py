#exo 1.x版本字体
#Saira 2.x版本字体


from tkinter import *
import pygame
import sys
import pygame.freetype  #文本
import random
import time
import platform
from logi import *
import core as cor

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

def welcome():
    '''已报废，备份'''
    window = Tk()
    window.title('Phigros for Python运行须知')
    window.geometry('420x150')
    #window.resizable(0,0)


    def close_window():
        window.destroy()

    swq = platform.system()

    Label(window, text="1.已安装Python3.x版本").place(x=2,y=0)
    Label(window, text="2.已安装pygame,PIL,zipfile,readfile,pydub,eyed3库").place(x=2,y=20)
    Label(window, text="3.开发环境为macOS，可能不太兼容").place(x=2,y=40)
    Label(window, text="4.你当前的系统是{}".format(swq)).place(x=2,y=60)
    Label(window, text="5.闪退90%是你的问题，请检查文件是否存在以及格式是否符合要求！").place(x=2,y=80)
    Label(window, text="6.程序尚未开发完整").place(x=2,y=100)
    
    Button(window,text="确定",command=close_window).place(x=90,y=120)
    Button(window,text="取消",command=sys.exit).place(x=170,y=120)
    window.mainloop()

def choose():
    #使用pygame之前必须初始化
    pygame.init()
    pygame.mixer.init()
    pygame.font.init()

    window_x = int(1920/2)
    window_y = int(1080/2)
    WHITE = (255,255,255)
    BLACK = (0,0,0)
    FPS = 60

    screen = pygame.display.set_mode((window_x, window_y))                #设置主屏窗口
    screen.fill((30,30,30))                                     #填充主窗口的背景颜色，参数值RGB（颜色元组）
    keep_going = True                                           #循环标志
    pygame.display.set_caption(cor.TITLE)            #设置窗口标题
    Log.info('Loading Choose UI.')
    font_EN=pygame.freetype.Font(r"resources/Saira-Medium.ttf",18*1.3)#设置字体
    font_CN=pygame.freetype.Font(r"resources/PingFang.ttf",18*1.3)#设置字体
    #背景图片
    image_surface = pygame.image.load('resources/texture/background.png').convert()      #加载背景
    image_surface.scroll(0,0)
    image_surface = pygame.transform.scale(image_surface, (window_x,window_y))

    #歌曲列表
    song_list = ['We Are Hardcore','Terrasphere','Aphasia']
    songlen = len(song_list)
    #加载歌曲背景
    songpic = pygame.image.load('resources/texture/song.png').convert_alpha()
    songpic = pygame.transform.scale(songpic,(854/4*1.5,183/4*1.5))          #调整大小 

    songstart = pygame.image.load('resources/texture/start.png').convert_alpha()
    songstart = pygame.transform.scale(songstart,(71/4*1.5,80/4*1.5))          #调整大小
    pygame.mixer.music.load('resources/audio/music.mp3')#背景音乐
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)#循环播放

    

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



    #主循环
    while 1:  
        clock = pygame.time.Clock()  
        clock.tick(FPS)
        pic_x=55;pic_y=45#载体
        button_x=76+159*1.5;button_y=62#开始按钮
        name_x=90;name_y=70#歌曲名称

        button_width=71/4*1.5;button_height=80/4*1.5
        xpp = 120#竖间隔
        ypp = 350#竖间隔


        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                #卸载所有模块
                pygame.quit()
                #终止程序
                sys.exit()
            if event.type==pygame.MOUSEBUTTONDOWN:
                if event.button==1:
                    #pos[0] = x       pos[1] = y
                    if event.pos[0]>=button_x                      and event.pos[0]<=button_x+button_width                    and event.pos[1]>=button_y and event.pos[1]<=button_y+button_height:
                        #判断鼠标点击位置是否在选歌按钮1上
                        #print('用户选择:',song_list[0])
                        Log.info('User Choose [0]')
                        return song_list[0].replace(" ","")
                    elif event.pos[0]>=button_x                    and event.pos[0]<=button_x+button_width                    and event.pos[1]>=button_y+xpp and event.pos[1]<=button_y+xpp+button_height:
                        #判断鼠标点击位置是否在选歌按钮2上
                        #print('用户选择:',song_list[1])
                        Log.info('User Choose [1]')
                        return song_list[1].replace(" ","")
                    elif event.pos[0]>=button_x                    and event.pos[0]<=button_x+button_width           and event.pos[1]>=button_y+(xpp*2) and event.pos[1]<=button_y+(xpp*2)+button_height:
                        #判断鼠标点击位置是否在选歌按钮3上
                        #print('用户选择:',song_list[2])
                        Log.info('User Choose [2]')
                        return song_list[2].replace(" ","")
        screen.blit(image_surface, (0, 0))
        
        u = 0
        columns = 4
        for i in range((songlen-1)//columns+1):#排列-列个数
            
            for i in range(columns):
                if u >= songlen:#判定有没有超出list个数
                    break#跳出这个循环力

                screen.blit(songpic, (pic_x,pic_y+xpp*(i)))#绘制歌曲背景
                screen.blit(songstart, (button_x,button_y+xpp*(i)))#绘制选歌按钮
                if is_chinese(song_list[u]):
                    font_CN.render_to(screen,(name_x,name_y+xpp*(i)-4),song_list[u],WHITE)#绘制歌曲名称
                else:
                    font_EN.render_to(screen,(name_x,name_y+xpp*(i)),song_list[u],WHITE)#绘制歌曲名称
                u+=1
            pic_x+=ypp;button_x+=ypp;name_x+=ypp

        #screen.blit(songpic, (pic_x,pic_y+xpp))#绘制歌曲背景
        #screen.blit(songstart, (button_x,button_y+xpp))#绘制选歌按钮
        #SongName2 = font_EN.render_to(screen,(name_x,name_y+xpp),song_list[1],WHITE)#绘制歌曲名称


        #screen.blit(songpic, (pic_x,pic_y+xpp))#绘制歌曲背景
        #screen.blit(songstart, (button_x,button_y+xpp))#绘制选歌按钮
        #SongName3 = font_EN.render_to(screen,(name_x,name_y+xpp),song_list[2],WHITE)#绘制歌曲名称

        mouse.update()   
        pygame.display.update()#更新屏幕

def loading():
    #使用pygame之前必须初始化
    pygame.init()
    pygame.mixer.init()
    pygame.font.init()

    window_x = int(1920/2)
    window_y = int(1080/2)
    WHITE = (255,255,255)
    BLACK = (0,0,0)
    FPS = 60

    pygame.mixer.music.load('resources/audio/mute.ogg')#静音
    pygame.mixer.music.play()

    screen = pygame.display.set_mode((window_x, window_y))                  #设置主屏窗口
    screen.fill((0,0,0))                                                    #填充主窗口的背景颜色，参数值RGB（颜色元组）
    keep_going = True                                                       #循环标志
    pygame.display.set_caption(cor.TITLE)                        #设置窗口标题

    font_EN=pygame.freetype.Font(r"resources/Saira-Medium.ttf",16)#设置字体
    font_2=pygame.freetype.Font(r"resources/Exo-Regular.pfb.ttf",15)#设置字体
    font_pf=pygame.freetype.Font(r"resources/PingFang.ttf",15)#设置字体
    font_pfs=pygame.freetype.Font(r"resources/PingFang.ttf",11)#设置字体

    #背景图片
    image_surface = pygame.image.load('resources/texture/background.png').convert()      #加载背景
    image_surface.scroll(0,0)
    image_surface = pygame.transform.scale(image_surface, (window_x,window_y))

    image_b = pygame.image.load('resources/texture/b2w.png').convert_alpha()
    image_b = pygame.transform.scale(image_b, (window_x,window_y/4))
    #歌曲列表
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
    tipstring = tips[random.randint(0,len(tips)-1)]

    

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
    while 1:  
        now = int(time.time())
        less = now-time_begin
        clock = pygame.time.Clock()  
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pass
        
        if less>=5:
            pygame.quit()
            return
        screen.blit(image_surface, (0, 0))
        screen.blit(image_b,(0,window_y/4*3))

        if len(tipstring)>=50:
            Tipstr = font_pfs.render_to(screen,(35,495),'Tip: {}'.format(tipstring),WHITE)#绘制
        else:
            Tipstr = font_pf.render_to(screen,(35,495),'Tip: {}'.format(tipstring),WHITE)#绘制
        Loadstr = font_EN.render_to(screen,(850,495),'Loading...',WHITE)#绘制

        mouse.update()   
        pygame.display.update()#更新屏幕


    

if __name__ == '__main__':
    #welcome()
    choose()
