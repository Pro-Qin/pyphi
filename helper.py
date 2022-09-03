from pydub import AudioSegment
from tinytag import TinyTag

def get_voice_time_secs(file_name):
    """
    获取音频文件时长
    :param file_name 文件名
    """
    # 先把文件保存在本地，我试过很多包，都需要先把文件保存在本地后才能获取音频长度，初步猜测是因为这些包的代码读取的是文件本地的信息
    # with open(file_name, 'w+') as f:
    #    f.write(file_data)
    # 加载本地文件
    #voice_file = eyed3.load(file_name)
    # 获取音频时长
    #secs = int(voice_file.info.time_secs)
    #return secs
    tag = TinyTag.get(file_name)
    return tag.duration       #歌曲时长

def trans_music(name, filepath, hz):
    '''
    转换音频格式
    '''
    song = AudioSegment.from_mp3(filepath)
    song.export(name + str(hz), format=str(hz))

def ccap(pos:tuple,width=0,height=0,window_x=960,window_y=540):
    '''
    计算中心锚点
    :Computing center anchor point
    :pos为元组
    :window_x 窗口x
    :window_y 窗口y
    :width    宽度
    :height   高度
    '''
    x = pos[0]
    y = pos[1]
    return (window_x/2+x+width/2,window_y/2+y+height/2)
    





if __name__ == '__main__':
    print(ccap((0,0)))