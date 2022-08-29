
import csv


def lookfile(gamename: str) -> dict:
    """
    根据传入的游戏名获取其相关属性
    :param gamename: 待查找的游戏名
    :return: 该铺面的数据 格式：
        filedata = {'谱面':'', '音乐':'', '图片':'', '宽高比':'', '按键缩放':'', '背景变暗':'', '名称':'', '等级':'', '曲绘':'', '谱师':''}
    """
    num=0
    data = []
    filedata = {'谱面':'', '音乐':'', '图片':'', '宽高比':'', '按键缩放':'', '背景变暗':'', '名称':'', '等级':'', '曲绘':'', '谱师':''}
    #csv_reader = csv.reader(open('preset/{}/{}'.format(gamename,'info.csv'),encoding='ISO-8859-1'))#打开文件 'preset/Terrasphere/info.csv'
    file = open('preset/{}/{}'.format(gamename,'info.csv')).readlines()#是个列表
    #for row in csv_reader:#读取文件
    #    data.append(row)

    
    FileCN = file[1].split(',')
    FileData = file[2].split(',')
    FileCN[-1] = FileCN[-1][:-1]
    for i in range(len(FileCN)):
        #分类
        filedata[str(FileCN[num])] = FileData[num]
        num+=1

    return filedata


if __name__ == '__main__':
    print(lookfile('Terrasphere'))