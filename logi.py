from logging import *
from tkinter.messagebox import *
class Log:
    def __init__(self) -> None:
        f=open('log.txt','w');f.truncate()#清空
        basicConfig(filename='log.txt', level=INFO,format='[%(levelname)s][%(asctime)s]:%(message)s')
    def error(title:str,text:str,en_text:str) -> None:
        '''
        :error 错误
        title:报错标题 text:报错正文 en_text:报错日志正文（英语）
        '''
        title = str(title);text = str(text);en_text = str(en_text)
        showerror(title, text)
        error(en_text)
    def warning(text:str) -> None:
        '''
        :warning 警告
        text:报错日志正文（英语）
        '''
        en_text = str(text)
        error(en_text)
    def info(text:str) -> None:
        '''
        :info 日志
        text:报错日志正文（英语）
        '''
        en_text = str(text)
        info(en_text)

if __name__ == '__main__':
    Log.info()