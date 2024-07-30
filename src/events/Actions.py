import os
import json
from typing import Any
from PySide6.QtCore import Signal, QThread
from loguru import logger


class ActionPic:
    def __init__(self) -> None:
        self.filePath = os.path.join(
            os.getcwd(), "data", "config", "action_pictures.json"
        )
        if os.path.isfile(self.filePath) is False:
            with open(self.filePath, "w+", encoding="utf-8") as wfp:
                wfp.write(json.dumps({}))
        self.actions = []
    
    def read(self, key: str) -> list:
        with open(self.filePath, "r", encoding="utf-8") as rfp:
            __read = json.loads(rfp.read())
            # 尝试查找Key
            result = __read.get(key, None)
            if result is None:
                logger.error(f"未找到key: {key}")
                return None

            # 将数据填入action
            path = result.get("path")
            if not path:
                logger.error(f"读取key: {key}， 时出现数据残缺。")
            
            self.actions = []
            for paths, _, files in os.walk(path):
                for file in files:
                    self.actions.append(
                        os.path.join(paths, file)
                    )
        return self.actions


actionPic = ActionPic()
actionAllPicData = {
    # 持续动作
    "Standby": actionPic.read("Standby"),
    "mention": actionPic.read("mention"),
    "sleep": actionPic.read("sleep"),
    "discomfort": actionPic.read("discomfort"),
    # 非持续动作
    "left": actionPic.read("left"),
    "right": actionPic.read("right"),
    "eat": actionPic.read("eat"),
    "love": actionPic.read("love")
}


class ActionEvent(QThread):
    """动作事件"""
    result = Signal(str)
    startActionEventTimerSignal = Signal()
    stopActionEventTimerSignal = Signal()

    def __init__(self, switchBackgroundFunc: Any) -> None:
        """
        对当前已有动作进行加载/播放
        :param switchBackgroundFunc: Any 更改主界面gui背景方法
        :return None
        """
        super().__init__()
        self.switchBackground = switchBackgroundFunc
        self.requestInterruption = False
        self.sign = "Standby"
        self.actionEventPicList = actionAllPicData[self.sign]

    def run(self) -> None:
        """运行"""
        self.startActionEventTimerSignal.emit()

    def playNextImage(self) -> None:
        """播放"""
        if self.requestInterruption:
            return None
        
        actionAllPicDataKeys = list(actionAllPicData.keys())
        # 查看当前列表中内容是否已删除完毕，代表着当前动作已结束。
        if not self.actionEventPicList:
            actionAllPicData[self.sign] = actionPic.read(self.sign) # 重新读取数据
            self.result.emit(self.sign)
            return None
        
        # 删除第一个元素，并记录下来
        next_image = self.actionEventPicList.pop(0)
        self.switchBackground(next_image)
        if self.sign not in actionAllPicDataKeys[-2:]:
            # 将删除的元素再次添加到列表末尾，到达循环目的。
            self.actionEventPicList.append(next_image)
        if self.sign in ['left', 'right']:
            self.result.emit(self.sign)

    def load(self, key: str) -> None:
        """
        通过key加载指定动作的图片列表
        :param key: str
        :return None
        """
        self.sign = key
        self.actionEventPicList = actionAllPicData[self.sign]

    def mentionEvent(self) -> None:
        """提起"""
        self.load("mention")

    def standbyEvent(self) -> None:
        """待机"""
        self.load("Standby")

    def eatEvent(self) -> None:
        """吃"""
        self.load("eat")

    def sleepEvent(self) -> None:
        """睡觉"""
        self.load("sleep")

    def loveEvent(self) -> None:
        """ღ( ´･ᴗ･` )比心"""
        self.load("love")

    def discomfortEvent(self) -> None:
        """不适"""
        self.load("discomfort")

    def left(self) -> None:
        """向左"""
        self.load("left")
    
    def right(self) -> None:
        """向右"""
        self.load("right")
