"""
Phira 兼容的事件系统和 BPM 处理
基于 Phira GitHub (https://github.com/TeamFlos/phira) 的实现逻辑
"""
import core as cor
import easing
import math
from typing import List, Tuple, Optional


# ==============================================================================
# BpmList — 基于 Phira 的核心实现
# ==============================================================================

class BpmList:
    """
    Phira 风格的 BpmList
    内部存储: [(beats, time_seconds, bpm), ...]
    """
    
    def __init__(self, bpm_items: List[dict]):
        """
        从 RPE JSON 的 BPMList 构建
        bpm_items: [{"bpm": 120, "startTime": [0, 0, 1]}, ...]
        """
        self.elements: List[Tuple[float, float, float]] = []
        self.cursor = 0
        
        # 按 startTime 排序
        sorted_items = sorted(bpm_items, key=lambda x: list2beat(x["startTime"]))
        
        time_s = 0.0
        last_beats = 0.0
        last_bpm = None
        
        for item in sorted_items:
            bpm = float(item["bpm"])
            now_beats = list2beat(item["startTime"])
            
            if last_bpm is not None:
                time_s += (now_beats - last_beats) * (60.0 / last_bpm)
            
            last_beats = now_beats
            last_bpm = bpm
            self.elements.append((now_beats, time_s, bpm))
        
        if not self.elements:
            # 默认 120 BPM
            self.elements = [(0.0, 0.0, 120.0)]
    
    def reset(self):
        """重置游标"""
        self.cursor = 0
    
    def beat_to_time(self, beats: float) -> float:
        """
        将 beat 转换为秒 (Phira 的 time_beats)
        """
        while self.cursor + 1 < len(self.elements):
            if self.elements[self.cursor + 1][0] > beats:
                break
            self.cursor += 1
        while self.cursor > 0 and self.elements[self.cursor][0] > beats:
            self.cursor -= 1
        
        start_beats, time_s, bpm = self.elements[self.cursor]
        return time_s + (beats - start_beats) * (60.0 / bpm)
    
    def time_to_beat(self, time_s: float) -> float:
        """
        将秒转换为 beat (Phira 的 beat)
        """
        while self.cursor + 1 < len(self.elements):
            if self.elements[self.cursor + 1][1] > time_s:
                break
            self.cursor += 1
        while self.cursor > 0 and self.elements[self.cursor][1] > time_s:
            self.cursor -= 1
        
        beats, start_time_s, bpm = self.elements[self.cursor]
        return beats + (time_s - start_time_s) / (60.0 / bpm)



# ==============================================================================
# Tween / Easing 基础实现 (不使用 easing.py)
# ==============================================================================

PI = math.pi

# 将 RPE easingType 映射到 Phira tween_id
# RPE映射: Plain(1)→Liner(2), EaseIn(2)→Sine(4), EaseOut(3)→Sine(3)
# Phira tween_ids: 0=const0, 1=const1, 2=linear, 3=sineIn, 4=sineOut, 5=sineInOut
# 6=quadIn, 7=quadOut, 8=quadInOut, ...

def _lerp(t): return t
def _ease_sine_out(t): return math.sin(t * PI / 2.0)
def _ease_sine_in(t): return 1.0 - math.cos(t * PI / 2.0)
def _ease_sine_inout(t): return -(math.cos(PI * t) - 1.0) / 2.0

def _ease_quad_out(t): return t * (2.0 - t)
def _ease_quad_in(t): return t * t
def _ease_quad_inout(t): return 2.0*t*t if t < 0.5 else -1.0 + (4.0-2.0*t)*t

def _ease_cubic_out(t): return (t - 1.0)**3 + 1.0
def _ease_cubic_in(t): return t*t*t
def _ease_cubic_inout(t): return 4*t**3 if t < 0.5 else (t-1)*(2*t-2)**2 + 1

def _ease_quart_out(t): return 1.0 - (t - 1.0)**4
def _ease_quart_in(t): return t**4
def _ease_quart_inout(t): return 8*t**4 if t < 0.5 else 1 - 8*(t-1)**4

def _ease_quint_out(t): return 1 + (t-1)**5
def _ease_quint_in(t): return t**5
def _ease_quint_inout(t): return 16*t**5 if t < 0.5 else 1 + 16*(t-1)**5

def _ease_expo_out(t): return 1 - 2**(-10*t) if t > 0 else 0
def _ease_expo_in(t): return 2**(10*t-10) if t > 0 else 0
def _ease_expo_inout(t):
    if t <= 0: return 0
    if t >= 1: return 1
    return 2**(20*t-10)/2 if t < 0.5 else (2-2**(-20*t+10))/2

def _ease_circ_out(t): return math.sqrt(1 - (t-1)**2)
def _ease_circ_in(t): return 1 - math.sqrt(1 - t**2)
def _ease_circ_inout(t):
    return (1-math.sqrt(1-4*t**2))/2 if t < 0.5 else (math.sqrt(1-(-2*t+2)**2)+1)/2

def _ease_back_out(t):
    C1, C3 = 1.70158, 2.70158
    t -= 1
    return C3*t**3 + C1*t**2 + 1
def _ease_back_in(t):
    C1, C3 = 1.70158, 2.70158
    return C3*t**3 - C1*t**2
def _ease_back_inout(t):
    C2 = 1.70158*1.525
    t2 = t*2
    if t2 < 1: return ((t2**2)*((C2+1)*t2-C2))/2
    t2 -= 2
    return ((t2**2)*((C2+1)*t2+C2)+2)/2

def _ease_elastic_out(t):
    if t <= 0: return 0
    if t >= 1: return 1
    return 2**(-10*t)*math.sin((t*10-0.75)*2*PI/3)+1
def _ease_elastic_in(t):
    if t <= 0: return 0
    if t >= 1: return 1
    return -(2**(10*t-10))*math.sin((t*10-10.75)*2*PI/3)
def _ease_elastic_inout(t):
    if t <= 0: return 0
    if t >= 1: return 1
    t2 = t*2
    C5 = 2*PI/4.5
    if t2 < 1:
        return -(2**(10*t2-10))*math.sin((t2*10-11.125)*C5)/2
    return 2**(-10*t2+10)*math.sin((t2*10-11.125)*C5)/2+1

def _ease_bounce_out(t):
    N1, D1 = 7.5625, 2.75
    if t < 1/D1: return N1*t**2
    if t < 2/D1: return N1*(t-1.5/D1)**2+0.75
    if t < 2.5/D1: return N1*(t-2.25/D1)**2+0.9375
    return N1*(t-2.625/D1)**2+0.984375
def _ease_bounce_in(t): return 1 - _ease_bounce_out(1-t)
def _ease_bounce_inout(t):
    return _ease_bounce_in(t*2)/2 if t < 0.5 else _ease_bounce_out(t*2-1)/2+0.5

# RPE easing_type → Phira tween_id 映射
# RPE: 0=linear, 1=ease(quad), 2=easeIn, 3=easeOut, 4=easeInOut
# Phira: 2=lerp, 7=quadOut, 6=quadIn, 8=quadInOut
RPE_TWEEN_MAP = {0: 2, 1: 7, 2: 6, 3: 7, 4: 8, 5: 4, 6: 3, 7: 10}

# Phira tween_id → easing function (共 33 个)
TWEEN_FUNCS = [
    _ease_bounce_out,  # dummy
    _ease_bounce_out,  # dummy
    _lerp,  # 2=linear
    _ease_sine_in, _ease_sine_out, _ease_sine_inout,  # 3-5
    _ease_quad_in, _ease_quad_out, _ease_quad_inout,  # 6-8
    _ease_cubic_in, _ease_cubic_out, _ease_cubic_inout,  # 9-11
    _ease_quart_in, _ease_quart_out, _ease_quart_inout,  # 12-14
    _ease_quint_in, _ease_quint_out, _ease_quint_inout,  # 15-17
    _ease_expo_in, _ease_expo_out, _ease_expo_inout,  # 18-20
    _ease_circ_in, _ease_circ_out, _ease_circ_inout,  # 21-23
    _ease_back_in, _ease_back_out, _ease_back_inout,  # 24-26
    _ease_elastic_in, _ease_elastic_out, _ease_elastic_inout,  # 27-29
    _ease_bounce_in, _ease_bounce_out, _ease_bounce_inout,  # 30-32
]

def lerp(a: float, b: float, t: float) -> float:
    """线性插值"""
    return a + (b - a) * t

def apply_tween(tween_id: int, t: float) -> float:
    """应用缓动函数，返回 [0,1] 范围内的值"""
    if 0 <= tween_id < len(TWEEN_FUNCS):
        return TWEEN_FUNCS[tween_id](t)
    return t


# ==============================================================================
# AnimFloat — 基于 Phira 的 Anim<T> 系统
# ==============================================================================

class Keyframe:
    """关键帧 (Phira 的 Keyframe<T>)"""
    __slots__ = ('time', 'value', 'tween_id')
    
    def __init__(self, time: float, value: float, tween_id: int = 2):
        self.time = time       # in beats (for event-based)
        self.value = value
        self.tween_id = tween_id  # Phira easing code


class AnimFloat:
    """
    Phira 风格的动画浮点数
    支持关键帧插值和 cursor 游标
    """
    __slots__ = ('keyframes', 'cursor', 'time', '_value')
    
    def __init__(self, keyframes: List[Keyframe] = None):
        self.keyframes = list(keyframes) if keyframes else []
        self.cursor = 0
        self.time = 0.0
        self._value = 0.0
    
    @staticmethod
    def fixed(value: float) -> 'AnimFloat':
        """固定值"""
        return AnimFloat([Keyframe(0, value, 0)])
    
    def is_empty(self) -> bool:
        return len(self.keyframes) == 0
    
    def dead(self) -> bool:
        return self.cursor + 1 >= len(self.keyframes)
    
    def set_time(self, time: float):
        """设置当前时间并计算插值 (Phira 的 set_time)"""
        if not self.keyframes:
            return
        if time == self.time and self.cursor > 0:
            return
        
        # 前向推进游标
        while self.cursor + 1 < len(self.keyframes):
            if self.keyframes[self.cursor + 1].time > time:
                break
            self.cursor += 1
        
        # 后向回退游标
        while self.cursor > 0 and self.keyframes[self.cursor].time > time:
            self.cursor -= 1
        
        self.time = time
        
        # 计算插值
        if self.cursor == len(self.keyframes) - 1:
            self._value = self.keyframes[self.cursor].value
        else:
            kf1 = self.keyframes[self.cursor]
            kf2 = self.keyframes[self.cursor + 1]
            duration = kf2.time - kf1.time
            if duration > 0:
                t = max(0.0, min(1.0, (time - kf1.time) / duration))
            else:
                t = 0.0
            eased_t = apply_tween(kf1.tween_id, t)
            self._value = lerp(kf1.value, kf2.value, float(eased_t))
    
    def now(self) -> float:
        """获取当前值"""
        return self._value if self.keyframes else 0.0
    
    def now_opt(self, default: float = None) -> Optional[float]:
        if not self.keyframes:
            return default
        return self._value
    
    def reset(self):
        self.cursor = 0
        self.time = 0.0
        self._value = 0.0 if not self.keyframes else self.keyframes[0].value


# ==============================================================================
# Speed 积分 — 将 speed events 转换为 height (Phira 的 SpeedIntegralTween)
# ==============================================================================

class SpeedIntegral:
    """
    基于 Phira 的 speed_segment_tween 实现
    将速度事件积分得到 height（总距离）
    """
    
    @staticmethod
    def integrate_speed(speed_events: List[dict], max_time: float) -> AnimFloat:
        """
        将 speed events 积分计算每个时间点的 height（累积距离）
        
        speed_events: [{"startTime": [...], "endTime": [...], "start": x, "end": y}, ...]
        max_time: 谱面最大时间（秒）
        
        返回: AnimFloat, time in beats, value = 累积距离 (floor_position)
        """
        keyframes = []
        
        if not speed_events:
            # 如果没有速度事件，使用默认速度 1.0
            keyframes.append(Keyframe(0.0, 0.0, 2))
            return AnimFloat(keyframes)
        
        # 按开始时间排序
        sorted_events = sorted(speed_events, key=lambda e: list2beat(e["startTime"]))
        
        total_distance = 0.0
        prev_beat = list2beat(sorted_events[0]["startTime"]) if sorted_events else 0.0
        
        # 第一个关键帧在 beat 0
        first_beat = list2beat(sorted_events[0]["startTime"]) if sorted_events else 0.0
        if first_beat > 0:
            keyframes.append(Keyframe(0.0, 0.0, 2))
        else:
            keyframes.append(Keyframe(0.0, 0.0, 2))
        
        for event in sorted_events:
            start_beat = list2beat(event["startTime"])
            end_beat = list2beat(event["endTime"])
            start_speed = float(event["start"])
            end_speed = float(event["end"])
            
            # 前一段到当前事件开始的距离（以开始速度匀速前进）
            if start_beat > prev_beat:
                total_distance += start_speed * (start_beat - prev_beat)
                keyframes.append(Keyframe(start_beat, total_distance, 2))
            
            # 本段：使用平均速度
            if end_beat > start_beat:
                avg_speed = (start_speed + end_speed) / 2.0
                segment_dist = avg_speed * (end_beat - start_beat)
                total_distance += segment_dist
                keyframes.append(Keyframe(end_beat, total_distance, 2))
            
            prev_beat = end_beat
        
        # 添加一段延伸到 max_time
        if prev_beat < max_time and prev_beat < 9999:
            last_speed = sorted_events[-1]["end"] if sorted_events else 1.0
            total_distance += last_speed * (max_time - prev_beat)
            keyframes.append(Keyframe(max_time, total_distance, 0))  # 保持常量
        
        if not keyframes:
            keyframes.append(Keyframe(0.0, 0.0, 0))
        
        return AnimFloat(keyframes)


# ==============================================================================
# 工具函数
# ==============================================================================

def list2beat(_list):
    """将 [beat, num, den] 格式转换为浮点数"""
    return _list[0] + _list[1] / _list[2]


# 单例 BpmList，由 data.py 设置
GLOBAL_BPMLIST = BpmList([{"bpm": 120, "startTime": [0, 0, 1]}])

def b2s(beat: float) -> float:
    """将 beat 转换为秒（使用全局 BpmList）"""
    GLOBAL_BPMLIST.reset()
    return GLOBAL_BPMLIST.beat_to_time(beat)

def s2b(seconds: float) -> float:
    """将秒转换为 beat"""
    GLOBAL_BPMLIST.reset()
    return GLOBAL_BPMLIST.time_to_beat(seconds)


# -----------------------------------------------------------------------------
# 兼容接口 — 供 data.py / pgr2rpe.py / core.py 使用
# -----------------------------------------------------------------------------

def bpmList(bpm_events):
    """兼容旧的 bpmList 函数 — 返回 {beat: bpm} 字典"""
    result = {}
    for item in bpm_events:
        beat = list2beat(item["startTime"])
        result[beat] = float(item["bpm"])
    return result


class BeatObject:
    """兼容旧的 BeatObject — 基于 BpmList 实现"""
    def __init__(self, bpm_items):
        self.bpm_list = BpmList(bpm_items)
    
    def get_value(self, seconds: float) -> float:
        """将秒转换为 beat"""
        self.bpm_list.reset()
        return self.bpm_list.time_to_beat(seconds)
