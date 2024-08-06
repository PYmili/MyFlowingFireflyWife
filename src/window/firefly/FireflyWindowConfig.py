import os
import json
from typing import Union
from loguru import logger

CONDIF_FILE = os.path.join(os.getcwd(), "data", "config", "main.json")
if os.path.isfile(CONDIF_FILE) is False:
    try:
        os.makedirs(CONDIF_FILE)
    except Exception as e:
        logger.info(e)


class ConfigFile:
    def __init__(self) -> None:
        self.scaledToWidthSize: int = 0     # 文件缩放倍数
        self.currentBgImage: str = None     # 当前背景图片
        self.readJsonFile()

    def readJsonFile(self) -> None:
        """读取 CONDFIG_FILE 中的json文件"""
        with open(CONDIF_FILE, "r", encoding="utf-8") as rfp:
            data = json.loads(rfp.read())
            self.scaledToWidthSize = data.get("scaledToWidthSize")
            self.currentBgImage = data.get("currentBgImage")
