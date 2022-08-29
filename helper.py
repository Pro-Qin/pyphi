from pydub import AudioSegment
import eyed3

def get_voice_time_secs(file_name):
    """
    获取音频文件时长
    :param file_data 文件的二进制流
    :param file_name 文件名
    """
    # 先把文件保存在本地，我试过很多包，都需要先把文件保存在本地后才能获取音频长度，初步猜测是因为这些包的代码读取的是文件本地的信息
    # with open(file_name, 'w+') as f:
    #    f.write(file_data)
    # 加载本地文件
    voice_file = eyed3.load(file_name)
    # 获取音频时长
    secs = int(voice_file.info.time_secs)
    return secs

def trans_music(name, filepath, hz):
    '''
    转换音频格式
    '''
    song = AudioSegment.from_mp3(filepath)
    song.export(name + str(hz), format=str(hz))