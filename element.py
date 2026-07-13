"""
Phira 兼容的谱面元素渲染
基于 Phira (https://github.com/TeamFlos/phira) 的实现逻辑
"""
import time
import math
from collections import deque
import typing as T
import pygame.surface
import alterobj
import core as cor
import debug


# ==============================================================================
# JudgeLine — 判定线
# ==============================================================================

class JudgeLine:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.angle = 0
        self.alpha = 0
        self.speed = 0
        self.id = -1
        self.lastbeat = 0
        
        # Phira 风格的事件系统
        self.x_anim: T.Optional[alterobj.AnimFloat] = None
        self.y_anim: T.Optional[alterobj.AnimFloat] = None
        self.alpha_anim: T.Optional[alterobj.AnimFloat] = None
        self.angle_anim: T.Optional[alterobj.AnimFloat] = None
        self.speed_anim: T.Optional[alterobj.AnimFloat] = None
        # height 速度积分（关键！Phira 用 height 而非 floor_position）
        self.height_anim: T.Optional[alterobj.AnimFloat] = None
        
        self.notes = []
        self.holds = []
        self.not_holds = []
        self.above1 = []
        self.above2 = []
        
        # 缓存
        self._LINE_LENGTH_HALF = cor.LINE_LENGTH / 2
        self._last_anim_time = -999.0

    def set_time(self, beat: float):
        """统一设置所有 AnimFloat 的时间（Phira 的 Object.set_time）"""
        if beat == self._last_anim_time:
            return
        self._last_anim_time = beat
        
        if self.x_anim:
            self.x_anim.set_time(beat)
            self.x = self.x_anim.now() * cor.LINE_X_SCALE + cor.WIDTH / 2
        if self.y_anim:
            self.y_anim.set_time(beat)
            self.y = self.y_anim.now() * cor.LINE_Y_SCALE + cor.HEIGHT / 2
        if self.alpha_anim:
            self.alpha_anim.set_time(beat)
            self.alpha = self.alpha_anim.now()
        if self.angle_anim:
            self.angle_anim.set_time(beat)
            self.angle = -self.angle_anim.now()
        if self.speed_anim:
            self.speed_anim.set_time(beat)
            self.speed = self.speed_anim.now()
        # height 已经以秒为单位，不需要额外转换

    def get_height(self, time_seconds: float) -> float:
        """获取指定时间（秒）的 line height"""
        if self.height_anim:
            # height_anim 的 keyframes 是以秒为单位的时间
            self.height_anim.set_time(time_seconds)
            return self.height_anim.now()
        return 0.0

    def blit(self, surface: pygame.surface.Surface, beat: float, current_time_sec: float):
        """
        绘制判定线和 note
        beat: 当前音乐播放的 beat
        current_time_sec: 当前时间（秒），用于 height 计算
        """
        self.set_time(beat)
        
        points = self.get_points()
        if points and self.alpha > 0:
            pygame.draw.line(surface, (237, 236, 176, max(0, min(255, int(self.alpha)))), 
                             points[0], points[1], width=5)

        # 获取当前 line height (积分速度后的累计位置)
        line_height = self.get_height(current_time_sec)
        
        # 按顺序绘制上面和下面的 note
        for note in self.above1:
            note.upgrade_and_blit(surface, beat, current_time_sec, line_height)
        for note in self.above2:
            note.upgrade_and_blit(surface, beat, current_time_sec, line_height)

    def get_points(self):
        """计算判定线在屏幕上的两端点"""
        _angle = self.angle % 180
        _angle_rad = math.radians(_angle)
        cos_a = math.cos(_angle_rad)
        sin_a = math.sin(_angle_rad)

        half_len = self._LINE_LENGTH_HALF

        line_left_x = self.x + half_len * cos_a
        line_right_x = self.x - half_len * cos_a
        line_top_y = -self.y + half_len * sin_a
        line_bottom_y = -self.y - half_len * sin_a

        if line_left_x > line_right_x:
            line_left_x, line_right_x = line_right_x, line_left_x
        if line_top_y < line_bottom_y:
            line_top_y, line_bottom_y = line_bottom_y, line_top_y

        _points = []
        if _angle == 90:
            if 0 <= self.x <= cor.WIDTH:
                if line_top_y >= 0 >= line_bottom_y:
                    _points.append((self.x, 0))
                if line_top_y >= -cor.HEIGHT >= line_bottom_y:
                    _points.append((self.x, cor.HEIGHT))
        elif _angle == 0:
            if -cor.HEIGHT <= -self.y <= 0:
                if line_left_x <= 0 <= line_right_x:
                    _points.append((0, self.y))
                if line_left_x <= cor.WIDTH <= line_right_x:
                    _points.append((cor.WIDTH, self.y))
        else:
            k = math.tan(_angle_rad)
            b = -self.y - self.x * k
            top_cross_x = -b / k
            bottom_cross_x = (-cor.HEIGHT - b) / k
            right_cross_y = cor.WIDTH * k + b
            left_cross_y = b

            if 0 <= top_cross_x <= cor.WIDTH and line_top_y >= 0 >= line_bottom_y:
                _points.append((top_cross_x, 0))
            if 0 <= bottom_cross_x <= cor.WIDTH and line_top_y >= -cor.HEIGHT >= line_bottom_y:
                _points.append((bottom_cross_x, cor.HEIGHT))
            if -cor.HEIGHT < left_cross_y < 0 and line_left_x <= 0 <= line_right_x:
                _points.append((0, -left_cross_y))
            if -cor.HEIGHT < right_cross_y < 0 and line_left_x <= cor.WIDTH <= line_right_x:
                _points.append((cor.WIDTH, -right_cross_y))

        if len(_points) == 1:
            if -cor.HEIGHT <= line_top_y <= 0 and \
                    0 <= (line_left_x if _angle > 90 else line_right_x) <= cor.WIDTH:
                _points.append((line_left_x if _angle > 90 else line_right_x, -line_top_y))
            elif -cor.HEIGHT <= line_bottom_y <= 0 and \
                    0 <= (line_right_x if _angle > 90 else line_left_x) <= cor.WIDTH:
                _points.append((line_right_x if _angle > 90 else line_left_x, -line_bottom_y))
            else:
                _points = []

        return _points


# ==============================================================================
# Note — 使用 Phira 坐标计算
# ==============================================================================

class Note:
    TAP = 1
    DRAG = 2
    FLICK = 3
    HOLD = 4

    _NOTE_OFFSETS = None

    @classmethod
    def _init_offsets(cls):
        if cls._NOTE_OFFSETS is None:
            theta = cor.NOTE_THETA
            r = cor.NOTE_R
            cls._NOTE_OFFSETS = [
                (r * math.cos(math.radians(theta)),
                 -r * math.sin(math.radians(theta))),
                (r * math.cos(math.radians(180 - theta)),
                 -r * math.sin(math.radians(180 - theta))),
                (r * math.cos(math.radians(-180 + theta)),
                 -r * math.sin(math.radians(-180 + theta))),
                (r * math.cos(math.radians(-theta)),
                 -r * math.sin(math.radians(-theta))),
            ]

    def __init__(self, judge_line, x=0, time_sec=0, above=True, alpha=0, end_sec=-1, fake=False, speed=1.0, height=0.0, y_offset=0.0):
        """
        time_sec: note 的时间（秒）— Phira 的 time
        height: note 的 floor position — Phira 的 height (从 speed 积分得来)
        y_offset: note 在判定线上的 y 偏移
        """
        self.judge_line = judge_line
        self.x = x                    # x 坐标 (RPE 归一化后)
        self.time = time_sec          # 秒
        self.end = end_sec            # 秒 (对于 Hold)
        self.y_offset = y_offset      # y 偏移
        self.height = height          # floor position (速度积分)
        self.angle = 0 if above else 180
        self.above = above
        self.alpha = alpha
        self.fake = fake
        self.id = -1
        self.highlight = False
        self.speed = speed
        # 屏幕坐标缓存
        self.x_in_surface = -1
        self.y_in_surface = -1
        self._line_height_cache = 0

    def compute_y(self, time_sec: float, line_height: float) -> float:
        """
        基于 Phira 公式计算 note 的相对 y 位置
        base = (note.height - line_height) * note.speed + note.y_offset
        然后根据判定线的角度投影到屏幕
        """
        # Phira: base = (note.height - line_height) / aspect_ratio * note.speed
        # 但在 pyphi 的屏幕坐标系下，不需要 aspect_ratio
        base = (self.height - line_height) * self.speed
        
        # 加上 y_offset（Phira 的 object.translation.y / speed 转换为世界坐标）
        y_offset = self.y_offset * self.speed
        y_pos = base + y_offset
        
        return y_pos

    def upgrade(self, time_sec: float, line_height: float):
        """计算 note 在屏幕上的位置"""
        # 获取 note 的相对 y 位置 (Phira 公式)
        _y = self.compute_y(time_sec, line_height)
        
        _x = self.x * cor.DEBUG_K
        r = (_x ** 2 + _y ** 2) ** 0.5

        if r == 0:
            angle = self.judge_line.angle
        elif _x > 0:
            angle = self.judge_line.angle + math.degrees(math.atan2(_y, _x))
        elif _x < 0:
            angle = self.judge_line.angle + math.degrees(math.atan2(_y, _x))
        else:
            angle = self.judge_line.angle + (90 if _y >= 0 else -90)

        self.x_in_surface = r * math.cos(math.radians(angle)) + self.judge_line.x
        self.y_in_surface = r * math.sin(math.radians(angle)) * (-1 if self.above else 1) + self.judge_line.y

    def blit(self, surface):
        x = self.x_in_surface
        y = self.y_in_surface

        if not (x < -50 or x > cor.WIDTH + 50 or y < -50 or y > cor.HEIGHT + 50):
            self.draw_at(surface, x, y, self.judge_line.angle, self.alpha)

    def upgrade_and_blit(self, surface, beat, time_sec, line_height):
        self.upgrade(time_sec, line_height)
        self.blit(surface)

    @classmethod
    def _get_rotated_diamond(cls, cx, cy, angle):
        """获取旋转后的菱形四个顶点"""
        cls._init_offsets()
        ang = math.radians(angle)
        cos_a = math.cos(ang)
        sin_a = math.sin(ang)
        points = []
        for ox, oy in cls._NOTE_OFFSETS:
            rx = ox * cos_a + oy * sin_a
            ry = -ox * sin_a + oy * cos_a
            points.append((cx + rx, cy + ry))
        return points

    @classmethod
    def draw_at_(cls, surface, x, y, angle, color, highlight):
        color_ = (
            min(color[0] + (64 if highlight else 0), 255),
            min(color[1] + (64 if highlight else 0), 255),
            min(color[2], 255)
        )
        points = cls._get_rotated_diamond(x, y, angle)
        pygame.draw.polygon(surface, color_, points)

    def draw_at(self, surface, x, y, angle, alpha):
        pass


class Tap(Note):
    def __init__(self, judge_line, x=0, time_sec=0, above=True, alpha=0, end_sec=-1, fake=False, speed=1.0, height=0.0, y_offset=0.0):
        super().__init__(judge_line, x, time_sec, above, alpha, end_sec, fake, speed, height, y_offset)
        self.id = Note.TAP

    def draw_at(self, surface, x, y, angle, alpha):
        Note.draw_at_(surface, x, y, angle, (0, 194, 255, alpha), self.highlight)


class Drag(Note):
    def __init__(self, judge_line, x=0, time_sec=0, above=True, alpha=0, end_sec=-1, fake=False, speed=1.0, height=0.0, y_offset=0.0):
        super().__init__(judge_line, x, time_sec, above, alpha, end_sec, fake, speed, height, y_offset)
        self.id = Note.DRAG

    def draw_at(self, surface, x, y, angle, alpha):
        Note.draw_at_(surface, x, y, angle, (237, 243, 77, alpha), self.highlight)


class Flick(Note):
    def __init__(self, judge_line, x=0, time_sec=0, above=True, alpha=0, end_sec=-1, fake=False, speed=1.0, height=0.0, y_offset=0.0):
        super().__init__(judge_line, x, time_sec, above, alpha, end_sec, fake, speed, height, y_offset)
        self.id = Note.FLICK

    def draw_at(self, surface, x, y, angle, alpha):
        Note.draw_at_(surface, x, y, angle, (255, 14, 89, alpha), self.highlight)


class Hold(Note):
    def __init__(self, judge_line, x=0, time_sec=0, above=True, alpha=0, end_sec=-1, fake=False, speed=1.0, height=0.0, y_offset=0.0):
        super().__init__(judge_line, x, time_sec, above, alpha, end_sec, fake, speed, height, y_offset)
        self.id = Note.HOLD
        self.end_height = height  # Hold end 的 height（由加载器设置）
        self.duration = self.end - self.time
        self.last_eval_time = -1
        self.length = 0
        self._BAR_WIDTH_HALF = cor.BAR_WIDTH / 2

    def upgrade(self, time_sec: float, line_height: float):
        """Hold 的升级，绘制延伸条"""
        if time_sec > self.end:
            time_sec = self.end

        # Hold 的起始和结束 y 位置
        base_y = self.compute_y(time_sec, line_height)
        end_base = (self.end_height - line_height) * self.speed + self.y_offset * self.speed
        
        if time_sec < self.time:
            length = (end_base - base_y)  # 整个长度
        else:
            length = (end_base - base_y)  # 剩余长度
            if length < 0:
                length = 0

        _x = self.x * cor.DEBUG_K
        r = (_x ** 2 + base_y ** 2) ** 0.5

        if r == 0:
            angle = self.judge_line.angle
        elif _x > 0:
            angle = self.judge_line.angle + math.degrees(math.atan2(base_y, _x))
        elif _x < 0:
            angle = self.judge_line.angle + math.degrees(math.atan2(base_y, _x))
        else:
            angle = self.judge_line.angle + (90 if base_y >= 0 else -90)

        self.x_in_surface = r * math.cos(math.radians(angle)) + self.judge_line.x
        self.y_in_surface = r * math.sin(math.radians(angle)) + self.judge_line.y

        self.length = length

    def blit(self, surface):
        length = self.length
        x = self.x_in_surface
        y = self.y_in_surface

        if length <= 0:
            return

        angle_rad = math.radians(self.judge_line.angle)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)

        bar_half = self._BAR_WIDTH_HALF / 2
        # Hold bar
        pygame.draw.polygon(surface,
                            (10 + (32 if self.highlight else 0),
                             195 + (32 if self.highlight else 0),
                             255,
                             self.alpha * 0.8), [
            (x + bar_half * cos_a, y - bar_half * sin_a),
            (x - bar_half * cos_a, y + bar_half * sin_a),
            (x - bar_half * cos_a + length * sin_a, y + bar_half * sin_a + length * cos_a),
            (x + bar_half * cos_a + length * sin_a, y - bar_half * sin_a + length * cos_a),
        ])

        # 末端菱形
        angle = self.judge_line.angle
        points = Note._get_rotated_diamond(x, y, angle)
        pygame.draw.polygon(surface, (10 + (32 if self.highlight else 0),
                                      195 + (32 if self.highlight else 0),
                                      255,
                                      self.alpha * 0.8), points)

    def upgrade_and_blit(self, surface, beat, time_sec, line_height):
        self.upgrade(time_sec, line_height)
        self.blit(surface)


# ==============================================================================
# EvalPainter — 判定特效
# ==============================================================================

class EvalPainter:
    DURATION = 0.5

    def __init__(self):
        self.notes_time_eval: T.Deque[T.Tuple[Note, float, str]] = deque()

    def add_note(self, note: Note, eval_: str):
        self.notes_time_eval.append((note, time.time(), eval_))

    def blit(self, surface):
        now = time.time()
        while self.notes_time_eval and (now - self.notes_time_eval[0][1]) >= EvalPainter.DURATION:
            self.notes_time_eval.popleft()

        if not self.notes_time_eval:
            return

        for note, t, eval_ in self.notes_time_eval:
            frame = min(int(29 * (now - t) / EvalPainter.DURATION), 29)
            try:
                texture = cor.Texture[cor.Texture.EvalImg][eval_, frame]
            except (KeyError, IndexError):
                continue
            surface.blit(
                texture,
                (note.x_in_surface - texture.get_width() / 2,
                 note.y_in_surface - texture.get_height() / 2)
            )
