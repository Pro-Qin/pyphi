"""
PGR (Phigros) 谱面格式解析器
基于 Phira (https://github.com/TeamFlos/phira) 的 pgr.rs 实现逻辑

支持的格式版本:
- formatVersion 1: 旧版 Phigros JSON 格式
- formatVersion 3: 新版 Phigros 格式（官方格式）
"""
import json
import math
import core as cor
import element
import alterobj


# --- PGR 事件结构 ---

class PgrEvent:
    """PGR 事件"""
    def __init__(self, data):
        self.start_time = data["startTime"]
        self.end_time = data["endTime"]
        self.start = data.get("start", 0)
        self.end = data.get("end", 0)
        self.start2 = data.get("start2", 0)
        self.end2 = data.get("end2", 0)


class PgrSpeedEvent:
    """PGR 速度事件"""
    def __init__(self, data):
        self.start_time = data["startTime"]
        self.end_time = data["endTime"]
        self.value = data["value"]


class PgrNote:
    """PGR Note"""
    def __init__(self, data):
        self.kind = data["type"]
        self.time = data["time"]
        self.position_x = data["positionX"]
        self.hold_time = data.get("holdTime", 0)
        self.speed = data.get("speed", 1.0)
        self.floor_position = data.get("floorPosition", 0)


class PgrJudgeLine:
    """PGR 判定线"""
    def __init__(self, data):
        self.bpm = data["bpm"]
        self.alpha_events = [PgrEvent(e) for e in data.get("judgeLineDisappearEvents", [])]
        self.rotate_events = [PgrEvent(e) for e in data.get("judgeLineRotateEvents", [])]
        self.move_events = [PgrEvent(e) for e in data.get("judgeLineMoveEvents", [])]
        self.speed_events = [PgrSpeedEvent(e) for e in data.get("judgeLineSpeedEvents", [])]
        self.notes_above = [PgrNote(n) for n in data.get("notesAbove", [])]
        self.notes_below = [PgrNote(n) for n in data.get("notesBelow", [])]


def list2beat(_list):
    """将 [beat, num, den] 格式转换为浮点数"""
    return _list[0] + _list[1] / _list[2]


# --- PGR 事件解析 ---

def parse_float_events(r, pgr_events, default_start=0):
    """解析浮点数事件，生成与 alterobj 兼容的事件列表"""
    events = []
    if not pgr_events:
        return events
    
    if pgr_events[0].start_time > 0:
        events.append({
            "easingType": 2,  # EaseOutSine (as fallback)
            "startTime": [0, 0, 1],
            "endTime": [pgr_events[0].start_time, 0, 1],
            "start": default_start,
            "end": pgr_events[0].start,
        })
    
    for e in pgr_events:
        if e.start_time > e.end_time:
            continue
        st_sec = e.start_time * r
        et_sec = e.end_time * r
        st_beat = [int(st_sec), int((st_sec % 1) * 32), 32]
        et_beat = [int(et_sec), int((et_sec % 1) * 32), 32]
        
        events.append({
            "easingType": 0,  # Liner
            "startTime": st_beat,
            "endTime": et_beat,
            "start": e.start,
            "end": e.end,
        })
    
    return events


def is_length_event(event):
    """判断事件是否是传统长度格式（PGR formatVersion < 3 使用）"""
    # 传统格式的 endTime 与 startTime 的关系
    return abs(event.end_time - event.start_time) > 0.001


def parse_move_events(r, pgr_events, format_version):
    """解析移动事件"""
    move_x_events = []
    move_y_events = []
    
    if not pgr_events:
        return move_x_events, move_y_events
    
    for e in pgr_events:
        if e.start_time > e.end_time:
            continue
        st_sec = e.start_time * r
        et_sec = e.end_time * r
        st_beat = [int(st_sec), int((st_sec % 1) * 32), 32]
        et_beat = [int(et_sec), int((et_sec % 1) * 32), 32]
        
        if format_version == 1:
            # formatVersion 1: 坐标编码在单个值中
            start_x = (e.start - e.start % 1000) / 1000
            start_y = e.start % 1000
            end_x = (e.end - e.end % 1000) / 1000
            end_y = e.end % 1000
            
            # 归一化到 [-1, 1]
            start_x = (-880. + start_x * 2.) / 880.
            start_y = (-520. + start_y * 2.) / 520.
            end_x = (-880. + end_x * 2.) / 880.
            end_y = (-520. + end_y * 2.) / 520.
        elif format_version == 3:
            start_x = -1. + e.start * 2.
            start_y = -1. + e.start2 * 2.
            end_x = -1. + e.end * 2.
            end_y = -1. + e.end2 * 2.
        else:
            # 未知版本，保守处理
            start_x = e.start
            start_y = e.start2
            end_x = e.end
            end_y = e.end2
        
        move_x_events.append({
            "easingType": 0,
            "startTime": st_beat,
            "endTime": et_beat,
            "start": start_x,
            "end": end_x,
        })
        move_y_events.append({
            "easingType": 0,
            "startTime": st_beat,
            "endTime": et_beat,
            "start": start_y,
            "end": end_y,
        })
    
    return move_x_events, move_y_events


def parse_speed_events_pgr(r, pgr_events, max_time):
    """解析速度事件，生成兼容的事件"""
    speed_events = []
    
    if not pgr_events:
        return speed_events
    
    # 确保第一个事件从 0 开始
    if pgr_events[0].start_time != 0:
        pgr_events[0].start_time = 0
    
    for e in pgr_events:
        st_sec = e.start_time * r
        et_sec = e.end_time * r
        st_beat = [int(st_sec), int((st_sec % 1) * 32), 32]
        et_beat = [int(et_sec), int((et_sec % 1) * 32), 32]
        
        speed_events.append({
            "easingType": 1,  # 用 Liner
            "startTime": st_beat,
            "endTime": et_beat,
            "start": e.value,
            "end": e.value,
        })
    
    return speed_events


def parse_notes_pgr(r, pgr_notes, above):
    """解析 PGR Note 为 element.Note 对象"""
    notes = []
    
    if not pgr_notes:
        return notes
    
    pgr_notes.sort(key=lambda n: n.time)
    
    for pn in pgr_notes:
        time_sec = pn.time * r
        time_beat = [int(time_sec), int((time_sec % 1) * 32), 32]
        
        # PGR type = 1: Tap, 2: Drag, 3: Hold, 4: Flick
        note_type = pn.kind
        x_pos = pn.position_x * (2. * 9. / 160.)  # PGR 坐标转换
        
        note_data = {
            "type": note_type,
            "positionX": x_pos,
            "startTime": time_beat,
            "endTime": time_beat,
            "above": 1 if above else 2,
            "alpha": 255,
            "isFake": 0,
            "speed": pn.speed if pn.kind != 3 else 1.0,
            "size": 1.0,
        }
        
        if note_type == 2:  # Hold
            end_time_sec = (pn.time + pn.hold_time) * r
            note_data["endTime"] = [int(end_time_sec), int((end_time_sec % 1) * 32), 32]
        
        notes.append(note_data)
    
    return notes


def convert(pgr_path, rpe_path):
    """将 PGR 格式转换为标准 RPE JSON 格式"""
    with open(pgr_path, 'r', encoding='utf-8') as f:
        pgr_data = json.load(f)
    
    format_version = pgr_data.get("formatVersion", 1)
    offset = pgr_data.get("offset", 0)
    judge_line_list = pgr_data.get("judgeLineList", [])
    
    if not judge_line_list:
        raise ValueError("PGR 谱面没有判定线数据")
    
    # 计算最大时间（以秒为单位）
    max_time = 0
    for jl_data in judge_line_list:
        r = 60.0 / 32.0 / jl_data["bpm"]
        for note in jl_data.get("notesAbove", []) + jl_data.get("notesBelow", []):
            t = note.get("time", 0)
            if t * r > max_time:
                max_time = t * r
    max_time += 1.0  # 加一点余量
    
    # 构建 RPE JSON
    rpe_chart = {
        "BPMList": [],
        "META": {
            "RPEVersion": 100,
            "background": pgr_data.get("background", "Unknown.jpg"),
            "charter": pgr_data.get("charter", "Unknown"),
            "composer": pgr_data.get("composer", "Unknown"),
            "id": str(pgr_data.get("id", "10000001")),
            "level": pgr_data.get("level", "Unknown"),
            "name": pgr_data.get("name", "Unknown"),
            "offset": offset,
            "song": pgr_data.get("song", "Unknown.mp3"),
        },
        "formatVersion": "3",
        "judgeLineList": [],
    }
    
    for jl_idx, jl_data in enumerate(judge_line_list):
        jl = PgrJudgeLine(jl_data)
        r = 60.0 / 32.0 / jl.bpm
        
        # BPM 列表
        bpm_beat = list2beat([0, 0, 1])
        if not any(abs(b["startTime"][0] - bpm_beat) < 0.001 for b in rpe_chart["BPMList"]):
            rpe_chart["BPMList"].append({
                "bpm": jl.bpm,
                "startTime": [0, 0, 1]
            })
        
        # 解析事件
        alpha_events = parse_float_events(r, jl.alpha_events, 255)
        rotate_events = parse_float_events(r, jl.rotate_events)
        move_x_events, move_y_events = parse_move_events(r, jl.move_events, format_version)
        speed_events = parse_speed_events_pgr(r, jl.speed_events, max_time)
        
        # 解析 notes
        notes_above = parse_notes_pgr(r, jl.notes_above, True)
        notes_below = parse_notes_pgr(r, jl.notes_below, False)
        all_notes = notes_above + notes_below
        all_notes.sort(key=lambda n: n["startTime"][0] * 1000 + n["startTime"][1] / n["startTime"][2])
        
        # 构建判定线
        judge_line = {
            "Group": 0,
            "Name": f"Line {jl_idx}",
            "Texture": "line.png",
            "eventLayers": [
                {
                    "alphaEvents": alpha_events,
                    "moveXEvents": move_x_events,
                    "moveYEvents": move_y_events,
                    "rotateEvents": rotate_events,
                    "speedEvents": speed_events,
                }
            ],
            "isCover": 1,
            "notes": all_notes,
            "numOfNotes": len(all_notes),
        }
        
        rpe_chart["judgeLineList"].append(judge_line)
    
    # 写入 RPE JSON
    with open(rpe_path, 'w', encoding='utf-8') as f:
        json.dump(rpe_chart, f, indent=2, ensure_ascii=False)
    
    return rpe_chart


def load_pgr_direct(pgr_path):
    """直接加载 PGR 谱面（不经过中间文件）"""
    with open(pgr_path, 'r', encoding='utf-8') as f:
        pgr_data = json.load(f)
    
    format_version = pgr_data.get("formatVersion", 1)
    offset = pgr_data.get("offset", 0)
    judge_line_data_list = pgr_data.get("judgeLineList", [])
    
    if not judge_line_data_list:
        raise ValueError("没有判定线数据")
    
    note_num = 0
    cor.DURATION = 999
    cor.NAME = pgr_data.get("name", cor.NAME)
    cor.ARTIST = pgr_data.get("composer", cor.ARTIST)
    cor.CHART = pgr_data.get("charter", cor.CHART)
    cor.LEVEL = pgr_data.get("level", cor.LEVEL)
    cor.IMAGE = pgr_data.get("background", cor.IMAGE)
    cor.SONG = pgr_data.get("song", cor.SONG)
    cor.OFFSET = offset
    
    # 收集所有判定线的 BPM（PGR 格式中每条线可能有不同 BPM）
    all_bpms = {}
    for jl_idx, jl_data in enumerate(judge_line_data_list):
        bpm = jl_data.get("bpm", 120)
        if bpm not in all_bpms.values():
            all_bpms[f"jl_{jl_idx}"] = {"bpm": bpm, "startTime": [0, 0, 1]}
    
    bpm_list = list(all_bpms.values())
    if not bpm_list:
        bpm_list = [{"bpm": 120, "startTime": [0, 0, 1]}]
    
    cor.BPMLIST = alterobj.bpmList(bpm_list)
    cor.BeatObject = alterobj.BeatObject(bpm_list)
    
    type2note = {1: element.Tap, 2: element.Hold, 3: element.Flick, 4: element.Drag}
    
    total_notes = 0
    for jl_idx, jl_data in enumerate(judge_line_data_list):
        jl = PgrJudgeLine(jl_data)
        r = 60.0 / 32.0 / jl.bpm
        
        judge_line = element.JudgeLine()
        judge_line.id = jl_idx
        
        # 转换事件
        move_x_events, move_y_events = parse_move_events(r, jl.move_events, format_version)
        alpha_events = parse_float_events(r, jl.alpha_events, 255)
        rotate_events = parse_float_events(r, jl.rotate_events)
        speed_events = parse_speed_events_pgr(r, jl.speed_events, 240)
        
        judge_line.x_object = alterobj.LineXObject(move_x_events)
        judge_line.y_object = alterobj.LineYObject(move_y_events)
        judge_line.angle_object = alterobj.AngleObject(rotate_events)
        judge_line.alpha_object = alterobj.AlphaObject(alpha_events)
        judge_line.speed_object = alterobj.LineSpeedObject(speed_events)
        judge_line.note_y_object = alterobj.NoteYObject(speed_events)
        
        # 解析 notes
        all_note_data = parse_notes_pgr(r, jl.notes_above, True) + parse_notes_pgr(r, jl.notes_below, False)
        all_note_data.sort(key=lambda n: (n["startTime"][0], n["startTime"][1] / n["startTime"][2], n["type"] != 2))
        
        for note_data in all_note_data:
            if not note_data["isFake"]:
                total_notes += 1
            
            x_scale = cor.NOTE_X_SCALE
            note = type2note[note_data["type"]](
                judge_line,
                note_data["positionX"] * x_scale,
                list2beat(note_data["startTime"]),
                True if note_data["above"] == 1 else False,
                note_data["alpha"],
                list2beat(note_data["endTime"]),
                True if note_data["isFake"] else False,
                note_data["speed"]
            )
            judge_line.notes.append(note)
        
        judge_line.notes.sort(key=lambda _note: [_note.at, _note.id != element.Note.HOLD])
        
        for note in judge_line.notes:
            if note.id == element.Note.HOLD:
                judge_line.holds.append(note)
            else:
                judge_line.not_holds.append(note)
            if note.above:
                judge_line.above1.append(note)
            else:
                judge_line.above2.append(note)
        
        cor.judge_line_list.append(judge_line)
    
    cor.NOTE_NUM = total_notes
    
    # 设置 highlight
    all_notes = []
    for jl in cor.judge_line_list:
        all_notes.extend(jl.notes)
    all_notes.sort(key=lambda x: x.at)
    
    if all_notes:
        temp_time = all_notes[0].at
        temp_notes = [all_notes[0]]
        for note in all_notes[1:]:
            if note.at == temp_time:
                temp_notes.append(note)
            else:
                if len(temp_notes) > 1:
                    for _note in temp_notes:
                        _note.highlight = True
                temp_notes = [note]
                temp_time = note.at
        if len(temp_notes) > 1:
            for _note in temp_notes:
                _note.highlight = True
