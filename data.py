import csv
import json.decoder
import shutil

import core as cor
import alterobj
import element
import os
from json import load
import zipfile
import pec2rpe
import hashlib


def list2beat(_list):
    return _list[0] + _list[1] / _list[2]


# todo: 支持 formatVersion3 - example: PUPA.json


def load_rpe(rpe_path):
    # fixme: speedObject
    fp = open(rpe_path, 'r', encoding="UTF-8")
    chart_json = load(fp)
    fp.close()

    note_num = 0

    # 加载基本信息
    cor.DURATION = 999
    cor.NAME = chart_json["META"]["name"]
    cor.ARTIST = chart_json["META"]["composer"]
    cor.CHART = chart_json["META"]["charter"]
    cor.LEVEL = chart_json["META"]["level"]
    cor.IMAGE = chart_json["META"]["background"]
    cor.SONG = chart_json["META"]["song"]
    cor.OFFSET = chart_json["META"]["offset"]
    
    # 增强谱面版本识别
    rpe_version = chart_json["META"].get("RPEVersion", "Unknown")
    format_version = chart_json.get("formatVersion", "1")
    print(f"谱面版本: RPE {rpe_version}, 格式版本: {format_version}")
    
    # 根据版本号执行不同的处理逻辑
    if format_version == "3":
        print("检测到格式版本3，应用相应解析逻辑...")
        # 这里可以添加针对formatVersion3的特殊处理
    elif format_version > "3":
        print(f"警告: 检测到未知格式版本 {format_version}，可能存在兼容性问题")
    cor.BPMLIST=alterobj.bpmList(chart_json["BPMList"])
    # 加载 秒拍转换
    cor.BeatObject = alterobj.BeatObject(
        chart_json["BPMList"]
    )

    type2note = {2: element.Hold, 1: element.Tap, 3: element.Flick, 4: element.Drag}
    x_scale = cor.NOTE_X_SCALE
    index = 0
    for judgeline_data in chart_json["judgeLineList"]:
        judge_line = element.JudgeLine()
        judge_line.id = index

        # 安全地初始化LineXObject，处理可能的easingType错误
        try:
            # 检查eventLayers是否存在
            if len(judgeline_data.get("eventLayers", [])) == 0:
                print(f"警告: 判定线 {index} 没有eventLayers数据，使用默认设置")
                judge_line.x_object = alterobj.LineXObject([])
            else:
                move_x_events = judgeline_data["eventLayers"][0].get("moveXEvents", [])
                # 增强的easingType错误处理
                filtered_events = []
                for event in move_x_events:
                    if "easingType" in event and event["easingType"] not in alterobj.easing.code2FuncDict:
                        print(f"警告: 判定线 {index} 中存在未知的easingType值 {event['easingType']}，使用默认缓动函数")
                        # 记录错误信息到日志
                        with open("log.txt", "a") as log_file:
                            log_file.write(f"[ERROR] 判定线 {index}: 未知easingType {event['easingType']} 在事件 {event}\n")
                        # 添加默认easingType
                        event["easingType"] = 0
                    filtered_events.append(event)
                judge_line.x_object = alterobj.LineXObject(filtered_events)
        except Exception as e:
            print(f"警告: 初始化判定线 {index} 的x_object时发生错误: {e}")
            judge_line.x_object = alterobj.LineXObject([])

        judge_line.y_object = alterobj.LineYObject(judgeline_data["eventLayers"][0]["moveYEvents"])
        judge_line.angle_object = alterobj.AngleObject(judgeline_data['eventLayers'][0]['rotateEvents'])
        judge_line.speed_object = alterobj.LineSpeedObject(judgeline_data['eventLayers'][0]['speedEvents'])
        judge_line.alpha_object = alterobj.AlphaObject(judgeline_data['eventLayers'][0]['alphaEvents'])
        judge_line.note_y_object = alterobj.NoteYObject(judgeline_data['eventLayers'][0]['speedEvents'])
        if judgeline_data.get("notes", False):
            for note_data in judgeline_data["notes"]:
                if not note_data["isFake"]:
                    note_num += 1
                # 2 -> Hold     1 -> Tap        3 -> Flick      4 -> Drag
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
                if note_data["type"] == 2:
                    if note_data["startTime"] == note_data["endTime"]:
                        print(note_data)
                        raise ValueError(
                            "startTime equals to endTime in Hold"
                        )
                judge_line.notes.append(note)

            judge_line.notes.sort(key=lambda _note: [_note.at, _note.id != element.Note.HOLD])

            for note in judge_line.notes:
                if note.id == element.Note.HOLD:
                    judge_line.holds.append(note)
                else:
                    judge_line.not_holds.append(note)

            for note in judge_line.notes:
                if note.above:
                    judge_line.above1.append(note)
                else:
                    judge_line.above2.append(note)

        cor.judge_line_list.append(judge_line)
        index += 1

    cor.NOTE_NUM = note_num

    # 设置 highlight 属性
    notes = []
    for judge_line in cor.judge_line_list:
        notes += judge_line.notes

    notes.sort(key=lambda x: x.at)

    temp_time = notes[0].at
    temp_notes = []

    for note in notes:
        
        if note.at == temp_time:
            temp_notes.append(note)
        else:
            if len(temp_notes) > 1:
                for _note in temp_notes:
                    _note.highlight = True
            temp_notes = [note]
            temp_time = note.at


# def load_pec(dir_path):
#     files = os.listdir(dir_path)
#
#     _id = random.randint(10000000, 99999999)
#     for file in os.listdir("./cache"):
#         if file.endswith(".json") and file.startswith("cache_"):
#             os.remove(f"./cache/{file}")
#     print(f"cache id: {_id}")
#     pec2rpe.convert(pec_path, f"./cache/cache_{_id}.json")
#     load_rpe(f"./cache/cache_{_id}.json")

class ChartError:'''一个谱面错误 A Chart Error'''

def load_dir(dir_path):
    if not os.path.exists("./cache/temp"):
        os.mkdir("./cache/temp")

    # 先压缩，并获取md5
    if os.path.exists("./cache/temp.zip"):
        os.remove("./cache/temp.zip")

    with zipfile.ZipFile("./cache/temp.zip", 'w', zipfile.ZIP_STORED) as temp_zip:
        files = os.listdir(dir_path)
        for file in files:
            temp_zip.write(dir_path + ("" if dir_path[-1] in ['\\', '/'] else "/") + file, arcname=file)

    load_zip("./cache/temp.zip")


def load_zip(zip_dir):
    print(f"loading zip: {zip_dir}")
    print(f"checking zip md5 ...    ", end="")
    # 先验证md5
    file_object = open(zip_dir, 'rb')
    file_content = file_object.read()
    file_object.close()
    file_md5 = hashlib.md5(file_content)
    md5 = file_md5.hexdigest()
    print(md5)

    if os.path.exists(f"./cache/{md5}") and not cor.NO_CACHE:
        print("cache found")
        print("loading cache ...    ", end='')
        load_rpe(f"./cache/{md5}/chart.json")

        cor.SONG = f"./cache/{md5}/{cor.SONG}"
        cor.IMAGE = f"./cache/{md5}/{cor.IMAGE}"
        print("done")

        return 0

    print("no cache found or in NO_CACHE_MODE")
    if os.path.exists("./cache/temp"):
        shutil.rmtree("./cache/temp")

    if os.path.exists(f"./cache/{md5}"):
        shutil.rmtree(f"./cache/{md5}")

    os.makedirs("./cache/temp")

    print("extracting zip files ...    ", end='')
    with zipfile.ZipFile(zip_dir, mode="r") as temp_zip:
        temp_zip.extractall("./cache/temp")
    print("done")

    print("reading info file ...    ", end='')
    # 读取 info, 获取铺面文件路径
    chart = ''
    song: str
    picture: str
    level = "Unknown. ?"
    name: str
    artist: str = "Unknown"
    creator: str = "Unknown"
    bpm: str = "Unknown"

    # 定义文件类型排除列表
    excluded_extensions = ["jpg", "jpeg", "png", "bmp", "json", "pec", "mp3", "ogg", "wav", "aac"]

    # 首先尝试读取info.txt
    info_found = False
    if os.path.exists("./cache/temp/info.txt"):
        try:
            with open("./cache/temp/info.txt", "r", encoding="gbk") as f:
                # 第一行是 #
                f.readline()
                line = f.readline()
                while line:
                    try:
                        if ": " in line:
                            key, value = line.strip().split(": ", 1)
                            # 扩展info识别关键词
                            if key.lower() in ["chart", "谱面", "铺面"]:
                                chart = value
                            elif key.lower() in ["picture", "image", "图片", "背景图"]:
                                picture = value
                            elif key.lower() in ["song", "music", "音频", "歌曲"]:
                                song = value
                            elif key.lower() in ["name", "标题", "歌曲名"]:
                                name = value
                            elif key.lower() in ["level", "难度", "等级"]:
                                level = value
                            elif key.lower() in ["artist", "艺术家", "歌手"]:
                                artist = value
                            elif key.lower() in ["creator", "作者", "谱师"]:
                                creator = value
                            elif key.lower() in ["bpm", "速度"]:
                                bpm = value
                        line = f.readline()
                    except ValueError:
                        # 如果行格式不正确，跳过
                        line = f.readline()
            info_found = True
        except UnicodeDecodeError:
            with open("./cache/temp/info.txt", "r", encoding="utf-8") as f:
                # 第一行是 #
                f.readline()
                line = f.readline()
                while line:
                    try:
                        if ": " in line:
                            key, value = line.strip().split(": ", 1)
                            # 扩展info识别关键词
                            if key.lower() in ["chart", "谱面", "铺面"]:
                                chart = value
                            elif key.lower() in ["picture", "image", "图片", "背景图"]:
                                picture = value
                            elif key.lower() in ["song", "music", "音频", "歌曲"]:
                                song = value
                            elif key.lower() in ["name", "标题", "歌曲名"]:
                                name = value
                            elif key.lower() in ["level", "难度", "等级"]:
                                level = value
                            elif key.lower() in ["artist", "艺术家", "歌手"]:
                                artist = value
                            elif key.lower() in ["creator", "作者", "谱师"]:
                                creator = value
                            elif key.lower() in ["bpm", "速度"]:
                                bpm = value
                        line = f.readline()
                    except ValueError:
                        # 如果行格式不正确，跳过
                        line = f.readline()
            info_found = True
        except Exception as e:
            print(f"读取info.txt失败: {e}")

    # 尝试读取info.csv
    if not info_found and os.path.exists("./cache/temp/info.csv"):
        try:
            with open("./cache/temp/info.csv", "r", encoding="gbk") as f:
                csv_ptr = csv.reader(f)
                next(csv_ptr)
                values = next(csv_ptr)
                try:
                    values = next(csv_ptr)
                except StopIteration:
                    # 只有两行数据
                    pass
                chart = values[0]
                song = values[1]
                picture = values[2]
                name = values[6]
                level = values[7]
                # 尝试从csv中获取更多信息
                if len(values) > 8:
                    artist = values[8] if values[8] else artist
                if len(values) > 9:
                    creator = values[9] if values[9] else creator
            info_found = True
        except UnicodeDecodeError:
            with open("./cache/temp/info.csv", "r", encoding="utf-8") as f:
                csv_ptr = csv.reader(f)
                next(csv_ptr)
                values = next(csv_ptr)
                try:
                    values = next(csv_ptr)
                except StopIteration:
                    # 只有两行数据
                    pass
                chart = values[0]
                song = values[1]
                picture = values[2]
                name = values[6]
                level = values[7]
                # 尝试从csv中获取更多信息
                if len(values) > 8:
                    artist = values[8] if values[8] else artist
                if len(values) > 9:
                    creator = values[9] if values[9] else creator
            info_found = True
        except Exception as e:
            print(f"读取info.csv失败: {e}")

    # 如果info.txt和info.csv未找到或读取失败，尝试从其他文件中读取
    if not info_found:
        print("未找到有效的info.txt或info.csv，尝试从其他文件中读取信息...")
        # 遍历所有文件
        for file in os.listdir("./cache/temp"):
            file_ext = file.split(".")[-1].lower() if "." in file else ""
            # 跳过排除的文件类型
            if file_ext in excluded_extensions:
                continue

            file_path = os.path.join("./cache/temp", file)
            # 尝试以不同编码打开文件
            for encoding in ["utf-8", "gbk", "ansi"]:
                try:
                    with open(file_path, "r", encoding=encoding) as f:
                        content = f.read()
                        # 搜索可能的info关键词
                        lines = content.split("\n")
                        for line in lines:
                            if ": " in line:
                                try:
                                    key, value = line.strip().split(": ", 1)
                                    # 使用扩展的关键词列表
                                    if key.lower() in ["chart", "谱面", "铺面"]:
                                        chart = value
                                        print(f"从{file}中找到谱面路径: {chart}")
                                    elif key.lower() in ["picture", "image", "图片", "背景图"]:
                                        picture = value
                                        print(f"从{file}中找到背景图路径: {picture}")
                                    elif key.lower() in ["song", "music", "音频", "歌曲"]:
                                        song = value
                                        print(f"从{file}中找到音频路径: {song}")
                                    elif key.lower() in ["name", "标题", "歌曲名"]:
                                        name = value
                                        print(f"从{file}中找到歌曲名: {name}")
                                    elif key.lower() in ["level", "难度", "等级"]:
                                        level = value
                                        print(f"从{file}中找到难度: {level}")
                                    elif key.lower() in ["artist", "艺术家", "歌手"]:
                                        artist = value
                                    elif key.lower() in ["creator", "作者", "谱师"]:
                                        creator = value
                                    elif key.lower() in ["bpm", "速度"]:
                                        bpm = value
                                except ValueError:
                                    continue
                        # 如果已经找到必要的信息，可以提前退出
                        if chart and song and picture and name:
                            break
                except (UnicodeDecodeError, FileNotFoundError):
                    continue
            if chart and song and picture and name:
                break

    # 如果仍然没有找到所有必要的信息，使用备用方案
    if not chart or not song or not picture or not name:
        print("无法从文件中获取完整信息，使用备用方案...")
        for file in os.listdir("./cache/temp"):
            if file.split(".")[-1].lower() in ["jpg", "jpeg", "png", "bmp"] and not picture:
                picture = file
                print(f"自动选择背景图: {picture}")
            elif file.split(".")[-1].lower() in ["json", "pec", "pez"] and not chart:
                chart = file
                name = '.'.join(file.split(".")[:-1])
                print(f"自动选择谱面: {chart}")
            elif file.split(".")[-1].lower() in ["mp3", "ogg", "wav", "aac"] and not song:
                song = file
                print(f"自动选择音频: {song}")

    print("done")

    print("copying files ...    ", end='')
    print("audio:", song)
    try:
        os.mkdir(f"./cache/{md5}")

        try:
            shutil.copy(f"./cache/temp/{song}", f"./cache/{md5}")
            shutil.copy(f"./cache/temp/{picture}", f"./cache/{md5}")
        except FileNotFoundError:
            print("error")
            # 有可能是解码异常
            # 用万能找文件法再找一次
            for file in os.listdir("./cache/temp"):
                if file.split(".")[-1].lower() in ["jpg", "jpeg", "png", "bmp"]:
                    picture = file
                elif file.split(".")[-1].lower() in ["json", "pec"]:
                    chart = file
                    name = '.'.join(file.split(".")[:-1])
                elif file.split(".")[-1].lower() in ["mp3", "ogg", "wav", "aac"]:
                    song = file
                    print("audio:", song)

            shutil.copy(f"./cache/temp/{song}", f"./cache/{md5}")
            shutil.copy(f"./cache/temp/{picture}", f"./cache/{md5}")

        print("done")

        print("decoding chart file ...    ", end='')

        try:
            # 增强谱面格式识别
            file_ext = chart.lower().split(".")[-1]
            file_path = f"./cache/temp/{chart}"
            
            # 基于文件内容的格式检测
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()
                    is_json = first_line.startswith('{') and ('META' in first_line or 'judgeLineList' in first_line)
            except:
                is_json = False
                
            if file_ext == "pec" or (not is_json and file_ext not in ["json", "rpe"]):
                print(f"检测到非RPE格式文件 ({file_ext})，尝试使用pec2rpe转换...")
                try:
                    # 调用pec2rpe进行转换
                    pec2rpe.convert(file_path, "./cache/chart.json")
                    # 转换成功后加载生成的json文件
                    load_rpe("./cache/chart.json")
                    shutil.copy("./cache/chart.json", f"./cache/{md5}/chart.json")
                except Exception as e:
                    print(f"转换失败: {e}")
                    raise ChartError(f"无法转换文件 {chart}: {e}")
            else:
                # 尝试用两种格式去加载
                try:
                    load_rpe(file_path)
                    # rpe 解析成功
                    shutil.copy(file_path, f"./cache/{md5}/chart.json")
                except json.decoder.JSONDecodeError as e:
                    print(f"RPE解析失败: {e}")
                    raise ChartError(f"无效的RPE文件 {chart}: {e}")

        except json.decoder.JSONDecodeError:
            # 不是rpe格式
            try:
                pec2rpe.convert(f"./cache/temp/{chart}", "./cache/chart.json")
                # pec 解析成功

                shutil.copy("./cache/chart.json", f"./cache/{md5}/chart.json")

                # 补全信息
                with open(f"./cache/{md5}/chart.json", "r", encoding="utf-8") as f:
                    chart_json = json.load(f)

                chart_json["META"]["level"] = level
                chart_json["META"]["song"] = song
                chart_json["META"]["background"] = picture
                chart_json["META"]["name"] = name

                with open(f"./cache/{md5}/chart.json", "w", encoding="utf-8") as f:
                    json.dump(chart_json, f)

                load_rpe(f"./cache/{md5}/chart.json")

            except ValueError or KeyError as j:
                raise ChartError(
                    "Unsupported chart format.\n{}".format(j)
                )

        cor.SONG = f"./cache/{md5}/{song}"
        cor.IMAGE = f"./cache/{md5}/{picture}"
        print("done")
        return 0

    except Exception as e:
        shutil.rmtree(f"./cache/{md5}")
        raise e


# todo: 支持官铺
# def load_json(json_path):
#     _id = random.randint(10000000, 99999999)
#     print(f"cache id: {_id}")
#     for file in os.listdir("./cache"):
#         if file.endswith(".json") and file.startswith("cache_"):
#             os.remove(f"./cache/{file}")
#     json2rpe.convert(json_path, f"./cache/cache_{_id}.json")
#     load_rpe(f"./cache/cache_{_id}.json")

if __name__ == '__main__':
    # load_dir("resources/56769032")
    pec2rpe.convert("./resources/56769032/56769032.json", "dfksj")
