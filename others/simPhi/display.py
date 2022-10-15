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

pygame.init()
gamename = w.choose()#选择界面
data.load_zip("others/sim-phi_pyphi/simPhi/preset/{}.zip".format(gamename))
w.loading()# 加载界面

# ---------- PYGAME INIT ----------
# 初始化音频
pygame.mixer.init()
pygame.mixer.music.load(cor.SONG)
pygame.freetype.init()
pygame.font.init()

# 初始化图像
pil_blurred = Image.open(cor.IMAGE).filter(ImageFilter.GaussianBlur(radius=15))
brightEnhancer = ImageEnhance.Brightness(pil_blurred)
img = brightEnhancer.enhance(0.5)
img.convert("RGB").save("./cache/bg_b_b.jpg", quality=75)
# convert it back to a pygame surface
background = pygame.transform.smoothscale(pygame.image.load("./cache/bg_b_b.jpg"),(cor.WIDTH, cor.HEIGHT))


# 初始化字体
f1      = pygame.freetype.Font(r"src/Exo-Regular.pfb.ttf", 12)
f2      = pygame.freetype.Font(r"src/Saira-Medium.ttf", 15)
font1   = pygame.font.Font(r"src/Exo-Regular.pfb.ttf", 14)
font2   = pygame.font.Font(r"src/Saira-Medium.ttf", 30)
font40  = pygame.font.Font("others/sim-phi_pyphi/simPhi/resources/cmdysj.ttf", 40)
font30  = pygame.font.Font("others/sim-phi_pyphi/simPhi/resources/cmdysj.ttf", 30)
font25  = pygame.font.Font("others/sim-phi_pyphi/simPhi/resources/cmdysj.ttf", 25)
font20  = pygame.font.Font("others/sim-phi_pyphi/simPhi/resources/cmdysj.ttf", 20)


# 初始化界面
screen = pygame.display.set_mode((cor.WIDTH, cor.HEIGHT), vsync=True)
surface = pygame.Surface((cor.WIDTH, cor.HEIGHT), pygame.SRCALPHA)
pygame.display.set_caption("Phigros for Python Max")

# 初始化时钟
clock = pygame.time.Clock()

# ---------- PYGAME INIT ----------
songsNameBar = pygame.image.load("others/sim-phi_pyphi/simPhi/resources/texture/SongsNameBar.png").convert_alpha()  # 歌曲名条
pause = pygame.image.load("others/sim-phi_pyphi/simPhi/resources/texture/Pause.png").convert_alpha()  # 暂停
# ---------- GAME INIT ----------
fps = 180
skip = 0
beat = cor.BeatObject.get_value(skip/60)
cor.OFFSET -= 175
note_num = 0
duration = tinytag.TinyTag.get(cor.SONG).duration

elementPainter = element.ElementPainter()
evalPainter = element.EvalPainter()

if cor.NOTE_NUM == 0:
    cor.NOTE_NUM = 1
    note_num = 1


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

# ---------- GAME INIT ----------
songsNameBar = pygame.transform.scale(songsNameBar, (4, 21))  # 歌曲名条调整大小
pause = pygame.transform.scale(pause, (20, 20))  # 暂停按钮调整大小
# ---------- GAME START ----------

pygame.mixer.music.play(start=skip)
start = time.time()
beat = cor.BeatObject.get_value((time.time()-start+skip-cor.OFFSET/1000)/60)

# ---------- GAME START ----------


while 1:
    # ---------- EVENT RESPOND ----------

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

    # elementPainter.paint(surface, beat)

    evalPainter.blit(surface)

    # ---------- DISPLAY ELEMENTS ----------

    # ---------- DISPLAY TEXTS ----------

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
