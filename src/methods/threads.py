import os
import json
from typing import Union

import requests
from loguru import logger
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QLabel

from ..firefly import (
    gpt,
    tts
)
from .VoiceToText import (
    BaiduYun_STT,
    Funasr_STT,
    SoundRecording
)
from .sttConfigManager import sttConfig

CURRNT_DIR = os.getcwd()


def loadingSTT() -> Union[BaiduYun_STT, Funasr_STT]:
    """
    对STT配置进行加载。
    :return STT_OBJECT
    """
    sttData = sttConfig().read("stt")
    logger.info(f"read Config File: {sttData}")
    stt = BaiduYun_STT()
    if sttData == 'funasr':
        stt = Funasr_STT()
    else:
        stt = BaiduYun_STT()

    return stt


class TTS:
    def __init__(self, text: str, message_label: QLabel) -> None:
        """
        进行TTS功能
        :param text: str 需要tts的文本
        :param message_label: QLabel 传入QLabel用来更新界面表情图片
        :return None
        """
        self.text = text
        self.message_label = message_label

    def run(self) -> bool:
        """运行"""
        # 通过api生成音频
        self.tts_wav = tts.FireFlyTTS(self.text).start()
        # 对message_label进行更新文本
        self.message_label.setWordWrap(True)
        self.message_label.setText(self.text)
        self.message_label.adjustSize()
        self.message_label.show()
        # 播放音频
        while not tts.WavPlayer(self.tts_wav).play(): pass
        return True


class sttQThread(QThread):
    recognitionResultReady = pyqtSignal(str)
    def __init__(self, stt_func: loadingSTT, message_label: QLabel) -> None:
        """
        STT 线程
        :param stt_func: function 需要使用的stt方法
        :param message_label: QLabel 用于更新主界面表情
        :return None
        """
        super().__init__()
        self.stt = stt_func
        self.message_label = message_label
        self.ChatReusltText = ""

    def run(self) -> None:
        """运行"""
        chat = gpt.Chat(self.getChatReusltCallback)
        while True:
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
        获取gpt返回数据的回调函数
        :param result_json: dict 返回的json数据
        :return None
        """
        if result_json['status_code'] != 200:
            logger.info("未获取到数据，API错误！")
            self.ChatReusltText = "未获取到数据，API错误！</end>Sadness"
            return None
        
        self.ChatReusltText = result_json['content']
