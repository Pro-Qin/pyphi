import core
import easing


def list2beat(_list):
    return _list[0] + _list[1] / _list[2]


class LineXObject:
    def __init__(self, events_json):
        scale = core.LINE_X_SCALE
        self.value = 0

        # 事件列表，存储了self.value的变化事件
        self.events = []

        for event in events_json:
            self.events.append(
                easing.code2FuncDict[event["easingType"]](
                    list2beat(event["startTime"]),
                    list2beat(event["endTime"]),
                    event["start"] * scale + core.WIDTH / 2,
                    event["end"] * scale + core.WIDTH / 2,
                )
            )

    def get_value(self, beat):
        # 根据self.events, 更新self.value,然后返回self.value

        # 考虑到有瞬时操作，即at == end，先不进行垃圾回收
        for event in self.events:
            if event.start_beat > beat:
                # 列表排序过了，后面的events都还没开始呢
                break

            # 代码执行到这里，说明这个event需要处理
            if event.end_beat < beat:
                # 理论上来讲这个event已经执行完毕
                # 但是Python的运行效率不可恭维
                # fixme: 求求大牛救救Python吧，运行速度慢的要死啊
                # todo: 用c++重构程序，或者设计 C-API
                # 我们要给这个event一个交代，即要让她的目的达成
                self.value = event.target
            else:
                # 这个event需要被执行，且没执行完
                # 那就让他执行呗，B话这么多的 [流汗]
                self.value = event.calculate(beat)

        # 那些瞬时event的遗言已经发表过了，现在安心垃圾回收
        while self.events and self.events[0].end_beat < beat:
            # 这个event已经结su嘞！
            self.events.pop(0)  # 小垃圾再见

        return self.value


class AlphaObject:
    def __init__(self, events_json):
        self.value = 0

        # 事件列表，存储了self.value的变化事件
        self.events = []

        for event in events_json:
            self.events.append(
                easing.code2FuncDict[event["easingType"]](
                    list2beat(event["startTime"]),
                    list2beat(event["endTime"]),
                    event["start"],
                    event["end"],
                )
            )

    def get_value(self, beat):
        # 根据self.events, 更新self.value,然后返回self.value

        # 考虑到有瞬时操作，即at == end，先不进行垃圾回收
        for event in self.events:
            if event.start_beat > beat:
                # 列表排序过了，后面的events都还没开始呢
                break

            # 代码执行到这里，说明这个event需要处理
            if event.end_beat < beat:
                # 理论上来讲这个event已经执行完毕
                # 但是Python的运行效率不可恭维
                # fixme: 求求大牛救救Python吧，运行速度慢的要死啊
                # todo: 用c++重构程序，或者设计 C-API
                # 我们要给这个event一个交代，即要让她的目的达成
                self.value = event.target
            else:
                # 这个event需要被执行，且没执行完
                # 那就让他执行呗，B话这么多的 [流汗]
                self.value = event.calculate(beat)

        # 那些瞬时event的遗言已经发表过了，现在安心垃圾回收
        while self.events and self.events[0].end_beat < beat:
            # 这个event已经结su嘞！
            self.events.pop(0)  # 小垃圾再见

        return self.value


class LineYObject:
    def __init__(self, events_json):
        scale = core.LINE_Y_SCALE
        self.value = 0

        # 事件列表，存储了self.value的变化事件
        self.events = []

        for event in events_json:
            self.events.append(
                easing.code2FuncDict[event["easingType"]](
                    list2beat(event["startTime"]),
                    list2beat(event["endTime"]),
                    event["start"] * scale + core.HEIGHT / 2,
                    event["end"] * scale + core.HEIGHT / 2,
                )
            )

    def get_value(self, beat):
        # 根据self.events, 更新self.value,然后返回self.value

        # 考虑到有瞬时操作，即at == end，先不进行垃圾回收
        for event in self.events:
            if event.start_beat > beat:
                # 列表排序过了，后面的events都还没开始呢
                break

            # 代码执行到这里，说明这个event需要处理
            if event.end_beat < beat:
                # 理论上来讲这个event已经执行完毕
                # 但是Python的运行效率不可恭维
                # fixme: 求求大牛救救Python吧，运行速度慢的要死啊
                # todo: 用c++重构程序，或者设计 C-API
                # 我们要给这个event一个交代，即要让她的目的达成
                self.value = event.target
            else:
                # 这个event需要被执行，且没执行完
                # 那就让他执行呗，B话这么多的 [流汗]
                self.value = event.calculate(beat)

        # 那些瞬时event的遗言已经发表过了，现在安心垃圾回收
        while self.events and self.events[0].end_beat < beat:
            # 这个event已经结su嘞！
            self.events.pop(0)  # 小垃圾再见

        return self.value


class AngleObject:
    def __init__(self, events_json):
        self.value = 0

        # 事件列表，存储了self.value的变化事件
        self.events = []

        for event in events_json:
            self.events.append(
                easing.code2FuncDict[event["easingType"]](
                    list2beat(event["startTime"]),
                    list2beat(event["endTime"]),
                    -event["start"],
                    -event["end"])
            )

    def get_value(self, beat):
        # 根据self.events, 更新self.value,然后返回self.value

        # 考虑到有瞬时操作，即at == end，先不进行垃圾回收
        for event in self.events:
            if event.start_beat > beat:
                # 列表排序过了，后面的events都还没开始呢
                break

            # 代码执行到这里，说明这个event需要处理
            if event.end_beat < beat:
                # 理论上来讲这个event已经执行完毕
                # 但是Python的运行效率不可恭维
                # fixme: 求求大牛救救Python吧，运行速度慢的要死啊
                # todo: 用c++重构程序，或者设计 C-API
                # 我们要给这个event一个交代，即要让她的目的达成
                self.value = event.target
            else:
                # 这个event需要被执行，且没执行完
                # 那就让他执行呗，B话这么多的 [流汗]
                self.value = event.calculate(beat)

        # 那些瞬时event的遗言已经发表过了，现在安心垃圾回收
        while self.events and self.events[0].end_beat < beat:
            # 这个event已经结su嘞！
            self.events.pop(0)  # 小垃圾再见

        return self.value


class LineSpeedObject:
    def __init__(self, events_json):
        self.value = 0

        # 事件列表，存储了self.value的变化事件
        self.events = []

        for event in events_json:
            self.events.append(
                easing.code2FuncDict[1](
                    list2beat(event['startTime']),
                    list2beat(event['endTime']),
                    event["start"],
                    event["end"],
                )
            )

    def get_value(self, beat):
        # 根据self.events, 更新self.value,然后返回self.value

        # 考虑到有瞬时操作，即at == end，先不进行垃圾回收
        for event in self.events:
            if event.start_beat > beat:
                # 列表排序过了，后面的events都还没开始呢
                break

            # 代码执行到这里，说明这个event需要处理
            if event.end_beat < beat:
                # 理论上来讲这个event已经执行完毕
                # 但是Python的运行效率不可恭维
                # fixme: 求求大牛救救Python吧，运行速度慢的要死啊
                # todo: 用c++重构程序，或者设计 C-API
                # 我们要给这个event一个交代，即要让她的目的达成
                self.value = event.target
            else:
                # 这个event需要被执行，且没执行完
                # 那就让他执行呗，B话这么多的 [流汗]
                self.value = event.calculate(beat)

        # 那些瞬时event的遗言已经发表过了，现在安心垃圾回收
        while self.events and self.events[0].end_beat < beat:
            # 这个event已经结su嘞！
            self.events.pop(0)  # 小垃圾再见

        return self.value


class BeatObject:
    """
    将以秒为单位的时间转换为Beat
    """

    def __init__(self, events_json):
        # fixme: 不支持变速
        self.value = 0

        # 事件列表，存储了self.value的变化事件
        self.events = []

        self.events.append(
            easing.code2FuncDict[1](
                0, core.DURATION, 0, core.DURATION*events_json[0]["bpm"]
            )
        )

    def get_value(self, beat):
        # 根据self.events, 更新self.value,然后返回self.value

        for event in self.events:
            if event.start_beat > beat:
                # 列表排序过了，后面的events都还没开始呢
                break

            # 代码执行到这里，说明这个event需要处理
            if event.end_beat < beat:
                # 理论上来讲这个event已经执行完毕
                # 但是Python的运行效率不可恭维
                # fixme: 求求大牛救救Python吧，运行速度慢的要死啊
                # todo: 用c++重构程序，或者设计 C-API
                # 我们要给这个event一个交代，即要让她的目的达成
                self.value = event.target
            else:
                # 这个event需要被执行，且没执行完
                # 那就让他执行呗，B话这么多的 [流汗]
                self.value = event.calculate(beat)

        return self.value


class NoteYObject:
    def __init__(self, events_json):
        scale = core.SPEED_SCALE
        self.value = 0

        # 事件列表，存储了self.value的变化事件
        self.events = []

        tmp_value = 0
        index = 0
        for event in events_json[:-1]:
            target = tmp_value + event["start"] * (
                    list2beat(events_json[index+1]["startTime"]) - list2beat(event["startTime"])) * scale

            self.events.append(easing.code2FuncDict[1](
                list2beat(event["startTime"]),
                list2beat(events_json[index + 1]["startTime"]),
                tmp_value,
                target,
            ))

            index += 1
            tmp_value = target

        self.events.append(
            easing.code2FuncDict[1](
                list2beat(events_json[-1]["startTime"]),
                core.DURATION,
                tmp_value,
                tmp_value + (core.DURATION - list2beat(events_json[-1]["startTime"])) * events_json[-1]["start"] * scale
            )
        )

    def _get_value(self, beat):
        # 根据self.events, 更新self.value,然后返回self.value
        # 不进行垃圾回收

        for event in self.events:
            if event.start_beat > beat:
                # 列表排序过了，后面的events都还没开始呢
                break

            # 代码执行到这里，说明这个event需要处理
            if event.end_beat < beat:
                # 理论上来讲这个event已经执行完毕
                # 但是Python的运行效率不可恭维
                # fixme: 求求大牛救救Python吧，运行速度慢的要死啊
                # todo: 用c++重构程序，或者设计 C-API
                # 我们要给这个event一个交代，即要让她的目的达成
                self.value = event.target
            else:
                # 这个event需要被执行，且没执行完
                # 那就让他执行呗，B话这么多的 [流汗]
                self.value = event.calculate(beat)

        return self.value

    def get_value(self, at, end):
        return self._get_value(end) - self._get_value(at)
