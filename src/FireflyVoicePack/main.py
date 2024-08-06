import os
import json
import random
from datetime import datetime
from typing import Union
from loguru import logger
from PySide6.QtCore import QThread, Signal, QMutex, QWaitCondition

from src.MediaPlayer import *

DATA_DIR = os.path.join(os.getcwd(), "data")


class VoicePack:
    @staticmethod
    def getAllVoicePack() -> dict:
        """获取所有音频包"""
        configFileDir = os.path.join(DATA_DIR, "config", "voicepack.json")
        with open(configFileDir, "r+", encoding="utf-8") as rfp:
            allPack = json.loads(rfp.read())
        return allPack
    
    @staticmethod
    def getVoicePackByKey(key: str) -> Union[dict, None]:
        """
        通过Key获取指定的音频包
        Params:
            key: str 需要查找的Key值
        :reutrn Union[dict, None]
        """
        allVoicePack = VoicePack.getAllVoicePack()
        return allVoicePack.get(key, None)


class FireflyVoicePackQThread(QThread):
    started = Signal(dict)
    played = Signal()
    def __init__(self, key: str = None) -> None:
        super().__init__(parent=None)
        self.key = key
    
    def run(self) -> None:        
        voicePackData: dict = VoicePack.getVoicePackByKey(self.key)
        timeOfDay = self.getTimeOfDay()
        if timeOfDay != "other":
            voicePackData = voicePackData[timeOfDay]
        else:
            voicePackData = voicePackData['other']
        voicePackData = random.choice(voicePackData)

        wav = voicePackData.get('wav')
        if not wav:
            self.result.emit({})
            return None

        self.started.emit(voicePackData)
        self.player = AudioPlayer(wav)
        self.player.play()
        self.sleep(5)   # 为了播放完整
        self.played.emit()

    def getTimeOfDay(self) -> str:
        """获取当前时间点对应的时间段"""
        # 获取当前时间
        now = datetime.now()
        hour = now.hour

        # 定义时间段的开始和结束时间
        if 6 <= hour < 8:
            return "morn"  # 早晨
        elif 10 <= hour < 12:
            return "noon"  # 中午
        elif 18 <= hour < 21:
            return "other"  # 傍晚
        elif 21 <= hour < 24 or 0 <= hour < 6:
            return "night"  # 夜晚
        else:
            return "other"  # 其他时间段
