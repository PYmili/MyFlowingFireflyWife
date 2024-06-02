import os
import json
from typing import Union

import requests
from loguru import logger
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QLabel

from firefly import (
    gpt,
    tts
)
from VoiceToText import (
    BaiduYun_STT,
    Funasr_STT,
    SoundRecording
)


def readConfig() -> dict:
    """
    读取config.json文件的数据
    :return dict
    """
    configJsonDir = os.path.join(os.getcwd(), "config.json")
    if os.path.isfile(configJsonDir) is False:
        with open(configJsonDir, "w+",encoding="utf-8") as fp:
            fp.write(json.dumps({
                "tts": "funasr"
            }))
        return {}
    with open(configJsonDir, "r", encoding="utf-8") as fp:
        __data = fp.read()
        if not __data:
            return {}

    return json.loads(__data)


def loadingSTT() -> Union[BaiduYun_STT, Funasr_STT]:
    """
    对STT配置进行加载。
    :return TTS_OBJECT
    """
    configData = readConfig()
    logger.info(f"read Config File: {configData}")
    stt = BaiduYun_STT()
    if configData.get('stt') == 'funasr':
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
        self.saveWavFile()
        # 对message_label进行更新文本
        self.message_label.setWordWrap(True)
        self.message_label.setText(self.text)
        self.message_label.adjustSize()
        self.message_label.show()
        # 播放音频
        while not tts.WavPlayer(self.tts_wav).play(): pass
        return True
    
    def saveWavFile(self) -> None:
        """
        保存.wav文件
        :return None
        """
        logger.info("Download Wav File: " + self.tts_wav)
        with requests.get(self.tts_wav) as response:
            if response.status_code == 200:
                with open("result_audio.wav", "wb+") as wfp:
                    wfp.write(response.content)
                self.tts_wav = os.path.join(os.getcwd(), "result_audio.wav")
                logger.info("Download Success.")
            else:
                logger.error(f"下载TTS: 生成音频错误。URL: {self.tts_wav}")
                return None


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