"""
谱面加载器 — 基于 Phira 实现逻辑
"""
import csv
import json
import json.decoder
import shutil

import core as cor
import alterobj
import element
import os
import zipfile
import pec2rpe
import hashlib


def list2beat(_list):
    return _list[0] + _list[1] / _list[2]


class ChartError(Exception):
    pass


def integrate_speed_to_height(speed_events: list, bpm_list: alterobj.BpmList, max_time: float) -> alterobj.AnimFloat:
    """
    将速度事件积分得到 height (Phira 兼容)
    height = ∫ speed(t) dt
    
    Returns: AnimFloat, 时间单位为秒, 值为累计距离
    """
    keyframes = []
    if not speed_events:
        return alterobj.AnimFloat([alterobj.Keyframe(0, 0, 0)])
    
    # 排序
    sorted_evts = sorted(speed_events, key=lambda e: list2beat(e["startTime"]))
    
    height = 0.0
    cursor = 0.0  # 当前秒数
    last_speed = 0.0
    
    # 处理事件
    for event in sorted_evts:
        start_beat = list2beat(event["startTime"])
        end_beat = list2beat(event["endTime"])
        start_speed = float(event["start"])
        end_speed = float(event["end"])
        
        # 转换为秒
        start_time = bpm_list.beat_to_time(start_beat)
        end_time = bpm_list.beat_to_time(end_beat)
        start_time = max(start_time, cursor)
        end_time = max(end_time, start_time)
        
        # 前一段匀速到事件开始
        if start_time > cursor:
            dt = start_time - cursor
            height += last_speed * dt
            keyframes.append(alterobj.Keyframe(start_time, height, 2))
        
        # 当前段用平均速度
        if end_time > start_time:
            avg_speed = (start_speed + end_speed) / 2.0
            # 应用 SPEED_RATIO (来自 Phira: 10/45/0.83175)
            SPEED_RATIO = 10.0 / 45.0 / 0.83175
            avg_speed *= SPEED_RATIO
            
            dt = end_time - start_time
            height += avg_speed * dt
            keyframes.append(alterobj.Keyframe(end_time, height, 2))
        
        cursor = end_time
        last_speed = end_speed * (10.0 / 45.0 / 0.83175)
    
    # 延伸到 max_time
    if cursor < max_time:
        height += last_speed * (max_time - cursor)
        keyframes.append(alterobj.Keyframe(max_time, height, 0))
    
    if not keyframes:
        keyframes.append(alterobj.Keyframe(0, 0, 0))
    
    return alterobj.AnimFloat(keyframes)


def load_rpe(rpe_path):
    """加载 RPE JSON 谱面 — 基于 Phira 逻辑"""
    with open(rpe_path, 'r', encoding="UTF-8") as f:
        chart_json = json.load(f)
    
    note_num = 0
    cor.judge_line_list.clear()
    
    # 基本信息
    cor.DURATION = 999
    cor.NAME = chart_json["META"]["name"]
    cor.ARTIST = chart_json["META"]["composer"]
    cor.CHART = chart_json["META"]["charter"]
    cor.LEVEL = chart_json["META"]["level"]
    cor.IMAGE = chart_json["META"]["background"]
    cor.SONG = chart_json["META"]["song"]
    cor.OFFSET = chart_json["META"]["offset"]
    
    rpe_version = chart_json["META"].get("RPEVersion", "Unknown")
    format_version = chart_json.get("formatVersion", "1")
    print(f"谱面版本: RPE {rpe_version}, 格式版本: {format_version}")
    
    # 构建 BpmList (Phira 风格)
    bpm_items = chart_json.get("BPMList", [{"bpm": 120, "startTime": [0, 0, 1]}])
    bpm_list = alterobj.BpmList(bpm_items)
    
    # 设置全局 BpmList
    alterobj.GLOBAL_BPMLIST = bpm_list
    cor.BPMLIST = alterobj.bpmList(bpm_items)
    cor.BeatObject = alterobj.BeatObject(bpm_items)
    
    # 计算最大时间（秒）
    max_time = 0.0
    for jl_data in chart_json["judgeLineList"]:
        for layer in jl_data.get("eventLayers", []):
            if layer:
                for evt in layer.get("speedEvents", []):
                    t = bpm_list.beat_to_time(list2beat(evt.get("endTime", [0, 0, 1])))
                    if t > max_time:
                        max_time = t
        for note in jl_data.get("notes", []):
            t = bpm_list.beat_to_time(list2beat(note.get("startTime", [0, 0, 1])))
            if note.get("type") == 2:  # Hold
                t2 = bpm_list.beat_to_time(list2beat(note.get("endTime", [0, 0, 1])))
                if t2 > max_time: max_time = t2
            if t > max_time: max_time = t
    max_time = max(max_time + 2.0, 60.0)
    
    type2note = {1: element.Tap, 2: element.Hold, 3: element.Flick, 4: element.Drag}
    total_notes = 0
    
    for jl_idx, jl_data in enumerate(chart_json["judgeLineList"]):
        # 初始化判定线
        judge_line = element.JudgeLine()
        judge_line.id = jl_idx
        
        # ---- 解析事件层（取第一个事件层） ----
        event_layers = [l for l in jl_data.get("eventLayers", []) if l]
        
        # Alpha 事件
        alpha_events_flat = []
        for layer in event_layers:
            for evt in layer.get("alphaEvents", []):
                alpha_events_flat.append(evt)
        judge_line.alpha_anim = _parse_events_to_anim(alpha_events_flat, bpm_list, 
                                                        scale=1.0/255.0, default=255.0/255.0)
        
        # 旋转事件
        rotate_events_flat = []
        for layer in event_layers:
            for evt in layer.get("rotateEvents", []):
                rotate_events_flat.append(evt)
        judge_line.angle_anim = _parse_events_to_anim(rotate_events_flat, bpm_list, 
                                                       scale=-1.0, default=0.0)
        
        # X 移动事件
        move_x_events_flat = []
        for layer in event_layers:
            for evt in layer.get("moveXEvents", []):
                move_x_events_flat.append(evt)
        judge_line.x_anim = _parse_events_to_anim(move_x_events_flat, bpm_list, 
                                                    scale=1.0, default=0.0)
        
        # Y 移动事件
        move_y_events_flat = []
        for layer in event_layers:
            for evt in layer.get("moveYEvents", []):
                move_y_events_flat.append(evt)
        judge_line.y_anim = _parse_events_to_anim(move_y_events_flat, bpm_list, 
                                                    scale=1.0, default=0.0)
        
        # 速度事件 → 积分得到 height (Phira 核心)
        speed_events_flat = []
        for layer in event_layers:
            for evt in layer.get("speedEvents", []):
                speed_events_flat.append(evt)
        judge_line.speed_anim = _parse_events_to_anim(speed_events_flat, bpm_list, 
                                                        scale=1.0, default=1.0)
        judge_line.height_anim = integrate_speed_to_height(speed_events_flat, bpm_list, max_time)
        
        # ---- 解析 Notes ----
        all_note_data = jl_data.get("notes", [])
        all_note_data.sort(key=lambda n: (list2beat(n["startTime"]) * 1000 + 
                                          n.get("positionX", 0)))
        
        for note_data in all_note_data:
            note_type = note_data["type"]
            is_fake = note_data.get("isFake", 0)
            
            # 计算时间（秒）和 height
            start_beat = list2beat(note_data["startTime"])
            time_sec = bpm_list.beat_to_time(start_beat)
            
            # 计算 note 的 floor position (Phira: height.set_time(time) → height.now())
            judge_line.height_anim.set_time(time_sec)
            note_height = judge_line.height_anim.now()
            
            # End time for Hold
            end_sec = -1
            end_height = note_height
            if note_type == 2:  # Hold
                end_beat = list2beat(note_data["endTime"])
                end_sec = bpm_list.beat_to_time(end_beat)
                judge_line.height_anim.set_time(end_sec)
                end_height = judge_line.height_anim.now()
            
            # X 坐标 — RPE: position_x / (RPE_WIDTH/2) → [-1, 1]
            position_x = note_data.get("positionX", 0)
            
            # Y 偏移
            y_offset = note_data.get("yOffset", note_data.get("y_offset", 0))
            speed = float(note_data.get("speed", 1.0))
            alpha = float(note_data.get("alpha", 255))
            
            if not is_fake:
                total_notes += 1
            
            note = type2note[note_type](
                judge_line,
                position_x * cor.NOTE_X_SCALE,
                time_sec,
                note_data.get("above", 1) == 1,
                alpha,
                end_sec,
                bool(is_fake),
                speed,
                note_height,
                y_offset / 900.0  # 归一化到 [-1, 1] 范围
            )
            # Hold 需要 end_height
            if note_type == 2:
                note.end_height = end_height
            
            judge_line.notes.append(note)
        
        # 排序并分配到列表
        judge_line.notes.sort(key=lambda n: (n.time, n.id != element.Note.HOLD))
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
    
    # Highlight 处理
    all_notes = []
    for jl in cor.judge_line_list:
        all_notes.extend(jl.notes)
    all_notes.sort(key=lambda x: x.time)
    
    if all_notes:
        temp_time = all_notes[0].time
        temp_notes = [all_notes[0]]
        for note in all_notes[1:]:
            if note.time == temp_time:
                temp_notes.append(note)
            else:
                if len(temp_notes) > 1:
                    for _note in temp_notes:
                        _note.highlight = True
                temp_notes = [note]
                temp_time = note.time
        if len(temp_notes) > 1:
            for _note in temp_notes:
                _note.highlight = True
    
    cor.NOTE_NUM = total_notes


def _parse_events_to_anim(events: list, bpm_list: alterobj.BpmList, 
                           scale: float = 1.0, default: float = 0.0) -> alterobj.AnimFloat:
    """
    将 RPE 事件列表转换为 AnimFloat
    events: RPE 格式的事件列表
    bpm_list: 用于 beat→time 转换
    scale: 值缩放因子
    default: 没有事件时的默认值
    """
    if not events:
        return alterobj.AnimFloat([alterobj.Keyframe(0, default, 0)])
    
    keyframes = []
    
    # 按 startTime 排序
    sorted_events = sorted(events, key=lambda e: list2beat(e["startTime"]))
    
    for event in sorted_events:
        start_beat = list2beat(event["startTime"])
        end_beat = list2beat(event["endTime"])
        
        # 转换为秒
        start_time = bpm_list.beat_to_time(start_beat)
        end_time = bpm_list.beat_to_time(end_beat)
        
        start_val = float(event["start"]) * scale
        end_val = float(event["end"]) * scale
        easing_type = event.get("easingType", 0)
        
        # RPE easing_type mapping to Phira tween_id
        # 0=linear→2, 1=ease(quadOut)→7, 2=easeIn(quadIn)→6, 3=easeOut→7, 4=easeInOut→8
        tween_map = alterobj.RPE_TWEEN_MAP
        easing_code = tween_map.get(easing_type, 2)
        
        if start_time == end_time:
            keyframes.append(alterobj.Keyframe(start_time, start_val, 0))
        else:
            keyframes.append(alterobj.Keyframe(start_time, start_val, easing_code))
            keyframes.append(alterobj.Keyframe(end_time, end_val, 0))
    
    if not keyframes:
        return alterobj.AnimFloat([alterobj.Keyframe(0, default, 0)])
    
    return alterobj.AnimFloat(keyframes)


def load_zip(zip_dir):
    """
    加载谱面 zip 包 — 支持多种格式
    """
    try:
        print(f'\nloading zip: {zip_dir}')
        
        # 计算文件MD5用于缓存
        with open(zip_dir, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        md5 = file_hash[0:32]
        cor.CHART_MD5 = md5
        
        # 检查缓存
        if os.path.exists(f"./cache/{md5}"):
            if cor.NO_CACHE:
                print('in NO_CACHE_MODE')
                shutil.rmtree(f"./cache/{md5}")
            else:
                print('cache found')
                # 读取缓存的元数据
                with open(f"./cache/{md5}/info.csv", 'r') as f:
                    rr = csv.reader(f)
                    for row in rr:
                        song = row[0]
                        picture = row[1]
                        chart = row[2]
                        break
                print('loading cache ...    ', end='')
                load_rpe(f"./cache/{md5}/chart.json")
                cor.SONG = f"./cache/{md5}/{song}"
                cor.IMAGE = f"./cache/{md5}/{picture}"
                print("done")
                return 0
        
        print('no cache found or in NO_CACHE_MODE')
        
        # 提取 zip
        print('extracting zip files ...    ', end='')
        if os.path.exists(f"./cache/temp"):
            shutil.rmtree(f"./cache/temp")
        os.makedirs(f"./cache/temp")
        
        with zipfile.ZipFile(zip_dir, 'r') as zf:
            zf.extractall("./cache/temp")
        
        files = os.listdir("./cache/temp")
        print('done')
        
        # 读取 info 文件
        print('reading info file ...    ', end='')
        song = ''
        picture = ''
        chart = ''
        
        info_files = [f for f in files if f.startswith("info") and f.endswith(('.csv', '.txt'))]
        if info_files:
            content = open(f"./cache/temp/{info_files[0]}", 'r', encoding='utf-8').read()
            if info_files[0].endswith('.csv'):
                for row in csv.reader(content.splitlines()):
                    song = row[0] if len(row) > 0 else ''
                    picture = row[1] if len(row) > 1 else ''
                    chart = row[2] if len(row) > 2 else ''
                    break
            else:
                for line in content.splitlines():
                    if ':' in line:
                        k, v = line.split(':', 1)
                        k = k.strip().lower()
                        v = v.strip()
                        if k == 'song': song = v
                        elif k == 'picture': picture = v
                        elif k == 'chart': chart = v
        else:
            # 如果没有 info 文件，按文件名推测
            for f in files:
                if f.endswith('.mp3') or f.endswith('.wav') or f.endswith('.ogg'):
                    song = f
                elif f.endswith('.jpg') or f.endswith('.png') or f.endswith('.jpeg'):
                    picture = f
                elif f.endswith('.json') or f.endswith('.pec') or f.endswith('.pgr'):
                    chart = f
        
        print(f'{song} / {picture} / {chart}')
        print('copying files ...    ', end='')
        
        # 创建缓存目录
        os.makedirs(f"./cache/{md5}")
        
        # 复制音频
        if song:
            shutil.copy(f"./cache/temp/{song}", f"./cache/{md5}/{song}")
        # 复制图片
        if picture:
            shutil.copy(f"./cache/temp/{picture}", f"./cache/{md5}/{picture}")
        
        print(f'audio: {song}')
        print('done')
        
        # 格式检测与加载
        print("decoding chart file ...    ", end='')
        
        file_path = f"./cache/temp/{chart}"
        
        # 判断文件类型
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(4096)
                stripped = content.strip()
                is_json = stripped.startswith('{')
                has_meta = '"META"' in content
                has_fv = '"formatVersion"' in content
        except:
            is_json = False
            has_meta = False
            has_fv = False
        
        file_ext = chart.lower().split(".")[-1] if '.' in chart else ''
        
        if file_ext == "pec" or (not is_json and file_ext not in ["rpe"]):
            # PEC 格式
            print(f"检测到PEC格式 ({file_ext})，使用pec2rpe转换...")
            try:
                pec2rpe.convert(file_path, "./cache/chart.json")
                load_rpe("./cache/chart.json")
                shutil.copy("./cache/chart.json", f"./cache/{md5}/chart.json")
            except Exception as e:
                print(f"PEC转换失败: {e}")
                try:
                    import json2rpe
                    json2rpe.convert(file_path, "./cache/chart.json")
                    load_rpe("./cache/chart.json")
                    shutil.copy("./cache/chart.json", f"./cache/{md5}/chart.json")
                except Exception as e2:
                    raise ChartError(f"无法转换文件 {chart}: PEC={e}, json2rpe={e2}")
        elif is_json:
            if has_meta:
                # 标准 RPE JSON
                print("检测到RPE格式...")
                load_rpe(file_path)
                shutil.copy(file_path, f"./cache/{md5}/chart.json")
            elif has_fv:
                # PGR 格式
                print("检测到PGR格式...")
                try:
                    import pgr2rpe
                    pgr2rpe.load_pgr_direct(file_path)
                    pgr2rpe.convert(file_path, f"./cache/{md5}/chart.json")
                except Exception as e:
                    print(f"PGR解析失败: {e}")
                    try:
                        import json2rpe
                        json2rpe.convert(file_path, "./cache/chart.json")
                        load_rpe("./cache/chart.json")
                        shutil.copy("./cache/chart.json", f"./cache/{md5}/chart.json")
                    except Exception as e2:
                        raise ChartError(f"无法解析JSON格式: PGR={e}, json2rpe={e2}")
            else:
                # 未知 JSON，尝试 PGR → json2rpe
                print("检测到未知JSON格式，尝试PGR/json2rpe...")
                try:
                    import pgr2rpe
                    pgr2rpe.load_pgr_direct(file_path)
                    pgr2rpe.convert(file_path, f"./cache/{md5}/chart.json")
                except Exception:
                    try:
                        import json2rpe
                        json2rpe.convert(file_path, "./cache/chart.json")
                        load_rpe("./cache/chart.json")
                        shutil.copy("./cache/chart.json", f"./cache/{md5}/chart.json")
                    except Exception as e:
                        raise ChartError(f"无法解析JSON {chart}: {e}")
        else:
            raise ChartError(f"未知的文件格式 {chart}")
        
        cor.SONG = f"./cache/{md5}/{song}"
        cor.IMAGE = f"./cache/{md5}/{picture}"
        print("done")
        return 0
    
    except Exception as e:
        shutil.rmtree(f"./cache/{md5}", ignore_errors=True)
        raise e
