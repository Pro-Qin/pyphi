#from logging import *
#basicConfig(filename='# Log.txt', level=INFO,format='[%(levelname)s][%(asctime)s]:%(message)s')
# from logi import *
# Log = Log()

from PIL import Image, ImageFilter, ImageEnhance
import core as cor
import pygame
import sys
import time
import data
import element
import tinytag
import pygame.freetype
import welcome as w
import random
import shutil  
shutil.rmtree('cache')  #清空缓存
pygame.init()
gamename = w.choose()#选择界面
data.load_zip("preset/{}.zip".format(gamename))
w.loading()# 加载界面
# Log.info('Loading UI.')

# ---------- PYGAME INIT ----------
# 初始化音频
pygame.mixer.init()
pygame.mixer.music.load(cor.SONG)
pygame.freetype.init()
pygame.font.init()
# Log.info('Initing.')

# 初始化图像
pil_blurred = Image.open(cor.IMAGE).filter(ImageFilter.GaussianBlur(radius=15))
brightEnhancer = ImageEnhance.Brightness(pil_blurred)
img = brightEnhancer.enhance(0.5)
img.convert("RGB").save("./cache/bg_b_b.jpg", quality=75)
# convert it back to a pygame surface
background = pygame.transform.smoothscale(pygame.image.load("./cache/bg_b_b.jpg"),(cor.WIDTH, cor.HEIGHT))
# Log.info('Image Init.')
try:
    # 初始化字体
    f1      = pygame.freetype.Font(r"resources/Exo-Regular.pfb.ttf", 12)
    f2      = pygame.freetype.Font(r"resources/Saira-Medium.ttf", 15)
    font1   = pygame.font.Font(r"resources/Exo-Regular.pfb.ttf", 14)
    font2   = pygame.font.Font(r"resources/Saira-Medium.ttf", 30)
    font40  = pygame.font.Font("resources/cmdysj.ttf", 40)
    font30  = pygame.font.Font("resources/cmdysj.ttf", 30)
    font25  = pygame.font.Font("resources/cmdysj.ttf", 25)
    font20  = pygame.font.Font("resources/cmdysj.ttf", 20)
    # Log.info('Loading fonts.')
except FileNotFoundError:
    pass
    # Log.error('文件缺失', '您运行的程序未找到字体文件，请检查程序是否完整。','The program you are running cannot find the font file.')

# 初始化界面
screen = pygame.display.set_mode((cor.WIDTH, cor.HEIGHT), vsync=True)
surface = pygame.Surface((cor.WIDTH, cor.HEIGHT), pygame.SRCALPHA)
pygame.display.set_caption(cor.TITLE)
# Log.info('Loading window.')

# 初始化时钟
clock = pygame.time.Clock()

# ---------- PYGAME INIT ----------
try:
    songsNameBar = pygame.image.load("resources/texture/SongsNameBar.png").convert_alpha()  # 歌曲名条
    pause = pygame.image.load("resources/texture/Pause.png").convert_alpha()  # 暂停
except FileNotFoundError:
    pass
    # Log.error('文件缺失', '您运行的程序未找到文件，请检查程序是否完整。','The program you are running cannot find the file.')
# ---------- GAME INIT ----------
fps = 180
skip = 0
beat = cor.BeatObject.get_value(skip/60)
cor.OFFSET -= 175
note_num = 0
duration = tinytag.TinyTag.get(cor.SONG).duration
# Log.info('Set vars.')

elementPainter = element.ElementPainter()
evalPainter = element.EvalPainter()

if cor.NOTE_NUM == 0:
    cor.NOTE_NUM = 1
    note_num = 1
# Log.info('Loading charts.')

for jl in cor.judge_line_list:
    note_bin = []
    for note in jl.not_holds:
        if note.at < beat:
            note_bin.append(note)
        else:
            break
    for note in note_bin:
        jl.not_holds.remove(note)
        if note in jl.above1:
            jl.above1.remove(note)
        else:
            jl.above2.remove(note)
        if not note.fake:
            note_num += 1
            # perfect += 1

    note_bin = []
    for note in jl.holds:
        if note.end < beat:
            note_bin.append(note)
        if note.at <= beat and (time.time() - note.last_eval_time >= 0.2):
            note.last_eval_time = time.time()

    for note in note_bin:
        jl.holds.remove(note)
        if note in jl.above1:
            jl.above1.remove(note)
        else:
            jl.above2.remove(note)
        if not note.fake:
            note_num += 1
            # perfect += 1
# Log.info('Loading charts DONE.')
# ---------- GAME INIT ----------
songsNameBar = pygame.transform.scale(songsNameBar, (4, 21))  # 歌曲名条调整大小
pause = pygame.transform.scale(pause, (20, 20))  # 暂停按钮调整大小
# Log.info('Set pic bg DONE.')
# ---------- GAME START ----------

pygame.mixer.music.play(start=skip)
pygame.mixer.music.set_volume(0.5)
# pygame.mixer.music.set_endevent(gotoend)
start = time.time()
beat = cor.BeatObject.get_value((time.time()-start+skip-cor.OFFSET/1000)/60)
maxcombo=0;perfect=0;good=0;bad=0;miss=0
try:
    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                #print(cor.DEBUG_K, cor.DEBUG_N)
                if event.scancode == 82:
                    cor.DEBUG_K += 0.05
                elif event.scancode == 81:
                    cor.DEBUG_K -= 0.05
                elif event.scancode == 79:
                    cor.DEBUG_N += 0.05
                elif event.scancode == 80:
                    cor.DEBUG_N -= 0.05
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                if event.button == 1:
                    if 19 <= pos[0] <= 19 + 20 and 20 <= event.pos[1] <= 20 + 20:
                        trueend = False
                        sys.exit()
        # ---------- EVENT RESPOND ----------

        # ---------- ESSENTIAL ----------

        if beat < 0:
            beat = cor.BeatObject.get_value((time.time() - start + skip - cor.OFFSET / 1000) / 60)
            continue

        screen.blit(background, (0, 0))
        # screen.fill((50, 50, 50))
        surface.fill((0, 0, 0, 0))

        # 进度条
        pygame.draw.rect(screen, (200, 200, 200),((0, 0), ((pygame.mixer.music.get_pos()/1000+skip)/duration*cor.WIDTH, 8)))
        if pygame.mixer.music.get_busy() == False:
            trueend = True
            break

        
        # ---------- ESSENTIAL ----------

        # ---------- DISPLAY ELEMENTS ----------

        # for jl in core.judge_line_list:
        #     note_bin = []
        #     for note in jl.not_holds:
        #         if note.at < beat:
        #             note_bin.append(note)
        #         else:
        #             break
        #     for note in note_bin:
        #         jl.not_holds.remove(note)
        #         if note in jl.above1:
        #             jl.above1.remove(note)
        #         else:
        #             jl.above2.remove(note)
        #         if not note.fake:
        #             evalPainter.add_note(note, core.Eval.PERFECT)
        #             if note.id == element.Note.TAP:
        #                 core.TAP_SOUND.play()
        #             elif note.id == element.Note.DRAG:
        #                 core.DRAG_SOUND.play()
        #             elif note.id == element.Note.FLICK:
        #                 core.FLICK_SOUND.play()
        #             note_num += 1
        #             perfect += 1
        #
        #     note_bin = []
        #     for note in jl.holds:
        #         if note.end < beat:
        #             note_bin.append(note)
        #
        #         if note.at <= beat and (time.time() - note.last_eval_time >= 0.2):
        #             if not note.fake:
        #                 if note.last_eval_time == -1:
        #                     core.TAP_SOUND.play()
        #                 evalPainter.add_note(note, core.Eval.PERFECT)
        #             note.last_eval_time = time.time()
        #
        #     for note in note_bin:
        #         jl.holds.remove(note)
        #         if note in jl.above1:
        #             jl.above1.remove(note)
        #         else:
        #             jl.above2.remove(note)
        #         if not note.fake:
        #             note_num += 1
        #             perfect += 1

        for jl in cor.judge_line_list:
            jl.blit(surface, beat)

            note_bin = []
            for note in jl.not_holds:
                if note.at < beat:
                    note_bin.append(note)
                else:
                    break
            for note in note_bin:
                jl.not_holds.remove(note)
                if note in jl.above1:
                    jl.above1.remove(note)
                else:
                    jl.above2.remove(note)
                if not note.fake:
                    evalPainter.add_note(note, cor.Eval.PERFECT)
                    if cor.ENABLE_SOUND:
                        if note.id == element.Note.TAP:
                            cor.TAP_SOUND.play()
                        elif note.id == element.Note.DRAG:
                            cor.DRAG_SOUND.play()
                        elif note.id == element.Note.FLICK:
                            cor.FLICK_SOUND.play()
                    note_num += 1
                    perfect += 1

            note_bin = []
            for note in jl.holds:
                if note.end < beat:
                    note_bin.append(note)

                if note.at <= beat and (time.time() - note.last_eval_time >= 0.2):
                    if not note.fake:
                        if note.last_eval_time == -1:
                            if cor.ENABLE_SOUND:
                                cor.TAP_SOUND.play()
                        evalPainter.add_note(note, cor.Eval.PERFECT)
                    note.last_eval_time = time.time()

            for note in note_bin:
                jl.holds.remove(note)
                if note in jl.above1:
                    jl.above1.remove(note)
                else:
                    jl.above2.remove(note)
                if not note.fake:
                    note_num += 1
                    perfect += 1

        # elementPainter.paint(surface, beat)
        evalPainter.blit(surface)

        # ---------- DISPLAY ELEMENTS ----------

        # ---------- DISPLAY TEXTS ----------
        if note_num > maxcombo:maxcombo = note_num
        combo_text      = font1.render("COMBO", True, (255, 255, 255))
        combo_num_text  = font2.render(str(note_num), True, (255, 255, 255))
        #score_text = font30.render(str(int(note_num/cor.NOTE_NUM*1000000)).rjust(7, '0'), True, (255, 255, 255))
        #fps_text = font25.render(str(int(clock.get_fps())).rjust(3, "0"), True, (255, 255, 255))
        #offset_text = font20.render(f"OFFSET={cor.OFFSET}", True, (255, 255, 255))

        if note_num >= 3:
            surface.blit(combo_text, (cor.WIDTH/2-font1.size("COMBO")[0]/2+2.5, 42))
            surface.blit(combo_num_text, (cor.WIDTH/2-font25.size(str(note_num))[0]/2, 3))
        surface.blit(pause, (20, 21))  # 暂停按钮
        surface.blit(songsNameBar, (20, 500))  # 歌曲名条
        SongsName       = f2.render_to(screen, [30, 503], cor.NAME, fgcolor=(255, 255, 255), size=21)  # 歌曲名
        SongsLevel      = f1.render_to(screen, [870, 507], cor.LEVEL,fgcolor=(255, 255, 255), size=18)  # 歌曲等级
        mark            = f1.render_to(screen, [815, 23],str(int(note_num/cor.NOTE_NUM*1000000)).rjust(7, "0"), fgcolor=(255, 255, 255), size=28)  # 分数
        fps_text        = f1.render_to(screen, [0, 8],str(int(clock.get_fps())).rjust(3, "0"), fgcolor=(255, 255, 255), size=12)

        # ---------- DISPLAY TEXTS ----------

        # ---------- REFRESH ----------

        screen.blit(surface, (0, 0))
        pygame.display.flip()
        clock.tick(fps)
        beat = cor.BeatObject.get_value((pygame.mixer.music.get_pos()/1000+skip-cor.OFFSET/1000)/60)

        # ---------- REFRESH ----------
except BaseException as b:
    print(b)
    # Log.error('程序错误', '您运行的程序运行过程中发生了错误，请检查程序是否经过修改、删减、改名等操作。并检查您的pygame是否为最新版本与python是否为3.10。','Game Main Code has been error!')
finally:
    if trueend:
        连击分 = maxcombo/note_num*100000
        oncescore=1/note_num;acc_ = 0+perfect*oncescore+good*0.65*oncescore
        rks = ((100*float(acc_)-55)/45)**2.0*float(cor.getnum_str(cor.LEVEL)) if acc_>=0.7 else 0#单曲rks算法为：若ACC<70%，则rks为0；若ACC≥70%，则rks=((100*ACC-55)/45)^2*该谱面的定数。
        
        cor.ENDLIST = {
        'score':1000000,
        'perfect':perfect,
        'maxcombo':maxcombo,
        'acc':1.00,
        'good':good,
        'bad':bad,
        'miss':miss,
        'early':0,
        'late':0,
        'level':cor.LEVEL,
        'name':cor.NAME,
        'username':'Guest',
        'rks':rks,
        }

        import ending
    else:
        pygame.quit()
        sys.exit()
        