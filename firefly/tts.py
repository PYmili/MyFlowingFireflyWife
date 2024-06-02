import os
import json
import wave
import subprocess
from typing import Union

from PyQt5.QtWidgets import QLabel
import requests
import pyaudio
from loguru import logger
from .liuying_gpt_sovits import StartLiuYingGPTSovites
from .configuration import Configuration


class FireFlyTTS:
    def __init__(self, content: str) -> None:
        """
        通过 API 生成tts音频链接
        :param content: str 需要生成的文字
        :return None
        """
        logger.info(f"TTS -> {content}")
        self.content = content
        
        # 读取配置文件
        self.configuration = Configuration()
        self.configuration.read()

    def start(self) -> Union[str, None]:
        """
        运行
        :return Union[str, None]
        """
        self.tts_wav = StartLiuYingGPTSovites(
            content=self.content,
            sessionHash=self.configuration.sessionHash,
            studioToken=self.configuration.studioToken
        )
        if not self.tts_wav:
            logger.error("未获取到tts wav")
            return None
        logger.info(self.tts_wav)
        # WavPlayer(os.path.join(os.getcwd(), "result_audio.wav")).play()
        # FFplayPlay(tts_wav).play()
        return self.tts_wav


class WavPlayer:
    def __init__(self, wav_file: str) -> None:
        logger.info("Playing Wav File: " + wav_file)
        self.wav_file_fp = wave.open(wav_file, 'rb')  # 打开WAV文件
        # 获取WAV文件的参数
        self.channels = self.wav_file_fp.getnchannels()  # 获取声道数
        self.sample_width = self.wav_file_fp.getsampwidth()  # 获取样本宽度（字节）
        self.framerate = self.wav_file_fp.getframerate()  # 获取采样率（Hz）
        self.frames = self.wav_file_fp.getnframes()  # 获取总帧数

        self.pyaudioObject = pyaudio.PyAudio()  # 创建PyAudio对象

    def play(self) -> bool:
        stream = self.pyaudioObject.open(
            format=self.pyaudioObject.get_format_from_width(self.sample_width),  # 获取与样本宽度对应的PyAudio格式
            channels=self.channels,  # 设置声道数
            rate=self.framerate,  # 设置采样率
            output=True  # 指定为输出流（播放）
        )

        # 循环读取WAV数据并写入流
        data = self.wav_file_fp.readframes(4096)  # 一次读取1024帧（可根据需要调整）
        while data:  # 当还有数据未读完时
            stream.write(data)  # 将数据写入音频流
            data = self.wav_file_fp.readframes(4096)  # 继续读取下一组1024帧

        # 关闭流和PyAudio对象
        stream.stop_stream()  # 停止音频流
        stream.close()  # 关闭音频流
        self.pyaudioObject.terminate()  # 关闭PyAudio对象
        return True


class FFplayPlay:
    def __init__(self, audio_path: str) -> None:
        """
        使用FFplay播放音频
        :param audio_url: str 需要播放的音频URL
        """
        self.audio_path = audio_path

    def play(self) -> None:
        """
        播放音频
        """
        if os.name == 'nt':  # Windows platform
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW  # 隐藏控制台窗口
            process = subprocess.Popen(
                ['ffplay', '-nodisp', '-autoexit', self.audio_path],
                startupinfo=startupinfo
            )
        else:  # Unix-like platforms (Linux, macOS)
            with open(os.devnull, 'w') as devnull:
                process = subprocess.Popen(
                    ['ffplay', '-nodisp', '-autoexit', self.audio_path],
                    stdout=devnull, stderr=devnull
                )

        # 等待ffplay进程结束（由于指定了-autoexit，它会在播放完毕后自动退出）
        process.wait()


# WavPlayer(os.path.join(os.getcwd(), "result_audio.wav")).play()
# FireFlyTTS("你好！").play()