from PIL import Image, ImageFilter, ImageEnhance
import core
import pygame
import sys
import time
import data
import easing
import element
import tinytag

pygame.init()

data.load_beatmap("../downloaded_beatmap/Party in the HOLLOWood.zip")

# ---------- PYGAME INIT ----------
# 初始化音频
pygame.mixer.init()
pygame.mixer.music.load(core.SONG)

# 初始化图像
pil_blurred = Image.open(core.IMAGE).filter(ImageFilter.GaussianBlur(radius=25))
brightEnhancer = ImageEnhance.Brightness(pil_blurred)
img = brightEnhancer.enhance(0.5)
img.convert("RGB").save("./cache/bg_b_b.jpg", quality=75)
# convert it back to a pygame surface
background = pygame.transform.smoothscale(pygame.image.load("./cache/bg_b_b.jpg"),
                                          (core.WIDTH, core.HEIGHT))

# 初始化字体
font40 = pygame.font.Font("./resources/cmdysj.ttf", 40)
font30 = pygame.font.Font("./resources/cmdysj.ttf", 30)
font25 = pygame.font.Font("./resources/cmdysj.ttf", 25)
font20 = pygame.font.Font("./resources/cmdysj.ttf", 20)

name_text = font25.render("| " + core.NAME, True, (255, 255, 255))
level_text = font25.render(core.LEVEL, True, (255, 255, 255))
copyright_text = font20.render("SimPhi Project - Code by xi2p", True, (200, 200, 200))

# 初始化界面
screen = pygame.display.set_mode((core.WIDTH, core.HEIGHT))
surface = pygame.Surface((core.WIDTH, core.HEIGHT), pygame.SRCALPHA)
pygame.display.set_caption("SimPhi v1.1.0 - Code by xi2p")

# 初始化时钟
clock = pygame.time.Clock()

# ---------- PYGAME INIT ----------

# ---------- GAME INIT ----------

skip = 0
beat = core.BeatObject.get_value(skip / 60)
core.OFFSET -= 175
note_num = 0
duration = tinytag.TinyTag.get(core.SONG).duration

elementPainter = element.ElementPainter()
evalPainter = element.EvalPainter()

if core.NOTE_NUM == 0:
    core.NOTE_NUM = 1
    note_num = 1

for jl in core.judge_line_list:

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

# ---------- GAME SCENE ----------

PREPARE = 0
PLAYING = 1
END_1 = 2
END_2 = 3
scene = PREPARE

# ---------- GAME SECTION ----------

# ---------- GAME START ----------

start = time.time()
beat = core.BeatObject.get_value((pygame.mixer.music.get_pos() / 1000 + skip - core.OFFSET / 1000) / 60)

# ---------- GAME START ----------


while 1:
    if scene == PLAYING:
        # ---------- EVENT RESPOND ----------

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:

                if event.scancode == 82:
                    core.DEBUG_K += 0.05
                elif event.scancode == 81:
                    core.DEBUG_K -= 0.05
                elif event.scancode == 79:
                    core.DEBUG_N += 0.05
                elif event.scancode == 80:
                    core.DEBUG_N -= 0.05

                print(core.DEBUG_K, core.DEBUG_N)

        # ---------- EVENT RESPOND ----------

        # ---------- ESSENTIAL ----------
        if not pygame.mixer.music.get_busy():
            scene = END_1
            start = time.time()
            continue

        if beat < 0:
            beat = core.BeatObject.get_value((pygame.mixer.music.get_pos() / 1000 + skip - core.OFFSET / 1000) / 60)
            continue

        screen.blit(background, (0, 0))
        # screen.fill((50, 50, 50))
        surface.fill((0, 0, 0, 0))

        # 进度条
        pygame.draw.rect(screen, (200, 200, 200),
                         ((0, 0), ((pygame.mixer.music.get_pos() / 1000 + skip) / duration * core.WIDTH, 8)))

        # ---------- ESSENTIAL ----------

        # ---------- DISPLAY ELEMENTS ----------

        for jl in core.judge_line_list:
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
                    evalPainter.add_note(note, core.Eval.PERFECT)
                    if core.ENABLE_SOUND:
                        if note.id == element.Note.TAP:
                            core.TAP_SOUND.play()
                        elif note.id == element.Note.DRAG:
                            core.DRAG_SOUND.play()
                        elif note.id == element.Note.FLICK:
                            core.FLICK_SOUND.play()
                    note_num += 1

            note_bin = []
            for note in jl.holds:
                if note.end < beat:
                    note_bin.append(note)

                if note.at <= beat and (time.time() - note.last_eval_time >= 0.2):
                    if not note.fake:
                        if note.last_eval_time == -1:
                            if core.ENABLE_SOUND:
                                core.TAP_SOUND.play()
                        evalPainter.add_note(note, core.Eval.PERFECT)
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

        combo_text = font30.render("COMBO", True, (255, 255, 255))
        combo_num_text = font40.render(str(note_num), True, (255, 255, 255))
        score_text = font30.render(str(int(note_num / core.NOTE_NUM * 1000000)).rjust(7, '0'), True, (255, 255, 255))
        fps_text = font25.render(str(int(clock.get_fps())).rjust(3, "0"), True, (255, 255, 255))
        offset_text = font20.render(f"OFFSET={core.OFFSET}", True, (255, 255, 255))

        if note_num >= 3:
            surface.blit(combo_text, (core.WIDTH / 2 - combo_text.get_width() / 2, 40))
            surface.blit(combo_num_text, (core.WIDTH / 2 - combo_num_text.get_width() / 2, 0))

        surface.blit(score_text, (core.WIDTH - score_text.get_width(), 0))
        surface.blit(fps_text, (0, 0))
        surface.blit(offset_text, (0, fps_text.get_height()))

        surface.blit(name_text, (5,
                                 core.HEIGHT - name_text.get_height() - 5))

        surface.blit(level_text, (core.WIDTH - level_text.get_width() - 5,
                                  core.HEIGHT - level_text.get_height() - copyright_text.get_height() - 5))

        surface.blit(copyright_text, (core.WIDTH - copyright_text.get_width() - 5,
                                      core.HEIGHT - copyright_text.get_height() - 5))

        # ---------- DISPLAY TEXTS ----------

        # ---------- REFRESH ----------

        screen.blit(surface, (0, 0))
        pygame.display.flip()
        clock.tick(120)
        # beat = core.BeatObject.get_value(skip/60)
        beat = core.BeatObject.get_value((pygame.mixer.music.get_pos() / 1000 + skip - core.OFFSET / 1000) / 60)

        # ---------- REFRESH ----------

    elif scene == PREPARE:

        # ---------- EVENT RESPOND ----------

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)

        # ---------- EVENT RESPOND ----------

        # ---------- ESSENTIAL ----------

        if time.time() - start > core.PREPARE_DURATION:
            scene = PLAYING
            surface.set_alpha(255)
            pygame.mixer.music.play(start=skip)
            continue

        screen.blit(background, (0, 0))
        # screen.fill((50, 50, 50))
        surface.fill((0, 0, 0, 0))

        # 进度条
        pygame.draw.rect(surface, (200, 200, 200),
                         (
                             (0,
                              core.HEIGHT / 2 - 3),
                             (
                                 (min(time.time() - start, 1)) * 8 / core.PREPARE_DURATION * core.WIDTH,
                                 6)
                         ))

        # ---------- ESSENTIAL ----------

        # ---------- DISPLAY TEXTS ----------
        passed = time.time() - start
        fade = 1
        if passed < fade:
            alpha = passed / fade * 255
        elif passed > core.PREPARE_DURATION - fade:
            alpha = (core.PREPARE_DURATION - passed) / fade * 255
        else:
            alpha = 255

        title_text = font40.render(core.NAME, True, (200, 200, 200))

        surface.blit(title_text, (core.WIDTH / 2 - title_text.get_width() / 2,
                                  core.HEIGHT / 2 - title_text.get_height() / 2 - 50))

        surface.blit(copyright_text, (core.WIDTH - copyright_text.get_width() - 5,
                                      core.HEIGHT - copyright_text.get_height() - 5))

        surface.set_alpha(alpha)

        # ---------- DISPLAY TEXTS ----------

        # ---------- REFRESH ----------

        screen.blit(surface, (0, 0))
        pygame.display.flip()
        clock.tick(120)

        # ---------- REFRESH ----------

    elif scene == END_1:

        # ---------- EVENT RESPOND ----------

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)

        # ---------- EVENT RESPOND ----------

        # ---------- ESSENTIAL ----------

        if time.time() - start > core.END_DURATION_1:
            scene = END_2
            background_clear = pygame.transform.smoothscale(pygame.image.load(core.IMAGE),
                                                            (core.WIDTH*0.4, core.HEIGHT*0.5))
            t2x = easing.code2FuncDict[4](0, core.END_DURATION_2, core.WIDTH/2, 0)
            phi_image = pygame.image.load("./resources/texture/phi.png")
            score_text = font40.render("1000000", True, (255, 255, 255))

            perfect_text = font20.render("Perfect", True, (255, 255, 255))
            good_text = font20.render("Good", True, (255, 255, 255))
            bad_text = font20.render("Bad", True, (255, 255, 255))
            miss_text = font20.render("Miss", True, (255, 255, 255))

            perfect_num_text = font20.render(f"{note_num}", True, (255, 255, 255))
            good_num_text = font20.render("0", True, (255, 255, 255))
            bad_num_text = font20.render("0", True, (255, 255, 255))
            miss_num_text = font20.render("0", True, (255, 255, 255))

            pygame.mixer.music.load("./resources/audio/GameOver.wav")
            pygame.mixer.music.play(-1, fade_ms=200)
            start = time.time()
            continue

        screen.blit(background, (0, 0))
        # screen.fill((50, 50, 50))
        surface.fill((0, 0, 0, 0))

        # ---------- ESSENTIAL ----------

        # ---------- DISPLAY TEXTS ----------

        passed = time.time() - start
        delta_y = 90 * passed / 1

        combo_text = font30.render("COMBO", True, (255, 255, 255))
        combo_num_text = font40.render(str(note_num), True, (255, 255, 255))
        score_text = font30.render(str(int(note_num / core.NOTE_NUM * 1000000)).rjust(7, '0'), True, (255, 255, 255))
        fps_text = font25.render(str(int(clock.get_fps())).rjust(3, "0"), True, (255, 255, 255))
        offset_text = font20.render(f"OFFSET={core.OFFSET}", True, (255, 255, 255))

        if note_num >= 3:
            surface.blit(combo_text, (core.WIDTH / 2 - combo_text.get_width() / 2, 40 - delta_y))
            surface.blit(combo_num_text, (core.WIDTH / 2 - combo_num_text.get_width() / 2, 0 - delta_y))

        surface.blit(score_text, (core.WIDTH - score_text.get_width(), 0 - delta_y))
        surface.blit(fps_text, (0, 0 - delta_y))
        surface.blit(offset_text, (0, fps_text.get_height() - delta_y))

        surface.blit(name_text, (5,
                                 core.HEIGHT - name_text.get_height() - 5 + delta_y))

        surface.blit(level_text, (core.WIDTH - level_text.get_width() - 5,
                                  core.HEIGHT - level_text.get_height() - copyright_text.get_height() - 5 + delta_y))

        surface.blit(copyright_text, (core.WIDTH - copyright_text.get_width() - 5,
                                      core.HEIGHT - copyright_text.get_height() - 5 + delta_y))

        # ---------- DISPLAY TEXTS ----------

        # ---------- REFRESH ----------

        screen.blit(surface, (0, 0))
        pygame.display.flip()
        clock.tick(120)

        # ---------- REFRESH ----------

    elif scene == END_2:

        # ---------- EVENT RESPOND ----------

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)

        # ---------- EVENT RESPOND ----------

        # ---------- ESSENTIAL ----------

        screen.blit(background, (0, 0))
        # screen.fill((50, 50, 50))
        surface.fill((0, 0, 0, 0))

        # ---------- ESSENTIAL ----------

        # ---------- DISPLAY ----------

        passed = time.time() - start
        if passed > core.END_DURATION_2:
            passed = core.END_DURATION_2

        delta_x = t2x.calculate(passed)

        # 左半边
        pygame.draw.rect(surface, (32, 32, 32, 225), (
            core.WIDTH * 0.05 - delta_x - 5, core.HEIGHT * 0.15 - 5,
            core.WIDTH * 0.4 + 10, core.HEIGHT * 0.5 + 10,
        ))
        surface.blit(background_clear, (core.WIDTH*0.05 - delta_x, core.HEIGHT*0.15))

        # 右半边
        pygame.draw.rect(surface, (32, 32, 32, 225), (
            core.WIDTH * 0.55 + delta_x - 5, core.HEIGHT * 0.15 - 5,
            core.WIDTH * 0.4 + 10, core.HEIGHT * 0.3 + 10,
        ))

        pygame.draw.rect(surface, (32, 32, 32, 225), (
            core.WIDTH * 0.55 + delta_x - 5, core.HEIGHT * 0.5 - 5,
            core.WIDTH * 0.4 + 10, core.HEIGHT * 0.15 + 10,
        ))

        surface.blit(phi_image, (
            core.WIDTH * 0.57 + delta_x - 5, core.HEIGHT * 0.3 - 5 - phi_image.get_height() / 2
        ))

        surface.blit(score_text, (
            core.WIDTH * 0.57 + delta_x + 8 + phi_image.get_width(), core.HEIGHT * 0.3 - 5 - score_text.get_height() / 2
        ))

        surface.blit(perfect_text, (
            core.WIDTH * 0.55 + delta_x - 5 - 10 + (core.WIDTH * 0.4 + 10) * 0.2 - perfect_text.get_width() / 2,
            core.HEIGHT * 0.545 - 5 - perfect_text.get_height() / 2
        ))

        surface.blit(good_text, (
            core.WIDTH * 0.55 + delta_x - 5 + (core.WIDTH * 0.4 + 10) * 0.4 - good_text.get_width() / 2,
            core.HEIGHT * 0.545 - 5 - good_text.get_height() / 2
        ))

        surface.blit(bad_text, (
            core.WIDTH * 0.55 + delta_x - 5 + (core.WIDTH * 0.4 + 10) * 0.6 - bad_text.get_width() / 2,
            core.HEIGHT * 0.545 - 5 - bad_text.get_height() / 2
        ))

        surface.blit(miss_text, (
            core.WIDTH * 0.55 + delta_x - 5 + (core.WIDTH * 0.4 + 10) * 0.8 - miss_text.get_width() / 2,
            core.HEIGHT * 0.545 - 5 - miss_text.get_height() / 2
        ))

        surface.blit(perfect_num_text, (
            core.WIDTH * 0.55 + delta_x - 5 - 10 + (core.WIDTH * 0.4 + 10) * 0.2 - perfect_num_text.get_width() / 2,
            core.HEIGHT * 0.615 - 5 - perfect_num_text.get_height() / 2
        ))

        surface.blit(good_num_text, (
            core.WIDTH * 0.55 + delta_x - 5 + (core.WIDTH * 0.4 + 10) * 0.4 - good_num_text.get_width() / 2,
            core.HEIGHT * 0.615 - 5 - good_num_text.get_height() / 2
        ))

        surface.blit(bad_num_text, (
            core.WIDTH * 0.55 + delta_x - 5 + (core.WIDTH * 0.4 + 10) * 0.6 - bad_num_text.get_width() / 2,
            core.HEIGHT * 0.615 - 5 - bad_num_text.get_height() / 2
        ))

        surface.blit(miss_num_text, (
            core.WIDTH * 0.55 + delta_x - 5 + (core.WIDTH * 0.4 + 10) * 0.8 - miss_num_text.get_width() / 2,
            core.HEIGHT * 0.615 - 5 - miss_num_text.get_height() / 2
        ))

        title_text = font30.render(core.NAME, True, (200, 200, 200))
        surface.blit(title_text, (
            core.WIDTH*0.05 - delta_x, core.HEIGHT*0.73
        ))

        level_text = font25.render(core.LEVEL, True, (200, 200, 200))
        surface.blit(level_text, (
            core.WIDTH*0.05 - delta_x, core.HEIGHT*0.73 + level_text.get_height() + 10
        ))

        surface.blit(copyright_text, (core.WIDTH - copyright_text.get_width() - 5,
                                      core.HEIGHT - copyright_text.get_height() - 5))

        surface.set_alpha(200)
        # ---------- DISPLAY ----------

        # ---------- REFRESH ----------

        screen.blit(surface, (0, 0))
        pygame.display.flip()
        clock.tick(120)

        # ---------- REFRESH ----------
