"""
author: xi2p
Inspired from https://github.com/Anslate/Phi_Chart_Transform
"""

import json
import math
import sys


def to_rpe_note_x(n):
    return n * 0.9 * 0.7 * 0.9 * 1.2 * 0.95


def to_float_time(n: list):
    return n[0] + n[1] / n[2]


def to_rpe_line_x(n):
    k = 625
    return -k + n * k * 2 / 2048


def to_rpe_line_y(n):
    k = 460
    return -k + n * k*2 / 1400


def to_rpe_line_speed(n):
    return n / (77 / 6) * 6.5 * 0.7 * 35 / 25


def to_rpe_time(n):
    return [math.floor(n), int(n * 32) % 32, 32]


def convert(pec_path, rpe_path):
    pec_file = open(pec_path, "r", encoding="UTF-8")
    rpe_chart = {
        "BPMList": [],
        "META": {
            # todo: 读取info.txt/info.csv来补充缺省的信息
            "RPEVersion": 100,
            "background": "Unknown.jpg",
            "charter": "Unknown",
            "composer": "Unknown",
            "id": "10000001",
            "level": "Unknown",
            "name": "Unknown",
            "offset": int(pec_file.readline().strip()),
            "song": "Unknown.mp3"
        },
        "judgeLineGroup": ["Default"],
        "judgeLineList": []
    }
    move_x_list = []
    move_y_list = []
    rotate_list = []
    alpha_list = []
    speed_list = []
    note_list = []
    # 先统计出判定线数量
    judge_line_num = 0

    line = pec_file.readline()
    while line:
        line = line.strip()
        if line:
            blocks = line.split(" ")
            if blocks[0] not in ["bp", "#", "&"]:  # 除了设置bpm外，所有语句的blocks[1]都是判定线编号
                judge_line_num = max(int(blocks[1]), judge_line_num)
        line = pec_file.readline()

    judge_line_num += 1
    for i in range(judge_line_num):
        rpe_chart["judgeLineList"].append({
            "Group": 0,
            "Name": "Untitled",
            "Texture": "line.png",
            "eventLayers": [
                {
                    "alphaEvents": [],
                    "moveXEvents": [],
                    "moveYEvents": [],
                    "rotateEvents": [],
                    "speedEvents": [],
                }
            ],
            "isCover": 1,
            "notes": [],
            "numOfNotes": 0
        })
        move_x_list.append([])
        move_y_list.append([])
        rotate_list.append([])
        alpha_list.append([])
        speed_list.append([])
        note_list.append([])

    pec_file.seek(0)
    pec_file.readline()

    line = pec_file.readline()
    while line:
        line = line.strip()
        if not line:
            line = pec_file.readline()
            continue

        blocks = line.split(" ")
        if blocks[0] == "bp":  # 设置bpm
            rpe_chart["BPMList"].append({
                "bpm": float(blocks[2]),
                "startTime": [float(blocks[1]), 0, 1]
            })
        elif blocks[0] == "cp":  # 判定线瞬间移动
            move_x_list[int(blocks[1])].append(
                {
                    "easingType": 1,
                    "end": to_rpe_line_x(float(blocks[3])),
                    "endTime": to_rpe_time(float(blocks[2])),
                    "linkgroup": 0,
                    "start": to_rpe_line_x(float(blocks[3])),
                    "startTime": to_rpe_time(float(blocks[2]))
                }
            )
            move_y_list[int(blocks[1])].append(
                {
                    "easingType": 1,
                    "end": to_rpe_line_y(float(blocks[4])),
                    "endTime": to_rpe_time(float(blocks[2])),
                    "linkgroup": 0,
                    "start": to_rpe_line_y(float(blocks[4])),
                    "startTime": to_rpe_time(float(blocks[2]))
                }
            )
        elif blocks[0] == "cm":  # 判定线缓动
            move_x_list[int(blocks[1])].append(
                {
                    "easingType": int(blocks[6]),
                    "end": to_rpe_line_x(float(blocks[4])),
                    "endTime": to_rpe_time(float(blocks[3])),
                    "linkgroup": 0,
                    "start": -1,
                    "startTime": to_rpe_time(float(blocks[2]))
                }
            )
            move_y_list[int(blocks[1])].append(
                {
                    "easingType": int(blocks[6]),
                    "end": to_rpe_line_y(float(blocks[5])),
                    "endTime": to_rpe_time(float(blocks[3])),
                    "linkgroup": 0,
                    "start": -1,
                    "startTime": to_rpe_time(float(blocks[2]))
                }
            )
        elif blocks[0] == "cd":  # 判定线角度瞬时变化
            rotate_list[int(blocks[1])].append(
                {
                    "easingType": 1,
                    "end": float(blocks[3]),
                    "endTime": to_rpe_time(float(blocks[2])),
                    "linkgroup": 0,
                    "start": float(blocks[3]),
                    "startTime": to_rpe_time(float(blocks[2]))
                }
            )
        elif blocks[0] == "cr":  # 判定线旋转缓动
            rotate_list[int(blocks[1])].append(
                {
                    "easingType": int(blocks[5]),
                    "end": float(blocks[4]),
                    "endTime": to_rpe_time(float(blocks[3])),
                    "linkgroup": 0,
                    "start": -1,
                    "startTime": to_rpe_time(float(blocks[2]))
                }
            )
        elif blocks[0] == "ca":  # 判定线alpha瞬时变化
            value = float(blocks[3])

            alpha_list[int(blocks[1])].append(
                {
                    "easingType": 1,
                    "end": value,
                    "endTime": to_rpe_time(float(blocks[2])),
                    "linkgroup": 0,
                    "start": value,
                    "startTime": to_rpe_time(float(blocks[2]))
                }
            )
        elif blocks[0] == "cf":  # 判定线alpha缓动
            value = float(blocks[4])

            alpha_list[int(blocks[1])].append(
                {
                    "easingType": 1,
                    "end": value,
                    "endTime": to_rpe_time(float(blocks[3])),
                    "linkgroup": 0,
                    "start": -1,
                    "startTime": to_rpe_time(float(blocks[2]))
                }
            )
        elif blocks[0] == "cv":  # 判定线speed瞬时变化
            speed_list[int(blocks[1])].append(
                {
                    "end": to_rpe_line_speed(float(blocks[3])),
                    "endTime": to_rpe_time(float(blocks[2])),
                    "linkgroup": 0,
                    "start": to_rpe_line_speed(float(blocks[3])),
                    "startTime": to_rpe_time(float(blocks[2]))
                }
            )
        elif blocks[0] == "n1":
            note_list[int(blocks[1])].append(
                {
                    "above": 1 if int(blocks[4]) == 1 else 2,
                    "alpha": 255,
                    "endTime": to_rpe_time(float(blocks[2])),
                    "isFake": int(blocks[5]),
                    "positionX": to_rpe_note_x(float(blocks[3])),
                    "size": 1.0,
                    "speed": 1.0,
                    "startTime": to_rpe_time(float(blocks[2])),
                    "type": 1,
                    "visibleTime": 999999.0,
                    "yOffset": 0.0
                }
            )
            note_list[int(blocks[1])][-1]["speed"] = \
                float(pec_file.readline().strip().split(" ")[-1])
            note_list[int(blocks[1])][-1]["size"] = \
                float(pec_file.readline().strip().split(" ")[-1])
            rpe_chart["judgeLineList"][int(blocks[1])]["numOfNotes"] += 1


        elif blocks[0] == "n2":
            note_list[int(blocks[1])].append(
                {
                    "above": 1 if int(blocks[5]) == 1 else 2,
                    "alpha": 255,
                    "endTime": to_rpe_time(float(blocks[3])),
                    "isFake": int(blocks[6]),
                    "positionX": to_rpe_note_x(float(blocks[4])),
                    "size": 1.0,
                    "speed": 1.0,
                    "startTime": to_rpe_time(float(blocks[2])),
                    "type": 2,
                    "visibleTime": 999999.0,
                    "yOffset": 0.0
                }
            )

            note_list[int(blocks[1])][-1]["speed"] = \
                float(pec_file.readline().strip().split(" ")[-1])
            note_list[int(blocks[1])][-1]["size"] = \
                float(pec_file.readline().strip().split(" ")[-1])
            rpe_chart["judgeLineList"][int(blocks[1])]["numOfNotes"] += 1


        elif blocks[0] == "n3":
            note_list[int(blocks[1])].append(
                {
                    "above": 1 if int(blocks[4]) == 1 else 2,
                    "alpha": 255,
                    "endTime": to_rpe_time(float(blocks[2])),
                    "isFake": int(blocks[5]),
                    "positionX": to_rpe_note_x(float(blocks[3])),
                    "size": 1.0,
                    "speed": 1.0,
                    "startTime": to_rpe_time(float(blocks[2])),
                    "type": 3,
                    "visibleTime": 999999.0,
                    "yOffset": 0.0
                }
            )
            note_list[int(blocks[1])][-1]["speed"] = \
                float(pec_file.readline().strip().split(" ")[-1])
            note_list[int(blocks[1])][-1]["size"] = \
                float(pec_file.readline().strip().split(" ")[-1])
            rpe_chart["judgeLineList"][int(blocks[1])]["numOfNotes"] += 1


        elif blocks[0] == "n4":
            note_list[int(blocks[1])].append(
                {
                    "above": 1 if int(blocks[4]) == 1 else 2,
                    "alpha": 255,
                    "endTime": to_rpe_time(float(blocks[2])),
                    "isFake": int(blocks[5]),
                    "positionX": to_rpe_note_x(float(blocks[3])),
                    "size": 1.0,
                    "speed": 1.0,
                    "startTime": to_rpe_time(float(blocks[2])),
                    "type": 4,
                    "visibleTime": 999999.0,
                    "yOffset": 0.0
                }
            )
            note_list[int(blocks[1])][-1]["speed"] = \
                float(pec_file.readline().strip().split(" ")[-1])
            note_list[int(blocks[1])][-1]["size"] = \
                float(pec_file.readline().strip().split(" ")[-1])
            rpe_chart["judgeLineList"][int(blocks[1])]["numOfNotes"] += 1


        line = pec_file.readline()

    for i in range(judge_line_num):
        for _list in [move_x_list, move_y_list, rotate_list, alpha_list]:
            _list[i].sort(key=lambda x: [x["startTime"], x["startTime"] != x["endTime"]])
            if _list[i][0]["start"] == -1:
                _list[i][0]["start"] = 0
            index = 1
            for _dict in _list[i][1:]:
                if _list[i][index]["start"] == -1:
                    _list[i][index]["start"] = _list[i][index-1]["end"]
                index += 1

        speed_list[i].sort(key=lambda x: x["startTime"])
        note_list[i].sort(key=lambda x: x["startTime"])

        for _dict in move_x_list[i]:
            rpe_chart["judgeLineList"][i]["eventLayers"][0]["moveXEvents"].append(_dict)

        for _dict in move_y_list[i]:
            rpe_chart["judgeLineList"][i]["eventLayers"][0]["moveYEvents"].append(_dict)

        for _dict in rotate_list[i]:
            rpe_chart["judgeLineList"][i]["eventLayers"][0]["rotateEvents"].append(_dict)

        for _dict in alpha_list[i]:
            rpe_chart["judgeLineList"][i]["eventLayers"][0]["alphaEvents"].append(_dict)

        for _dict in speed_list[i]:
            rpe_chart["judgeLineList"][i]["eventLayers"][0]["speedEvents"].append(_dict)

        for _dict in note_list[i]:
            rpe_chart["judgeLineList"][i]["notes"].append(_dict)

    with open(rpe_path, "w", encoding="UTF-8") as rpe_file:
        json.dump(rpe_chart, rpe_file)

    pec_file.close()


if __name__ == '__main__':
    convert(sys.argv[1], sys.argv[2])
