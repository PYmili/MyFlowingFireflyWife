import os
import json
import random
from datetime import datetime
from typing import Union, Optional
from loguru import logger
from PySide6.QtCore import QThread, Signal

from src.MediaPlayer import AudioPlayer

DATA_DIR = os.path.join(os.getcwd(), "data")

class VoicePack:
    @staticmethod
    def getAllVoicePack() -> dict:
        configFileDir = os.path.join(DATA_DIR, "config", "voicepack.json")
        try:
            with open(configFileDir, "r+", encoding="utf-8") as rfp:
                allPack = json.load(rfp)
            return allPack
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"无法读取或分析voicepack.json: {e}")
            return {}

    @staticmethod
    def getVoicePackByKey(key: str) -> Union[dict, None]:
        allVoicePack = VoicePack.getAllVoicePack()
        return allVoicePack.get(key)

    @staticmethod
    def getTimeOfDay() -> str:
        now = datetime.now()
        hour = now.hour
        if 6 <= hour < 8:
            return "morn"
        elif 10 <= hour < 12:
            return "noon"
        elif 18 <= hour < 21:
            return "evening"
        elif 21 <= hour < 24 or 0 <= hour < 6:
            return "night"
        else:
            return "other"

class FireflyVoicePackQThread(QThread):
    started = Signal(dict)
    played = Signal()

    def __init__(self, key: Optional[str] = None):
        super().__init__()
        self.key = key
        self.voicePackData: Optional[dict] = None

    def run(self) -> None:
        try:
            self.voicePackData = VoicePack.getVoicePackByKey(self.key)
            timeOfDay = VoicePack.getTimeOfDay()
            self.voicePackData = self.voicePackData.get(timeOfDay, self.voicePackData.get('other'))
            self.voicePackData = random.choice(self.voicePackData)
        except IndexError:
            logger.error("没有可用的语音包数据。")
            self.result.emit({})
            return

        self.started.emit(self.voicePackData)
        self.player = AudioPlayer(self.voicePackData.get('wav'))
        if self.player:
            self.player.play()
            self.played.emit()
        else:
            logger.error("无法初始化音频播放器。")

