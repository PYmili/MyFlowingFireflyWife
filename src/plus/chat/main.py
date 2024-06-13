import os
from typing import Any

from loguru import logger
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QWidget

from . import tts
from .fireflyAI import ai
from .stt import SoundRecording
from ..plus import PlusCallableType
from .manager.SttConfigManager import sttConfig

STT_NAME = sttConfig().read("stt")
logger.info(f"read Config File: {STT_NAME}")
if STT_NAME == 'funasr':
    from .stt import Funasr_STT
    STT = Funasr_STT()
else:
    from .stt import BaiduYun_STT
    STT = BaiduYun_STT()


class TTS:
    def __init__(self, text: str) -> None:
        """
        进行TTS功能
        :param text: str 需要tts的文本
        :return None
        """
        self.text = text

    def run(self) -> bool:
        """运行"""
        # 通过api生成音频
        self.tts_wav = tts.FireFlyTTS(self.text).start()
        # 播放音频
        while not tts.WavPlayer(self.tts_wav).play(): pass
        return True


class sttQThread(QThread):
    recognitionResultReady = pyqtSignal(str)
    def __init__(self) -> None:
        """
        STT 线程
        :return None
        """
        super().__init__()
        self.stt = STT
        self.ChatReusltText = ""
        self.requestInterruption = True

    def run(self) -> None:
        """运行"""
        chat = ai.Chat(self.getChatReusltCallback)
        while not self.requestInterruption:
            # 录音
            audio_bytes = SoundRecording()
            if not audio_bytes:
                continue
            
            # 开始STT
            logger.info("进行STT")
            result = self.stt.SpeechToText(
                audio_bytes
            )
            if not result:
                continue

            logger.info(result)
            
            # 唤醒关键字检查
            if "流萤" not in result:
                logger.info("未检测到唤醒，将跳过zzzzzz...")
                continue
            
            # 缓存聊天记录
            chat.addMessage(result)
            chat.run()

            # 进行TTS
            splitChatResultText = self.ChatReusltText.split("</end>")[0]
            tts = TTS(splitChatResultText, self.message_label)
            while not tts.run(): pass

            # 返回数据
            self.recognitionResultReady.emit(self.ChatReusltText)
    
    def getChatReusltCallback(self, result_json: dict) -> None:
        """
        获取ai返回数据的回调函数
        :param result_json: dict 返回的json数据
        :return None
        """
        if result_json['status_code'] != 200:
            logger.info("未获取到数据，API错误！")
            self.ChatReusltText = "未获取到数据，API错误！</end>Sadness"
            return None
        
        self.ChatReusltText = result_json['content']


class SettingWindow(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)


class main(PlusCallableType):
    @staticmethod
    def run() -> sttQThread:
        """外部调用运行"""
        return sttQThread

    @staticmethod
    def settingWindow() -> SettingWindow:
        """外部调用配置窗口"""
        return SettingWindow
