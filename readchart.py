import readfile
import ast

class chart():
    def init(gamename:str):
        '''初始化识别谱面'''
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
        with open(readfile.lookfile(gamename)['chart'],mode='r') as f:
            data = ast.literal_eval(f.readlines()[0])#转换为字典
        f.close()
        formatVersion = data['formatVersion']   #版本(1-3)
        offset        = data['offset']          #歌曲播放延迟
        numOfNotes    = data['numOfNotes']      #物量
        judgeLineList = data['judgeLineList']   #判定线与note信息
        return numOfNotes,judgeLineList




if __name__ == '__main__':
    chart.init('volcanic')
    0/0