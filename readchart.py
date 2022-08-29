import readfile

class chart():
    def init(gamename):
        renderer = {#存放谱面
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
        mouse = {}#存放鼠标事件(用于检测，下同)
        touch = {}#存放触摸事件
        keyboard = {}#存放键盘事件
        taps = []#额外处理tap(试图修复吃音bug)
        data = readfile.lookfile(gamename)
    