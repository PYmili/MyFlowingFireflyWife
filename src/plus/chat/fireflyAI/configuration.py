import os
import json
from loguru import logger

PLUS_CONFIG_DIR = os.path.join(os.getcwd(), "data", "config", "plus", "chat")
CONFIG_FILE_DIR = os.path.join(PLUS_CONFIG_DIR, "configuration.json")


class Configuration:
    def __init__(self) -> None:
        """用于处理configuration.json文件的数据"""
        self.QWen_API_KEY = None
        self.writeDict = {
            "QWen_API_KEY": ""
        }
        if os.path.isfile(CONFIG_FILE_DIR) is False:
            self.createFile()
    
    def read(self) -> None:
        """读取所有数据"""
        with open(CONFIG_FILE_DIR, "r+") as rfp:
            loads = json.loads(rfp.read())
            self.QWen_API_KEY = loads.get("QWen_API_KEY")
    
    def createFile(self) -> None:
        """创建文件"""
        with open(CONFIG_FILE_DIR, "w+", encoding="utf-8") as wfp:
            wfp.write(json.dumps(self.writeDict), indent=4)
