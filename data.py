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

        judge_line.x_object = alterobj.LineXObject(judgeline_data["eventLayers"][0]["moveXEvents"])
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

    if os.path.exists("./cache/temp/info.txt"):
        try:
            with open("./cache/temp/info.txt", "r", encoding="gbk") as f:
                # 第一行是 #
                f.readline()
                line = f.readline()
                while line:
                    key, value = line.strip().split(": ")
                    if key == "Chart":
                        chart = value
                    elif key == "Picture":
                        picture = value
                    elif key == "Song":
                        song = value
                    elif key == "Name":
                        name = value
                    elif key == "Level":
                        level = value
                    line = f.readline()
        except UnicodeDecodeError:
            with open("./cache/temp/info.txt", "r", encoding="utf-8") as f:
                # 第一行是 #
                f.readline()
                line = f.readline()
                while line:
                    key, value = line.strip().split(": ")
                    if key == "Chart":
                        chart = value
                    elif key == "Picture":
                        picture = value
                    elif key == "Song":
                        song = value
                    elif key == "Name":
                        name = value
                    elif key == "Level":
                        level = value
                    line = f.readline()

    elif os.path.exists("./cache/temp/info.csv"):
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

    else:
        # raise FileNotFoundError(
        #     "Unsupported pack format: info.txt or info.csv is required."
        # )
        for file in os.listdir("./cache/temp"):
            if file.split(".")[-1].lower() in ["jpg", "jpeg", "png", "bmp"]:
                picture = file
            elif file.split(".")[-1].lower() in ["json", "pec"]:
                chart = file
                name = '.'.join(file.split(".")[:-1])
            elif file.split(".")[-1].lower() in ["mp3", "ogg", "wav", "aac"]:
                song = file

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
            # 尝试用两种格式去加载
            load_rpe(f"./cache/temp/{chart}")

            # rpe 解析成功
            shutil.copy(f"./cache/temp/{chart}", f"./cache/{md5}/chart.json")

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

            except ValueError:
                raise ValueError(
                    "Unsupported chart format."
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
