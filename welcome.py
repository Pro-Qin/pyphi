#exo 1.x版本字体
#Saira 2.x版本字体


from tkinter import *
from tkinter import filedialog
import pygame
import sys
import pygame.freetype  #文本
import random
import time
import platform
import os
import zipfile
import shutil
from logi import *
import core as cor

# 创建userCharts文件夹（如果不存在）
user_charts_dir = os.path.join(os.path.dirname(__file__), 'userCharts')
if not os.path.exists(user_charts_dir):
    os.makedirs(user_charts_dir)

# 处理导入的文件并保存为zip
def handle_imported_file(file_path):
    # 获取文件名（不含扩展名）
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    zip_path = os.path.join(user_charts_dir, f'{file_name}.zip')

    # 检查是否为pez文件
    if file_path.lower().endswith('.pez'):
        # 创建临时目录
        temp_dir = os.path.join(os.path.dirname(__file__), 'temp')
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        try:
            # 解压pez文件
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            # 创建新的zip文件
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
                # 遍历临时目录中的所有文件
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_full_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_full_path, temp_dir)
                        zip_ref.write(file_full_path, arcname)

            # 清理临时目录
            shutil.rmtree(temp_dir)
            Log.info(f'成功导入并转换pez文件到: {zip_path}')
            return True, zip_path
        except Exception as e:
            Log.error(f'处理pez文件时出错: {str(e)}')
            return False, str(e)
    elif file_path.lower().endswith('.zip'):
        try:
            # 直接复制zip文件
            shutil.copy2(file_path, zip_path)
            Log.info(f'成功导入zip文件到: {zip_path}')
            return True, zip_path
        except Exception as e:
            Log.error(f'复制zip文件时出错: {str(e)}')
            return False, str(e)
    else:
        return False, '不支持的文件格式，仅支持.pez和.zip文件'

# 打开文件选择对话框
def import_file():
    file_path = filedialog.askopenfilename(
        title='选择谱面文件',
        filetypes=[('谱面文件', '*.pez *.zip')]
    )
    if file_path:
        success, message = handle_imported_file(file_path)
        if success:
            # 重新加载谱面列表
            global song_list, songlen
            song_list = load_song_list()
            songlen = len(song_list)
            print(f'文件导入成功: {message}')
        else:
            print(f'文件导入失败: {message}')

# 加载谱面列表
def load_song_list():
    """
    加载preset和userCharts文件夹中的所有谱面文件
    :return: 包含所有谱子信息的列表，每个元素是元组(谱子名称, 是否来自userCharts)
    """
    song_list = []
    
    # 扫描preset文件夹
    preset_dir = os.path.join(os.path.dirname(__file__), 'preset')
    if os.path.exists(preset_dir):
        for file in os.listdir(preset_dir):
            if file.lower().endswith('.zip'):
                song_name = os.path.splitext(file)[0]
                song_list.append((song_name, False))
    
    # 扫描userCharts文件夹
    user_charts_dir = os.path.join(os.path.dirname(__file__), 'userCharts')
    if os.path.exists(user_charts_dir):
        for file in os.listdir(user_charts_dir):
            if file.lower().endswith('.zip'):
                song_name = os.path.splitext(file)[0]
                song_list.append((song_name, True))
    
    return song_list

# 绘制圆角矩形
def draw_rounded_rect(surface, rect, color, radius):
    x, y, width, height = rect
    pygame.draw.rect(surface, color, (x, y + radius, width, height - 2 * radius))
    pygame.draw.rect(surface, color, (x + radius, y, width - 2 * radius, height))
    pygame.draw.circle(surface, color, (x + radius, y + radius), radius)
    pygame.draw.circle(surface, color, (x + width - radius, y + radius), radius)
    pygame.draw.circle(surface, color, (x + radius, y + height - radius), radius)
    pygame.draw.circle(surface, color, (x + width - radius, y + height - radius), radius)


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
    LIGHT_BLUE = (173, 216, 230, 255)  # 浅蓝色
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

    #加载谱面列表
    global song_list, songlen
    song_list = load_song_list()
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

        # 导入按钮参数
        import_btn_width = 30
        import_btn_height = 30
        import_btn_x = window_x - import_btn_width - 20
        import_btn_y = 20
        import_btn_radius = 10
        import_btn_color = (255, 255, 255, 155)  # 白色，透明度155

        # 导入按钮矩形
        import_btn_rect = (import_btn_x, import_btn_y, import_btn_width, import_btn_height)


        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                #卸载所有模块
                pygame.quit()
                #终止程序
                sys.exit()
            if event.type==pygame.MOUSEBUTTONDOWN:
                if event.button==1:
                    #pos[0] = x       pos[1] = y
                    # 检查导入按钮点击
                    if (event.pos[0] >= import_btn_x and
                        event.pos[0] <= import_btn_x + import_btn_width and
                        event.pos[1] >= import_btn_y and
                        event.pos[1] <= import_btn_y + import_btn_height):
                        # 打开文件选择对话框
                        import_file()
                    else:
                        # 检查是否点击了谱面按钮
                        for i in range((songlen-1)//columns+1):
                            for j in range(columns):
                                idx = i * columns + j
                                if idx >= songlen:
                                    break
                                # 计算当前按钮位置
                                current_pic_x = 55 + i * ypp
                                current_button_x = 76 + 159*1.5 + i * ypp
                                current_button_y = 62 + j * xpp
                                # 检查点击位置
                                if (event.pos[0] >= current_button_x and
                                    event.pos[0] <= current_button_x + button_width and
                                    event.pos[1] >= current_button_y and
                                    event.pos[1] <= current_button_y + button_height):
                                    song_name = song_list[idx][0]
                                    Log.info(f'User Choose [{idx}]: {song_name}')
                                    return song_name.replace(" ","")
        screen.blit(image_surface, (0, 0))
        
        # 绘制导入按钮
        temp_surface = pygame.Surface((import_btn_width, import_btn_height), pygame.SRCALPHA)
        draw_rounded_rect(temp_surface, (0, 0, import_btn_width, import_btn_height), import_btn_color, import_btn_radius)
        screen.blit(temp_surface, (import_btn_x, import_btn_y))

        u = 0
        columns = 4
        for i in range((songlen-1)//columns+1):#排列-列个数
            current_pic_x = 55 + i * ypp
            current_button_x = 76 + 159*1.5 + i * ypp
            current_name_x = 90 + i * ypp
            
            for j in range(columns):
                idx = i * columns + j
                if idx >= songlen:#判定有没有超出list个数
                    break#跳出这个循环力

                screen.blit(songpic, (current_pic_x,pic_y+xpp*(j)))#绘制歌曲背景
                screen.blit(songstart, (current_button_x,button_y+xpp*(j)))#绘制选歌按钮
                song_name, is_user_chart = song_list[idx]
                color = LIGHT_BLUE if is_user_chart else WHITE
                if is_chinese(song_name):
                    font_CN.render_to(screen,(current_name_x,name_y+xpp*(j)-4),song_name,color)#绘制歌曲名称
                else:
                    font_EN.render_to(screen,(current_name_x,name_y+xpp*(j)),song_name,color)#绘制歌曲名称
                u+=1

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
