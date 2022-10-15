import time
import typing as T
import pygame.surface
import math
import alterobj
import core as cor
import threading
import debug


class JudgeLine:
    # 欺骗指数。用于暂时解决note出现在屏幕外就中断整个判定线的绘制的问题
    CHEAT_INDICATOR = 1

    # 判定线
    def __init__(self):
        """
        初始化判定线
        """
        self.x = 0
        self.y = 0
        self.angle = 0
        self.alpha = 0
        self.speed = 0
        self.id = -1
        self.lastbeat=0
        self.x_object: T.Union[alterobj.LineXObject, None] = None
        self.y_object: T.Union[alterobj.LineYObject, None] = None
        self.alpha_object: T.Union[alterobj.AlphaObject, None] = None
        self.angle_object: T.Union[alterobj.AngleObject, None] = None
        self.speed_object: T.Union[alterobj.LineSpeedObject, None] = None
        self.note_y_object: T.Union[alterobj.NoteYObject, None] = None
        # if self.speed_object:
        #     self.notes_y_object = self.speed_object.get_y_object()
        # else:
        #     self.notes_y_object = alterobj.FakeNoteYObject(speed)
        self.notes = []

        self.holds = []
        self.not_holds = []
        self.above1 = []
        self.above2 = []
        self.floor_position=0

    def add_note(self, note):
        self.notes.append(note)

    def blit(self, surface: pygame.surface.Surface, beat: float):
        """
        将判定线本身绘制到surface上
        :param surface: 被绘制的Surface对象
        :param beat: beat
        """

        self.x = self.x_object.get_value(beat)
        self.y = self.y_object.get_value(beat)
        self.alpha = self.alpha_object.get_value(beat)
        self.angle = self.angle_object.get_value(beat)
        self.speed=self.speed_object.get_value(beat)
        self.floor_position+=alterobj.b2s(beat-self.lastbeat)
        points = self.get_points()

        if points and self.alpha:
            pygame.draw.line(surface, (237, 236, 176, self.alpha), points[0], points[1], width=5)

        debug.mark(surface, self.x, self.y, r=10)

        for note in self.above1:
            note.upgrade_and_blit(surface, beat)
            if note.x_in_surface > cor.WIDTH + cor.WIDTH * JudgeLine.CHEAT_INDICATOR or\
                    note.x_in_surface < 0 - cor.WIDTH * JudgeLine.CHEAT_INDICATOR or \
                    note.y_in_surface < 0 - cor.HEIGHT * JudgeLine.CHEAT_INDICATOR or\
                    note.y_in_surface > cor.HEIGHT + cor.HEIGHT * JudgeLine.CHEAT_INDICATOR:
                break

        for note in self.above2:
            note.upgrade_and_blit(surface, beat)
            if note.x_in_surface > cor.WIDTH + cor.WIDTH * JudgeLine.CHEAT_INDICATOR or\
                    note.x_in_surface < 0 - cor.WIDTH * JudgeLine.CHEAT_INDICATOR or \
                    note.y_in_surface < 0 - cor.HEIGHT * JudgeLine.CHEAT_INDICATOR or\
                    note.y_in_surface > cor.HEIGHT + cor.HEIGHT * JudgeLine.CHEAT_INDICATOR:
                break
        self.lastbeat=beat
    def get_points(self):
        # 此处除cross内坐标，都是将y轴向上视为y轴正方向
        # 交点
        _points = []

        _angle = self.angle % 180

        # 找出线段左右边界
        line_left = self.x + cor.LINE_LENGTH / 2 * math.cos(math.radians(_angle))
        line_right = self.x - cor.LINE_LENGTH / 2 * math.cos(math.radians(_angle))

        if line_left > line_right:
            line_left, line_right = line_right, line_left

        # 找出线段上下边界
        line_top = -self.y + cor.LINE_LENGTH / 2 * math.sin(math.radians(_angle))
        line_bottom = -self.y - cor.LINE_LENGTH / 2 * math.sin(math.radians(_angle))

        if line_top < line_bottom:
            line_top, line_bottom = line_bottom, line_top

        if _angle == 90:
            # 划定最小值域
            if 0 <= self.x <= cor.WIDTH:
                if line_top >= 0 >= line_bottom:
                    _points.append((self.x, 0))
                if line_top >= -cor.HEIGHT >= line_bottom:
                    _points.append((self.x, cor.HEIGHT))
        elif _angle == 0:
            if -cor.HEIGHT <= -self.y <= 0:
                if line_left <= 0 <= line_right:
                    _points.append((0, self.y))
                if line_left <= cor.WIDTH <= line_right:
                    _points.append((cor.WIDTH, self.y))
        else:
            # 先求斜率
            k = math.tan(math.radians(_angle))
            # 再求截距
            b = -self.y - self.x * k

            # 上方直线交点
            # y = kx + b, y = 0 => x = -b / k
            top_cross_x = -b / k

            # 下方直线交点
            # y = kx + b, y = HEIGHT => x = (-HEIGHT - b) / k
            bottom_cross_x = (-cor.HEIGHT - b) / k

            # 左侧直线交点
            right_cross_y = cor.WIDTH * k + b

            # 右侧直线交点
            left_cross_y = b

            if 0 <= top_cross_x <= cor.WIDTH:
                if line_top >= 0 >= line_bottom:
                    _points.append((top_cross_x, 0))
            if 0 <= bottom_cross_x <= cor.WIDTH:
                if line_top >= -cor.HEIGHT >= line_bottom:
                    _points.append((bottom_cross_x, cor.HEIGHT))
            if -cor.HEIGHT < left_cross_y < 0:
                if line_left <= 0 <= line_right:
                    _points.append((0, -left_cross_y))
            if -cor.HEIGHT < right_cross_y < 0:
                if line_left <= cor.WIDTH <= line_right:
                    _points.append((cor.WIDTH, -right_cross_y))

        if len(_points) == 1:
            # 只有一个交点，那么可能是线不够长
            # 上方端点在画面内
            if -cor.HEIGHT <= line_top <= 0 and \
                    0 <= (line_left if _angle > 90 else line_right) <= cor.WIDTH:
                point_x = (line_left if _angle > 90 else line_right)
                _points.append((point_x, -line_top))
            # 下方端点在画面内
            elif -cor.HEIGHT <= line_bottom <= 0 and \
                    0 <= (line_right if _angle > 90 else line_left) <= cor.WIDTH:
                point_x = line_right if _angle > 90 else line_left
                _points.append((point_x, -line_bottom))
            else:
                # 只是擦到一个角了，不用显示
                _points = []

        return _points


class Note:
    TAP = 1
    DRAG = 2
    FLICK = 3
    HOLD = 4

    # 所有音符的超类
    def __init__(self, judge_line, x=0, at=0, above=True, alpha=0, end=-1, fake=False,speed=1.0):
        """
        初始化音符
        :param x: 初始x坐标
        :param at: 打击时间
        :param above: 是否从判定线上方下落
        :param alpha: 透明度
        :param end: 如果Note是Hold，则本属性为结束打击时间
        :param fake: 真假Note
        """
        self.judge_line = judge_line
        self.x = x
        self.at = at
        self.end = end
        self.angle = 0 if above else 180
        self.above = above
        self.alpha = alpha
        self.fake = fake
        self.id = -1
        self.highlight = False  # 是否双押或表演(高光)
        self.y_in_surface = -1
        self.x_in_surface = -1
        self.speed=speed

    def upgrade(self, surface: pygame.surface.Surface, beat: float):
        """
        更新本Note的位置
        :param surface: 被绘制的Surface对象
        :param beat: beat
        """
        judge_line = self.judge_line
        if beat > self.at:
            beat = self.at
        _y = (alterobj.b2s(self.at)-(judge_line.floor_position))* cor.DEBUG_N*self.speed*800
        # _y = 0
        _x = self.x * cor.DEBUG_K
        r = (_x ** 2 + _y ** 2) ** 0.5
        if _x > 0:
            angle = judge_line.angle + math.degrees(math.atan(_y / _x))
        elif _x < 0:
            angle = judge_line.angle + math.degrees(math.atan(_y / _x)) + 180
        else:
            angle = judge_line.angle + (90 if _y >= 0 else - 90)
        #x = r * math.cos(math.radians(angle)) * (1 if self.above else -1) + judge_line.x
        x = r * math.cos(math.radians(angle)) * 1 + judge_line.x
        y = r * math.sin(math.radians(angle)) * (-1 if self.above else 1) + judge_line.y

        self.x_in_surface = x
        self.y_in_surface = y

    def blit(self, surface):
        x = self.x_in_surface
        y = self.y_in_surface
        angle = self.judge_line.angle
        alpha = self.alpha

        if not (x < 0 or x > cor.WIDTH or y < 0 or y > cor.HEIGHT):
            self.draw_at(surface, x, y, angle, alpha)
            debug.mark(surface, x, y, color=(200, 50, 50), r=5)

    def upgrade_and_blit(self, surface: pygame.surface.Surface, beat: float):
        self.upgrade(surface, beat)
        self.blit(surface)

    @classmethod
    def draw_at_(cls, surface, x, y, angle, color, highlight):
        color_ = (
            min(color[0] + (64 if highlight else 0), 255),
            min(color[1] + (64 if highlight else 0), 255),
            min(color[2], 255)
        )
        pygame.draw.polygon(surface, color_, [
            (x + cor.NOTE_R * math.cos(math.radians(angle + cor.NOTE_THETA)),
             y - cor.NOTE_R * math.sin(math.radians(angle + cor.NOTE_THETA))),
            (x + cor.NOTE_R * math.cos(math.radians(angle + 180 - cor.NOTE_THETA)),
             y - cor.NOTE_R * math.sin(math.radians(angle + 180 - cor.NOTE_THETA))),
            (x + cor.NOTE_R * math.cos(math.radians(angle - 180 + cor.NOTE_THETA)),
             y - cor.NOTE_R * math.sin(math.radians(angle - 180 + cor.NOTE_THETA))),
            (x + cor.NOTE_R * math.cos(math.radians(angle - cor.NOTE_THETA)),
             y - cor.NOTE_R * math.sin(math.radians(angle - cor.NOTE_THETA))),
        ])

    def draw_at(self, surface, x, y, angle, alpha):
        pass


class Tap(Note):
    # 所有音符的超类
    def __init__(self, judge_line, x=0, at=0, above=True, alpha=0, end=-1, fake=False,speed=1.0):
        super().__init__(judge_line, x, at, above, alpha, end, fake,speed)
        self.id = Note.TAP

    def draw_at(self, surface, x, y, angle, alpha):
        Note.draw_at_(surface, x, y, angle, (10, 180, 240, alpha), self.highlight)


class Drag(Note):
    # 所有音符的超类
    def __init__(self, judge_line, x=0, at=0, above=True, alpha=0, end=-1, fake=False,speed=1.0):
        super().__init__(judge_line, x, at, above, alpha, end, fake,speed)
        self.id = Note.DRAG

    def draw_at(self, surface, x, y, angle, alpha):
        Note.draw_at_(surface, x, y, angle, (211, 211, 105, alpha), self.highlight)
        # Note.draw_at_(surface, x, y, angle, (240, 237, 105, alpha), self.highlight)


class Flick(Note):
    # 所有音符的超类
    def __init__(self, judge_line, x=0, at=0, above=True, alpha=0, end=-1, fake=False,speed=1.0):
        super().__init__(judge_line, x, at, above, alpha, end, fake,speed)
        self.id = Note.FLICK

    def draw_at(self, surface, x, y, angle, alpha):
        Note.draw_at_(surface, x, y, angle, (191, 40, 110, alpha), self.highlight)
        # Note.draw_at_(surface, x, y, angle, (254, 88, 118, alpha), self.highlight)


class Hold(Note):
    # 所有音符的超类
    def __init__(self, judge_line, x=0, at=0, above=True, alpha=0, end=-1, fake=False,speed=1.0):
        super().__init__(judge_line, x, at, above, alpha, end, fake,speed)
        self.id = Note.HOLD
        self.duration = self.end - self.at
        self.last_eval_time = -1
        self.length = 0

    def upgrade(self, surface: pygame.surface.Surface, beat: float):
        """
        将判定线本身及Note绘制到surface上
        :param surface: 被绘制的Surface对象
        :param beat: beat
        """
        judge_line = self.judge_line
        if beat > self.end:
            beat = self.end
        full_length = judge_line.note_y_object.get_value(self.at, self.end)*self.speed*judge_line.speed/6

        if beat < self.at:
            length = full_length
            _y = judge_line.note_y_object.get_value(beat, self.at) * (
                1 if self.above else -1
            )
        else:
            length = full_length * (self.end - beat) / self.duration
            _y = 0

        _y = _y * cor.DEBUG_N*judge_line.speed/6

        r = (self.x ** 2 + _y ** 2) ** 0.5
        if self.x > 0:
            angle = judge_line.angle + math.degrees(math.atan(_y / self.x))
        elif self.x < 0:
            angle = judge_line.angle + math.degrees(math.atan(_y / self.x)) + 180
        else:
            angle = judge_line.angle + (90 if _y >= 0 else - 90)
        x = r * math.cos(math.radians(angle)) + judge_line.x
        y = -r * math.sin(math.radians(angle)) + judge_line.y

        self.x_in_surface = x
        self.y_in_surface = y

        if self.y_in_surface < 0 or self.y_in_surface > cor.HEIGHT or \
                self.x_in_surface < 0 or self.x_in_surface > cor.WIDTH:
            return 0
        self.length = length

    def blit(self, surface):
        length = self.length
        judge_line = self.judge_line
        x = self.x_in_surface
        y = self.y_in_surface

        length = length if self.above else -length
        # p1, p2 = Hold.get_points(x, y, length, judge_line.angle + (90 if self.above else -90))
        # length = ((p1[0]-p2[0]) ** 2 + (p1[1]-p2[1]) ** 2) ** 0.5

        _angle = math.degrees(math.atan(length / (cor.BAR_WIDTH / 2) * 2))
        _angle1 = math.radians(judge_line.angle + _angle)
        _angle2 = math.radians(180 + judge_line.angle - _angle)

        r = (length ** 2 + ((cor.BAR_WIDTH / 2) / 2) ** 2) ** 0.5
        pygame.draw.polygon(surface,
                            (10 + (32 if self.highlight else 0),
                             195 + (32 if self.highlight else 0),
                             255,
                             self.alpha * 0.8), [
                                (x + (cor.BAR_WIDTH / 2) / 2 * math.cos(math.radians(judge_line.angle)),
                                 y - (cor.BAR_WIDTH / 2) / 2 * math.sin(math.radians(judge_line.angle))),
                                (x - (cor.BAR_WIDTH / 2) / 2 * math.cos(math.radians(judge_line.angle)),
                                 y + (cor.BAR_WIDTH / 2) / 2 * math.sin(math.radians(judge_line.angle))),
                                (x + r * math.cos(_angle2),
                                 y - r * math.sin(_angle2)),
                                (x + r * math.cos(_angle1),
                                 y - r * math.sin(_angle1)),

                            ])
        # r = (length ** 2 + (core.NOTE_WIDTH / 2) ** 2) ** 0.5
        # pygame.draw.line(surface,
        #                  (10 + (32 if self.highlight else 0), 195 + (32 if self.highlight else 0), 255,
        #                   self.alpha * 0.8),
        #                  (x, y),
        #                  (x + (r * math.cos(_angle2) + r * math.cos(_angle1)) / 2,
        #                   y - (r * math.sin(_angle2) + r * math.sin(_angle1)) / 2),
        #                  width=14)

        # pygame.draw.circle(surface,
        #                    (10 + (32 if self.highlight else 0), 195 + (32 if self.highlight else 0), 255,
        #                     self.alpha * 0.8),
        #                    (x + (r * math.cos(_angle2) + r * math.cos(_angle1)) / 2,
        #                     y - (r * math.sin(_angle2) + r * math.sin(_angle1)) / 2),
        #                    8)

        _angle = math.degrees(math.atan(length / cor.NOTE_WIDTH * 2))
        _angle1 = math.radians(judge_line.angle + _angle)
        _angle2 = math.radians(180 + judge_line.angle - _angle)

        angle = judge_line.angle
        pygame.draw.polygon(surface, (10 + (32 if self.highlight else 0),
                                      195 + (32 if self.highlight else 0),
                                      255,
                                      self.alpha * 0.8), [
                                (x + cor.NOTE_R * math.cos(math.radians(angle + cor.NOTE_THETA)),
                                 y - cor.NOTE_R * math.sin(math.radians(angle + cor.NOTE_THETA))),
                                (x + cor.NOTE_R * math.cos(math.radians(angle + 180 - cor.NOTE_THETA)),
                                 y - cor.NOTE_R * math.sin(math.radians(angle + 180 - cor.NOTE_THETA))),
                                (x + cor.NOTE_R * math.cos(math.radians(angle - 180 + cor.NOTE_THETA)),
                                 y - cor.NOTE_R * math.sin(math.radians(angle - 180 + cor.NOTE_THETA))),
                                (x + cor.NOTE_R * math.cos(math.radians(angle - cor.NOTE_THETA)),
                                 y - cor.NOTE_R * math.sin(math.radians(angle - cor.NOTE_THETA))),
                            ])
        debug.mark(surface, x, y, color=(200, 50, 50), r=5)
        # length = 12
        # _angle = math.degrees(math.atan(length / core.NOTE_WIDTH * 2))
        # _angle1 = math.radians(judge_line.angle + _angle)
        # _angle2 = math.radians(180 + judge_line.angle - _angle)
        # r = (length ** 2 + (core.NOTE_WIDTH / 2) ** 2) ** 0.5
        # pygame.draw.polygon(surface,
        #                     (10 + (32 if self.highlight else 0),
        #                      195 + (32 if self.highlight else 0),
        #                      255,
        #                      self.alpha * 0.8), [
        #                         (x + core.NOTE_WIDTH / 2 * math.cos(math.radians(judge_line.angle)),
        #                          y - core.NOTE_WIDTH / 2 * math.sin(math.radians(judge_line.angle))),
        #                         (x - core.NOTE_WIDTH / 2 * math.cos(math.radians(judge_line.angle)),
        #                          y + core.NOTE_WIDTH / 2 * math.sin(math.radians(judge_line.angle))),
        #                         (x + r * math.cos(_angle2),
        #                          y - r * math.sin(_angle2)),
        #                         (x + r * math.cos(_angle1),
        #                          y - r * math.sin(_angle1)),
        #
        #                     ])

    def upgrade_and_blit(self, surface: pygame.surface.Surface, beat: float):
        self.upgrade(surface, beat)
        self.blit(surface)

    @classmethod
    def get_points(cls, x, y, length, angle):
        # 此处除cross内坐标，都是将y轴向上视为y轴正方向
        # 交点
        _points = []

        _angle = angle % 360

        # 找出线段左右边界
        line_left = x + length / 2 * math.cos(math.radians(_angle))
        line_right = x - length / 2 * math.cos(math.radians(_angle))

        if line_left > line_right:
            line_left, line_right = line_right, line_left

        # 找出线段上下边界
        line_top = -y + length / 2 * math.sin(math.radians(_angle))
        line_bottom = -y - length / 2 * math.sin(math.radians(_angle))

        if line_top < line_bottom:
            line_top, line_bottom = line_bottom, line_top

        if _angle == 90:
            # 划定最小值域
            if 0 <= x <= cor.WIDTH:

                if line_top >= 0 >= line_bottom:
                    _points.append((x, 0))
                if line_top >= -cor.HEIGHT >= line_bottom:
                    _points.append((x, cor.HEIGHT))
        elif _angle == 0:
            if -cor.HEIGHT <= -y <= 0:
                if line_left <= 0 <= line_right:
                    _points.append((0, y))
                if line_left <= cor.WIDTH <= line_right:
                    _points.append((cor.WIDTH, y))
        else:
            # 先求斜率
            k = math.tan(math.radians(_angle))
            # 再求截距
            b = -y - x * k

            # 上方直线交点
            # y = kx + b, y = 0 => x = -b / k
            top_cross_x = -b / k

            # 下方直线交点
            # y = kx + b, y = HEIGHT => x = (-HEIGHT - b) / k
            bottom_cross_x = (-cor.HEIGHT - b) / k

            # 左侧直线交点
            right_cross_y = cor.WIDTH * k + b

            # 右侧直线交点
            left_cross_y = b

            if 0 <= top_cross_x <= cor.WIDTH:
                if line_top >= 0 >= line_bottom:
                    _points.append((top_cross_x, 0))
            if 0 <= bottom_cross_x <= cor.WIDTH:
                if line_top >= -cor.HEIGHT >= line_bottom:
                    _points.append((bottom_cross_x, cor.HEIGHT))
            if -cor.HEIGHT < left_cross_y < 0:
                if line_left <= 0 <= line_right:
                    _points.append((0, -left_cross_y))
            if -cor.HEIGHT < right_cross_y < 0:
                if line_left <= cor.WIDTH <= line_right:
                    _points.append((cor.WIDTH, -right_cross_y))

        if len(_points) != 2:
            # 只有一个交点，那么可能是线不够长
            # 上方端点在画面内
            if -cor.HEIGHT <= line_top <= 0 and \
                    0 <= (line_left if (180 > _angle > 90 or 360 > _angle > 270) else line_right) <= cor.WIDTH:
                point_x = line_left if (180 > _angle > 90 or 360 > _angle > 270) else line_right
                _points.append((point_x, -line_top))

            # 下方端点在画面内
            if -cor.HEIGHT <= line_bottom <= 0 and \
                    0 <= (line_right if (180 > _angle > 90 or 360 > _angle > 270) else line_left) <= cor.WIDTH:
                point_x = line_right if (180 > _angle > 90 or 360 > _angle > 270) else line_left
                _points.append((point_x, -line_bottom))

        if len(_points) == 1:
            _points = []

        # print(line_top, line_bottom, _angle, _points, )
        return _points


class EvalPainter:
    # 持续时长
    DURATION = 0.5

    def __init__(self):
        # [(<Tap Object>, 1.254418), ...]
        self.notes_time_eval: T.List[T.Tuple[Note, float, str]] = []

    def add_note(self, note: Note, eval_: str):
        """
        添加note
        :param note:
        :param eval_: core.Eval.GOOD / core.Eval.PERFECT
        :return:
        """
        self.notes_time_eval.append((note, time.time(), eval_))

    def blit(self, surface):
        # todo: 做Hold的part

        while self.notes_time_eval and (time.time() - self.notes_time_eval[0][1]) >= EvalPainter.DURATION:
            self.notes_time_eval.pop(0)

        for note, time_, eval_ in self.notes_time_eval:
            texture = cor.Texture[cor.Texture.EvalImg][eval_,
                                                         min(int(29 * (time.time() - time_) / EvalPainter.DURATION),
                                                             29)]
            surface.blit(
                texture, (note.x_in_surface - texture.get_width() / 2, note.y_in_surface - texture.get_height() / 2)
            )


class ElementPainter:
    """
    为了避免庞大的计算量，本模块使用多线程对所有note进行计算，在减少计算压力的同时保证note显示的完整性
    note 绘制的步骤：
        1. 判定线先更新位置并显示，同时将note载入notes[]，然后再载入threads[]
        2. 启动线程。判定线全部更新完之后，NotePainter对所有的note的位置使用多线程计算更新
        3. note的位置更新的过程中，可以显示的note会被浅拷贝至visible_notes[]
        4. 位置全部更新完后，对visible_notes[]进行排序，key=lambda x: [x.judgeline.id, x.at, x.id != element.Note.HOLD]
        5. 最后按顺序绘制visible_notes[]中的note即可
    """
    N = 25  # 一个线程分配的Note数

    def __init__(self):
        self.visible_notes = []

    def paint(self, surface, beat):
        self.visible_notes = []
        threads = []

        # ---------- STEP 1 ----------

        for judge_line in cor.judge_line_list:
            judge_line.blit(surface, beat)

            for i in range(0, len(judge_line.notes), ElementPainter.N):
                t = threading.Thread(
                    target=ElementPainter.upgrade_notes,
                    args=(self, judge_line.notes[i: i + ElementPainter.N], surface, beat,)
                )
                t.setDaemon(True)
                threads.append(t)

        # ---------- STEP 1 ----------

        # ---------- STEP 2 ----------

        for t in threads:
            t.start()

        # 等待计算完毕
        for t in threads:
            t.join()

        # ---------- STEP 2 ----------

        # ---------- STEP 4 ----------

        self.visible_notes.sort(key=lambda x: [x.judge_line.id, x.at, x.id != Note.HOLD])

        # ---------- STEP 4 ----------

        # ---------- STEP 5 ----------

        for note in self.visible_notes:
            note.blit(surface)

        # ---------- STEP 5 ----------

    def upgrade_notes(self, notes, surface, beat):
        # ---------- STEP 3 ----------

        for note in notes:
            note.upgrade(surface, beat)
            if not (note.x_in_surface > cor.WIDTH or note.x_in_surface < 0 or
                    note.y_in_surface < 0 or note.y_in_surface > cor.HEIGHT):
                self.visible_notes.append(note)

        # ---------- STEP 3 ----------


if __name__ == '__main__':
    pass
