import os
import json
import random
from typing import Union

import psutil
from loguru import logger
from PySide6.QtCore import Signal, QThread

from src.player import AudioPlayer
from src.extends.extend import ExtendType, ExtendInfoType

CONFIG_FILE_DIR = os.path.join(os.getcwd(), "data", "config", "battery_voice.json")
DATA_AUDIO_DIR = os.path.join(os.getcwd(), "data", "config", "audio")


class BattryVoiceQThread(QThread):
    result = Signal(bool)
    def __init__(self) -> None:
        """
        Params:
            player: callable | 播放器
        """
        super().__init__(parent=None)
        self.requestInterruption: bool = False     # 用于请求停止服务
        self.isCurrentPowerPlugged: bool = False    # 当前是否插入电源
        self.isLowBattery: bool = False            # 是否为低电量
        self.isHealthyPower: bool = False          # 是否为健康电量
        self.isFullPower: bool = False             # 是否充满电池

    def run(self) -> None:
        if self.getBatteryInfo() is None:
            logger.warning("未获取到当前电脑的电池信息。")
            self.result.emit(False)
            return None
        while not self.requestInterruption:
            __batteryInfo = self.getBatteryInfo()
            if __batteryInfo is None:
                break
            percent: int = __batteryInfo.get("percent")                 # 电源百分比
            powerPlugged: bool = __batteryInfo.get("power_plugged")     # 是否插入电源适配器
            # secsleft: int = __batteryInfo.get("secsleft")               # 当前电量剩余时间
            
            # 插入电源适配器时触发
            if powerPlugged and self.isCurrentPowerPlugged is False:
                self.isCurrentPowerPlugged = True
                self.playAudio("power_plugged")        # 播放插入电源适配器音频
            # 拔掉电源适配器时触发
            elif not powerPlugged and self.isCurrentPowerPlugged is True:
                self.isCurrentPowerPlugged = False
                self.isLowBattery = False
                self.isHealthyPower = False
                self.isFullPower = False
                self.playAudio("power_not_plugged")    # 播放未插入电源适配器音频

            if self.isCurrentPowerPlugged is False:
                continue
 
            # 电量各阶段
            if 1 <= percent < 50 and self.isLowBattery is False:
                self.playAudio("LOW_BATTERY")       # 播放低电量音频
                self.isLowBattery = True
            elif 50 <= percent <= 90 and self.isHealthyPower is False:
                self.playAudio("HEALTHY_POWER")     # 播放健康电量音频
                self.isHealthyPower = True
            elif percent == 100 and self.isFullPower is False:
                self.playAudio("FULL_POWER")        # 播放充满音频
                self.isFullPower = True

    def playAudio(self, key: str) -> bool:
        """
        通过key值对配置文件的音频数据进行读取并播放。
        :param key: str 需要播放的音频关键字
        :return bool
        """
        with open(CONFIG_FILE_DIR, "r+", encoding="utf-8") as rfp:
            data = json.loads(rfp.read())
            if not data:
                logger.warning(f"读取配置文件：{CONFIG_FILE_DIR}时，出现错误。")
                return False
        # 进行播放
        playFile = data.get(key)
        if not playFile:
            logger.warning(f"未找到音频文件: {key}。")
            return False
        playFile = random.choice(playFile)  # 从列表中随机提取一个音频
        playFile = os.path.join(os.getcwd(), playFile['wav'])
        logger.info(f"电量音频播放: {playFile}")
        audioPlayer = AudioPlayer(playFile)
        audioPlayer.play()
        return True
        
    @staticmethod
    def getBatteryInfo() -> Union[dict, None]:
        """
        获取电池信息。
        :return Union[dict, None]
        """
        battery = psutil.sensors_battery()
        if battery is None:
            return None

        return {
            'percent': battery.percent,
            'power_plugged': battery.power_plugged,
            'secsleft': battery.secsleft
        }


class batteryVoice:
    def __init__(self) -> None:
        self.battryVoiceThread: QThread = None
        self.InfoJson: ExtendInfoType = ExtendType.readInfoJson("BatteryVoice")

    def start(self) -> bool:
        self.battryVoiceThread = BattryVoiceQThread()
        self.battryVoiceThread.start()
        self.InfoJson.isStatic = True
        ExtendType.writeInfoJson(self.InfoJson.name, self.InfoJson)
        return True

    def stop(self) -> bool:
        self.InfoJson.isStatic = False
        ExtendType.writeInfoJson(self.InfoJson.name, self.InfoJson)
        if not self.battryVoiceThread:
            logger.error(f"未启动: BattryVoiceQThread")
            return False
        self.battryVoiceThread.requestInterruption = True
        self.battryVoiceThread.exit(0)
        self.battryVoiceThread.wait()
        return True
    