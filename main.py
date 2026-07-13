from PIL import Image, ImageFilter, ImageEnhance
import core as cor
import pygame
import sys
import time
import data
import element
import alterobj
import tinytag
import pygame.freetype
import welcome as w

pygame.init()
print('Choosing UI.')

gamename = ''
while not gamename:
    try:
        gamename = w.choose()
        try:
            data.load_zip(f'preset/{gamename}.zip')
        except FileNotFoundError:
            data.load_zip(f'userCharts/{gamename}.zip')
        print(f'Loading Chart {gamename}.')
    except Exception as e:
        print(f'加载谱面失败: {e}')
        print('请选择其他谱面。')
        gamename = ''

w.loading()
print('Loading UI.')

# ---------- PYGAME INIT ----------
pygame.mixer.init()
pygame.mixer.music.load(cor.SONG)
pygame.freetype.init()
pygame.font.init()

# 背景图像
pil_blurred = Image.open(cor.IMAGE).filter(ImageFilter.GaussianBlur(radius=15))
brightEnhancer = ImageEnhance.Brightness(pil_blurred)
img = brightEnhancer.enhance(0.5)
img.convert("RGB").save("./cache/bg_b_b.jpg", quality=75)
background = pygame.transform.smoothscale(pygame.image.load("./cache/bg_b_b.jpg"), (cor.WIDTH, cor.HEIGHT))

# ---------- FONT (改进渲染) ----------
fonts_ok = True
try:
    f1 = pygame.freetype.Font(r"resources/cmdysj.ttf", 12)
    f1.antialiased = True
    f1.kerning = True
    f2 = pygame.freetype.Font(r"resources/Saira-Medium.ttf", 15)
    f2.antialiased = True
    f2.kerning = True
    f3 = pygame.freetype.Font(r"resources/Saira-Medium.ttf", 12)
    f3.antialiased = True
    
    font1 = pygame.font.Font(r"resources/cmdysj.ttf", 14)
    font2 = pygame.font.Font(r"resources/Saira-Medium.ttf", 30)
    font25 = pygame.font.Font("resources/cmdysj.ttf", 25)
    font_score = pygame.font.Font("resources/Saira-Medium.ttf", 28)
except FileNotFoundError:
    print('\n字体缺失\n')
    fonts_ok = False

# 窗口
screen = pygame.display.set_mode((cor.WIDTH, cor.HEIGHT), vsync=True)
surface = pygame.Surface((cor.WIDTH, cor.HEIGHT), pygame.SRCALPHA)
pygame.display.set_caption(cor.TITLE)
clock = pygame.time.Clock()

# UI纹理
songsNameBar = pause = None
try:
    songsNameBar = pygame.transform.scale(
        pygame.image.load("resources/texture/SongsNameBar.png").convert_alpha(), (4, 21))
    pause = pygame.transform.scale(
        pygame.image.load("resources/texture/Pause.png").convert_alpha(), (20, 20))
except FileNotFoundError:
    pass

# ---------- GAME ----------
FPS = 60
cor.OFFSET -= 175
note_num = 0
duration = tinytag.TinyTag.get(cor.SONG).duration
evalPainter = element.EvalPainter()

if cor.NOTE_NUM == 0:
    cor.NOTE_NUM = 1

# 启动音乐
pygame.mixer.music.play()
pygame.mixer.music.set_volume(0.5)
start_time_sec = 0.0  # 音乐开始的时刻
trueend = False
maxcombo = 0
perfect = 0
good = bad = miss = 0

try:
    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.scancode == 82: cor.DEBUG_K += 0.05
                elif event.scancode == 81: cor.DEBUG_K -= 0.05
                elif event.scancode == 79: cor.DEBUG_N += 0.05
                elif event.scancode == 80: cor.DEBUG_N -= 0.05
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    pos = pygame.mouse.get_pos()
                    if pause and 19 <= pos[0] <= 39 and 20 <= pos[1] <= 40:
                        trueend = False
                        pygame.quit()
                        sys.exit(0)

        # 当前时间（秒，含偏移）
        current_sec = (pygame.mixer.music.get_pos() / 1000) - cor.OFFSET / 1000
        
        # 转换到 beat（用于事件插值）
        beat = alterobj.s2b(max(0, current_sec))

        if current_sec < -2:
            continue

        # 绘制背景
        screen.blit(background, (0, 0))
        surface.fill((0, 0, 0, 0))

        # 进度条
        music_pos = pygame.mixer.music.get_pos() / 1000
        progress = music_pos / duration if duration > 0 else 0
        pygame.draw.rect(screen, (200, 200, 200), ((0, 0), (progress * cor.WIDTH, 8)))

        if not pygame.mixer.music.get_busy() and music_pos > 0:
            trueend = True
            break

        # ---- 绘制判定线和 Note ----
        for jl in cor.judge_line_list:
            jl.blit(surface, beat, current_sec)

            # 判定已到时间的 Tap/Drag/Flick
            done = []
            for note in jl.not_holds:
                if note.time <= current_sec:
                    done.append(note)
                else:
                    break
            for n in done:
                jl.not_holds.remove(n)
                if n in jl.above1: jl.above1.remove(n)
                else: jl.above2.remove(n)
                if not n.fake:
                    evalPainter.add_note(n, cor.Eval.PERFECT)
                    if cor.ENABLE_SOUND:
                        if n.id == element.Note.TAP: cor.TAP_SOUND.play()
                        elif n.id == element.Note.DRAG: cor.DRAG_SOUND.play()
                        elif n.id == element.Note.FLICK: cor.FLICK_SOUND.play()
                    note_num += 1
                    perfect += 1

            # 判定 Hold
            done = []
            for note in jl.holds:
                if note.end <= current_sec:
                    done.append(note)
                if note.time <= current_sec and (time.time() - note.last_eval_time >= 0.2):
                    if not note.fake:
                        if note.last_eval_time == -1 and cor.ENABLE_SOUND:
                            cor.TAP_SOUND.play()
                        evalPainter.add_note(note, cor.Eval.PERFECT)
                    note.last_eval_time = time.time()
            for n in done:
                jl.holds.remove(n)
                if n in jl.above1: jl.above1.remove(n)
                else: jl.above2.remove(n)
                if not n.fake:
                    note_num += 1
                    perfect += 1

        # 判定特效
        evalPainter.blit(surface)

        # ---- UI ----
        if note_num > maxcombo: maxcombo = note_num

        if fonts_ok and note_num >= 3:
            combo_t = font1.render("COMBO", True, (255, 255, 255))
            combo_n = font2.render(str(note_num), True, (255, 255, 255))
            cx = cor.WIDTH / 2 - font1.size("COMBO")[0] / 2 + 2.5
            cy = cor.WIDTH / 2 - font25.size(str(note_num))[0] / 2
            # 阴影
            shadow = font2.render(str(note_num), True, (0,0,0))
            shadow.set_alpha(120)
            surface.blit(shadow, (cy+2, 5))
            surface.blit(combo_t, (cx, 42))
            surface.blit(combo_n, (cy, 3))

        if pause:
            surface.blit(pause, (20, 21))
        if songsNameBar:
            surface.blit(songsNameBar, (20, 500))

        if fonts_ok:
            # 歌曲名称 + 等级（带阴影）
            f2.render_to(screen, [31, 504], cor.NAME, fgcolor=(0,0,0,80), size=21)
            f2.render_to(screen, [30, 503], cor.NAME, fgcolor=(255, 255, 255), size=21)
            f1.render_to(screen, [871, 508], cor.LEVEL, fgcolor=(0,0,0,80), size=18)
            f1.render_to(screen, [870, 507], cor.LEVEL, fgcolor=(255, 255, 255), size=18)
            
            # 分数（带阴影）
            score_str = str(int(note_num / cor.NOTE_NUM * 1000000)).rjust(7, "0")
            sw = font_score.size(score_str)[0]
            f1.render_to(screen, [cor.WIDTH - sw - 19, 24], score_str, fgcolor=(0,0,0,80), size=28)
            f1.render_to(screen, [cor.WIDTH - sw - 20, 23], score_str, fgcolor=(255, 255, 255), size=28)
            
            # FPS
            f1.render_to(screen, [0, 8], str(int(clock.get_fps())).rjust(3, "0"), fgcolor=(255, 255, 255), size=12)

        screen.blit(surface, (0, 0))
        pygame.display.flip()
        clock.tick(FPS)

except BaseException as b:
    import traceback
    traceback.print_exc()
finally:
    if trueend:
        acc_ = perfect / max(note_num, 1)
        rks = ((100 * float(acc_) - 55) / 45) ** 2.0 * float(cor.getnum_str(cor.LEVEL)) if acc_ >= 0.7 else 0
        cor.ENDLIST = {
            'score': 1000000, 'perfect': perfect, 'maxcombo': note_num,
            'acc': acc_, 'good': good, 'bad': bad, 'miss': miss,
            'early': 0, 'late': 0, 'level': cor.LEVEL, 'name': cor.NAME,
            'username': 'Guest', 'rks': rks,
        }
        import ending
    else:
        pygame.quit()
        sys.exit()
