import sys
from tkinter.messagebox import showinfo, showwarning, showerror, askyesno

def lookfile(gamename):#剖析文件
    num=0
    data = []
    filedata = {'谱面':'', '音乐':'', '图片':'', '宽高比':'', '按键缩放':'', '背景变暗':'', '名称':'', '等级':'', '曲绘':'', '谱师':''}
    #csv_reader = csv.reader(open('preset/{}/{}'.format(gamename,'info.csv'),encoding='ISO-8859-1'))#打开文件 'preset/Terrasphere/info.csv'
    try:
        file = open('preset/{}/{}'.format(gamename,'info.csv'), encoding="utf-8").readlines()#是个列表
    except FileNotFoundError:
        showerror('没有谱面文件','根目录未找到名字为{}的谱面'.format(gamename))
        sys.exit()
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