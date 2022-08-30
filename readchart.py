import readfile
import ast


class chart():
    def init(gamename: str) -> dict:
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


if __name__ == '__main__':
    chart.init('volcanic')
    0/0
