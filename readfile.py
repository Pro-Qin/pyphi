from tkinter import messagebox  # 显示错误信息用的
import os
'''Made By OAO'''

def csvLoad(csvPath: str) -> list:  # 解析csv文件
    with open(csvPath, "r", encoding="utf-8") as csv:
        return csv.read().split(",")


def lookfile(name: str):  # 给一个名字，自动匹配
    '''自动根据所给的歌曲名寻找音乐、铺面、图片等文件'''
    info = {}  # 存储谱面的信息，也是返回的值

    music = [".mp3", ".wav"]        # 音乐文件，用于接下来的自动读取，方便添加与修改
    chart = [".pec", ".json"]       # 谱面文件
    picture = [".png", ".jpg",]     # 图片文件
    csv = [".csv"]
    csvRead = True  # csv文件是否读取?
    path = 'preset/'+name
    for file in os.listdir(path):  # 遍历
        fileType = os.path.splitext(file)[1]  # 记录每个文件的扩展名（后缀名），用于识别每个文件的用处，后面的[1]很关键!!!
        filePath = os.path.join(path, file)  # 文件的绝对路径

        if fileType in music:
            info["music"] = filePath  # 把信息添加进字典里，备用
        elif fileType in chart:
            info["chart"] = filePath
        elif fileType in picture:
            info["picture"] = filePath
        elif fileType in csv:
            info["other"] = csvLoad(filePath)
            csvRead = True
    
    if csvRead == False:
        info["other"] = ["0", "0", "0", "0"]  # 没csv的后果
    
        
    """
    这边稍微讲一下，我的新格式读取完是这样的：
    {'music': './preset\\Terrasphere\\Terrasphere.mp3', 'chart': './preset\\Terrasphere\\Terrasphere.pec', 'picture': './preset\\Terrasphere\\Terrasphere.png', 'other': [曲名, 难度, 曲师, 谱师]}

    （other那边你自己理解）
    也就是说，返回的值是这样的一个字典

    比如：
    在main.py里要加载一个音乐

    就这样写：
    info_data["music"]

    就好了，很方便

    *谱面、音乐、背景图片、csv 这几个文件是自动读取的，支持的格式对应上面的几个列表；其中前三个是必须的，否则程序跑不起来，会报错

    """

    return info


if __name__ == '__main__':
    print(lookfile('volcanic'))
