import readfile
import ast
import json
import core
import alterobj
import element


def load_pyphi(gamename: str) -> dict:
    '''初始化识别谱面'''
    renderer = {  # 存放谱面
        'chart': None,
        'bgImage': None,
        'bgImageBlur': None,
        'bgMusic': None,
        'lines': [],
        'notes': [],
        'taps': [],
        'drags': [],
        'flicks': [],
        'holds': [],
        'reverseholds': [],
        'tapholds': []
    }
    mouse = {}  # 存放鼠标事件(用于检测，下同)
    touch = {}  # 存放触摸事件
    keyboard = {}  # 存放键盘事件
    taps = []  # 额外处理tap(试图修复吃音bug)
    with open(readfile.lookfile(gamename)['chart'], mode='r') as f:
        data = ast.literal_eval(f.readlines()[0])  # 转换为字典
    f.close()
    '''
    在这里讲一下data内容:(格式: pyphi名 解释 类型 范围 其他)
        offset 音乐播放延迟 浮点数
        numOfNotes 物量 整数
        noteList note信息放置 列表
            01 字典
                type 类型 整数 (0=Tap 1=Drag 2=Flick 3=Hold)
                speed 速度 浮点数 (0.0 - 1.0)
                linenum 绑定的判定线编号 整数 (0 - ?)
                relaposX 掉落在判定线的相对X 浮点数 (-?.?? - ?.??)
                passtime 判定时间 浮点数 (0.000 - ?.???)
                *startime 开始时间 浮点数 (0.000 - ?.???) [Hold]
                *endtime 结束时间 浮点数 (0.000 - ?.???) [Hold]
            02 字典
                ...
        LineList 判定线信息放置 列表
            01 字典 (编号顺序-1即为判定线编号)
                pos 坐标 元组(x,y)
                alpha 透明度 整数 (0-100)
                event
    '''
    offset = data['offset']
    numOfNotes = data['numOfNotes']
    return data


def list2beat(_list):
    return _list[0] + _list[1] / _list[2]


def load_rpe(gamename: str):
    # fixme: speedObject
    fp = open(readfile.lookfile(gamename)['chart'], 'r', encoding="UTF-8")
    chart_json = json.load(fp)
    fp.close()

    note_num = 0

    # 加载基本信息
    core.DURATION = 999
    core.NAME = chart_json["META"]["name"]
    core.ARTIST = chart_json["META"]["composer"]
    core.CHART = chart_json["META"]["charter"]
    core.LEVEL = chart_json["META"]["level"]
    core.IMAGE = chart_json["META"]["background"]
    core.SONG = chart_json["META"]["song"]
    core.OFFSET = chart_json["META"]["offset"]

    # 加载 秒拍转换
    core.BeatObject = alterobj.BeatObject(
        chart_json["BPMList"]
    )

    type2note = {2: element.Hold, 1: element.Tap,
                 3: element.Flick, 4: element.Drag}
    x_scale = core.NOTE_X_SCALE
    index = 0
    for judgeline_data in chart_json["judgeLineList"]:
        judge_line = element.JudgeLine()
        judge_line.id = index

        judge_line.x_object = alterobj.LineXObject(
            judgeline_data["eventLayers"][0]["moveXEvents"])
        judge_line.y_object = alterobj.LineYObject(
            judgeline_data["eventLayers"][0]["moveYEvents"])
        judge_line.angle_object = alterobj.AngleObject(
            judgeline_data['eventLayers'][0]['rotateEvents'])
        # judge_line.speed_object = alterobj.LineSpeedObject(judgeline_data['eventLayers'][0]['speedEvents'])
        judge_line.alpha_object = alterobj.AlphaObject(
            judgeline_data['eventLayers'][0]['alphaEvents'])
        judge_line.note_y_object = alterobj.NoteYObject(
            judgeline_data['eventLayers'][0]['speedEvents'])
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
                    True if note_data["isFake"] else False
                )
                if note_data["type"] == 2:
                    if note_data["startTime"] == note_data["endTime"]:
                        print(note_data)
                        raise ValueError(
                            "startTime equals to endTime in Hold"
                        )
                judge_line.notes.append(note)

            judge_line.notes.sort(
                key=lambda _note: [_note.at, _note.id != element.Note.HOLD])

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

        core.judge_line_list.append(judge_line)
        index += 1

    core.NOTE_NUM = note_num

    # 设置 highlight 属性
    notes = []
    for judge_line in core.judge_line_list:
        notes += judge_line.notes

    notes.sort(key=lambda x: x.at)

    temp_time = notes[0].at
    temp_notes = []

    for note in notes:
        if note.fake:
            note.highlight = True
        if note.at == temp_time:
            temp_notes.append(note)
        else:
            if len(temp_notes) > 1:
                for _note in temp_notes:
                    _note.highlight = True
            temp_notes = [note]
            temp_time = note.at


if __name__ == '__main__':
    load_pyphi('volcanic')
    0/0
