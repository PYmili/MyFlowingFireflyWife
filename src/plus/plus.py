import os
import sys
import json
import importlib
from io import open
from abc import ABC
from typing import Union, Dict
from dataclasses import dataclass
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QWidget
from loguru import logger


PLUS_DIR = os.path.join(os.getcwd(), "data", "config", "plus")
PLUS_CONFIG_DIR = os.path.join(PLUS_DIR, "plus.json")
if os.path.isdir(PLUS_DIR) is False:
    try:
        os.makedirs(PLUS_DIR)
    except Exception as e:
        logger.error("Plus init error result: " + e)


@dataclass
class addressType:
    github: str
    gitee: str
    other: str


@dataclass
class plusDataType:
    author: str
    version: str
    description: str
    address: addressType
    static: str


class PlusCallableType(ABC):
    @staticmethod
    def run() -> QThread:
        pass
    
    @staticmethod
    def settingWindow() -> QWidget:
        pass


class plusConfigManager:
    def __init__(self) -> None:
        """plus的config文件管理器"""
        pass
    
    def readDataByPlusName(self, plusName: Union[str, None] = None) -> Union[plusDataType, list[plusDataType], None]:
        """
        通过plusName值读取数据
        Params:
            plusName: Union[str, None] = None 需要的plusName值，默认None时，返回全部plus。
        Return: Union[plusDataType, list[plusDataType], None]
        """
        if plusName:
            plusName = plusName.split(".")[-1]
        if os.path.isfile(PLUS_CONFIG_DIR) is False:
            self.__createConfigFile__()
        with open(PLUS_CONFIG_DIR, "r+", encoding="utf-8") as rfp:
            __read: dict = json.loads(rfp.read())
            if plusName is None:
                return [{key: plusDataType(**value)} for key, value in __read.items()]
            __read = __read.get(plusName, None)
            if __read:
                # 返回一个包含单个plus数据的字典
                return plusDataType(**__read)
            
    def writeDataByPlusName(self, plusName: str, data: plusDataType) -> None:
        """
        通过plusName写入数据到配置文件
        Params:
            plusName: str 需要写入的plus的名称
            data: plusDataType 要写入的数据
        """
        with open(PLUS_CONFIG_DIR, "r", encoding="utf-8") as rfp:
            existing_data = json.load(rfp)
        
        if plusName in existing_data:
            # 更新现有的数据
            existing_data[plusName] = data.__dict__  # 使用__dict__来确保传递正确的属性

        with open(PLUS_CONFIG_DIR, "w", encoding="utf-8") as wfp:
            json.dump(existing_data, wfp, indent=4, ensure_ascii=False)
        
    def __createConfigFile__(self) -> None:
        """创建plus的Config文件"""
        with open(PLUS_CONFIG_DIR, "w+", encoding="utf-8") as wfp:
            wfp.write("{\n}")


class plusLoader:
    def __init__(self, _plusName: Union[str, None] = None) -> None:
        """
        plus加载器
        Params:
            _plusName: str 需要加载的plus的名称
        Retrun: None
        """
        self.manager = plusConfigManager()
        if _plusName:
            self.plusName = _plusName
            self.allDataList: list = []
            self.data: plusDataType = self.__readData__()
        else:
            logger.info("启动上一次已启动的plus。")
            self.allDataList: list = self.manager.readDataByPlusName()
            for allData in self.allDataList:
                for key, value in allData.items():
                    if value.static != "on":
                        continue
                    self.data = value
                    self.plusName = key
                    self.on()

    def on(self) -> Union[PlusCallableType, None]:
        """
        打开这个plus， 并返回object
        :return Union[object, None]
        """
        logger.info(f"启动 plusName: {self.plusName}")
        # 判断是否已启动
        if self.getStaitc() is True:
            logger.warning(f"已启动 plusName: {self.plusName}")
            return None
        
        # 对plus进行import
        self.plus = importlib.import_module(self.plusName, "main")
        result = lambda: getattr(self.plus.main, "main", lambda: None)()
        if not self.getStaitc():
            logger.error(f"{self.plusName}启动失败！")
            self.setStatic(False)
            return result
        self.setStatic(True)
        return result
            

    def off(self) -> bool:
        """禁用这个plus"""
        logger.info(f"禁用 plusName: {self.plusName}")
        if self.getStaitc() is True:
            del sys.modules[self.plusName]
            if not self.getStaitc():
                self.setStatic(False)
                return True
            self.setStatic(True)
            return False
        else:
            logger.warning(f"未启动 plusName: {self.plusName}")
            return False
        
    def offAll(self) -> None:
        """关闭所有plus。"""
        if not self.allDataList:
            return False
        plusNames = [list(i.keys())[0] for i in self.allDataList]
        for plusName in plusNames:
            self.plusName = plusName
            self.off()

    def getStaitc(self) -> bool:
        """当前这个plus的状态"""
        __static = sys.modules.get(self.plusName)
        if __static:
            return True
        else:
            return False
        
    def setStatic(self, __static: bool) -> bool:
        """更改当前plus的状态"""
        if __static is False:
            self.data.static = "off"
        else:
            self.data.static = "on"
    
    def __readData__(self) -> Union[dict, None]:
        """
        读取plus数据
        Return: Union[List[dict], None]
        """
        readResult = self.manager.readDataByPlusName(self.plusName)
        if not readResult:
            # 读取错误，没有这个plus
            logger.error(f"Error Reading: There is no such {self.plusName} plus.")
        return readResult

    def save(self) -> None:
        """显式写入当前plus的数据到配置文件"""
        if self.data is not None and self.manager is not None:  # 添加对 self.manager 的检查
            self.manager.writeDataByPlusName(self.plusName, self.data)
            logger.info(f"{self.plusName}的数据已保存。")
        elif self.manager is None:
            logger.error(f"Manager instance is None for {self.plusName}, unable to save.")
        else:
            logger.warning(f"No data to save for {self.plusName}.")
