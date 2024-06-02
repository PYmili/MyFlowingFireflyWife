import os
import json

configFilePath = os.path.join(
    os.path.split(__file__)[0],
    "configuration.json"
)


class Configuration:
    def __init__(self) -> None:
        """用于处理configuration.json文件的数据"""
        self.QWen_API_KEY = None
        self.sessionHash = None
        self.studioToken = None
        self.writeDict = {
            "QWen_API_KEY": "",
            "sessionHash": "",
            "studioToken": ""
        }
        if os.path.isfile(configFilePath) is False:
            self.createFile()
    
    def read(self) -> None:
        """读取所有数据"""
        with open(configFilePath, "r+") as rfp:
            loads = json.loads(rfp.read())
            self.QWen_API_KEY = loads.get("QWen_API_KEY")
            self.sessionHash = loads.get("sessionHash")
            self.studioToken = loads.get("studioToken")
    
    def createFile(self) -> None:
        """创建文件"""
        with open(configFilePath, "w+", encoding="utf-8") as wfp:
            wfp.write(json.dumps(self.writeDict), indent=4)
