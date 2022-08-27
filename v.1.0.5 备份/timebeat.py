import pygame
import math
import time

d = str
#d是json文件提取出的字典
meta=d["META"]
bpml=d["BPMList"]

bpml.sort(key=lambda x:x["startTime"][0]+x["startTime"][1]/x["startTime"][2])#排序

startTimes=list(map(lambda x:x["startTime"][0]+x["startTime"][1]/x["startTime"][2],bpml))#开始时间
bpms=list(map(lambda x:x["bpm"],bpml))#bpm的值
spaces=list(startTimes[i+1]-startTimes[i] for i in range(len(startTimes)-1))#bpm切换间隔
spaces.append(math.inf)#最后加个无穷大
bpss=list(map(lambda x:x/60,bpms))#把bpm转换成bps

def time():return(pygame.time.get_ticks()-ot)/1000#获取开始后的时间（秒）
def beat():#获取开始后的拍数
    t=time();b=0#初始化
    for k in range(len(bpss)):#迭代
        i=spaces[k]#（迭代为什么要用range（
        if t>i:#在经过之后的
            b+=i*bpss[k]#拍都加上去
            t-=i#减去然后下一个
        else:#之间的
            b+=t*bpss[k]#已经过的加上去
            return b#后面的还没到，直接跳过
    return time()/60*bpml[0]["bpm"]
    
#音乐初始化之后立刻执行
ot=pygame.time.get_ticks()+meta["offset"]

