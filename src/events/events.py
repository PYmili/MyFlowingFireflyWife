import os
import json
import time
from typing import Any
from PyQt5.QtCore import pyqtSignal, QThread, QTimer
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
            _type = result.get("type")
            number = result.get("number")
            if not all([path, _type, number]):
                logger.error(f"读取key: {key}， 时出现数据残缺。")
            
            self.actions = []
            for paths, dirs, files in os.walk(path):
                for file in files:
                    self.actions.append(
                        os.path.join(paths, file)
                    )
        return self.actions


actionPic = ActionPic()
actionAllPicList = {
    "Standby": actionPic.read("Standby"),
    "mention": actionPic.read("mention"),
    "eat": actionPic.read("eat")
}


class ActionEvent(QThread):
    result = pyqtSignal(bool)
    start_timer_signal = pyqtSignal()
    stop_timer_signal = pyqtSignal()

    def __init__(self, switchBackgroundFunc: Any) -> None:
        super().__init__()
        self.switchBackground = switchBackgroundFunc
        self.requestInterruption = False
        self.sign = "Standby"
        self.actionEventPicList = actionAllPicList[self.sign]

    def run(self) -> None:
        self.start_timer_signal.emit()

    def playNextImage(self) -> None:
        if self.requestInterruption:
            return None
        
        if self.actionEventPicList:
            # 删除第一个元素，并记录下来
            next_image = self.actionEventPicList.pop(0)
            self.switchBackground(next_image)
            if self.sign != "eat":
                # 将删除的元素再次添加到列表末尾，到达循环目的。
                self.actionEventPicList.append(next_image)

        # 对eat的特殊处理
        if self.sign == "eat" and not self.actionEventPicList:
            # 重新读取eat
            actionAllPicList["eat"] = actionPic.read("eat")
            self.result.emit(True)
            
        if self.sign != "mention" and self.sign != "eat":
            self.result.emit(True)

    def load(self, key: str) -> None:
        self.sign = key
        self.actionEventPicList = actionAllPicList[self.sign]
        logger.info(f"Action: {key}")

    def mentionEvent(self) -> None:
        self.load("mention")

    def standbyEvent(self) -> None:
        self.load("Standby")

    def eatEvent(self) -> None:
        self.load("eat")