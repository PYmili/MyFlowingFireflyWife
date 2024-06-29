import os
import sys
import json
import importlib
from io import open
from abc import ABC, abstractmethod
from typing import Union, Dict
from dataclasses import dataclass
from PySide6.QtCore import QThread
from PySide6.QtWidgets import QWidget
from loguru import logger

sys.path.insert(0, os.path.join(
        os.path.abspath(os.path.dirname(os.getcwd()))
    )
)
from src import FireflyVoicePack


PLUGIN_DIR = os.path.join(os.getcwd(), "data", "config", "plugin")
PLUGIN_CONFIG_DIR = os.path.join(PLUGIN_DIR, "plugin.json")
if os.path.isdir(PLUGIN_DIR) is False:
    try:
        os.makedirs(PLUGIN_DIR)
    except Exception as e:
        logger.error("plugin init error result: " + e)


@dataclass
class addressType:
    github: str
    gitee: str
    other: str


@dataclass
class pluginDataType:
    author: str
    version: str
    description: str
    address: addressType
    static: str


class pluginClassType(ABC):
    @abstractmethod
    def run() -> QThread:
        pass

    @abstractmethod
    def stop() -> bool:
        pass
    
    @abstractmethod
    def settingWindow() -> QWidget:
        pass


class pluginConfigManager:
    def __init__(self) -> None:
        """plugin的config文件管理器"""
        pass
    
    def readDataBypluginName(self, pluginName: Union[str, None] = None) -> Union[pluginDataType, list[pluginDataType], None]:
        """
        通过pluginName值读取数据
        Params:
            pluginName: Union[str, None] = None 需要的pluginName值，默认None时，返回全部plugin。
        Return: Union[pluginDataType, list[pluginDataType], None]
        """
        if pluginName:
            pluginName = pluginName.split(".")[-1]
        if os.path.isfile(PLUGIN_CONFIG_DIR) is False:
            self.__createConfigFile__()
        with open(PLUGIN_CONFIG_DIR, "r+", encoding="utf-8") as rfp:
            __read: dict = json.loads(rfp.read())
            if pluginName is None:
                return [{key: pluginDataType(**value)} for key, value in __read.items()]
            __read = __read.get(pluginName, None)
            if __read:
                # 返回一个包含单个plugin数据的字典
                return pluginDataType(**__read)
            
    def writeDataBypluginName(self, pluginName: str, data: pluginDataType) -> None:
        """
        通过pluginName写入数据到配置文件
        Params:
            pluginName: str 需要写入的plugin的名称
            data: pluginDataType 要写入的数据
        """
        with open(PLUGIN_CONFIG_DIR, "r", encoding="utf-8") as rfp:
            existing_data = json.load(rfp)
        
        if pluginName in existing_data:
            # 更新现有的数据
            existing_data[pluginName] = data.__dict__  # 使用__dict__来确保传递正确的属性

        with open(PLUGIN_CONFIG_DIR, "w", encoding="utf-8") as wfp:
            json.dump(existing_data, wfp, indent=4, ensure_ascii=False)
        
    def __createConfigFile__(self) -> None:
        """创建plugin的Config文件"""
        with open(PLUGIN_CONFIG_DIR, "w+", encoding="utf-8") as wfp:
            wfp.write("{\n}")


class pluginLoader:
    def __init__(self, _pluginName: Union[str, None] = None) -> None:
        """
        plugin加载器
        Params:
            _pluginName: str 需要加载的plugin的名称
        Retrun: None
        """
        sys.path.insert(0, os.path.join(
                os.path.abspath(os.path.dirname(__file__))
            )
        )
        self.manager = pluginConfigManager()
        self.plugin = None
        self.pluginName = _pluginName
        self.data: pluginDataType = self.__readData__()

    def on(self) -> Union[pluginClassType, None]:
        """
        打开这个plugin，并返回object。
        :return Union[pluginClassType, None]
        """
        logger.info(f"启动 pluginName: {self.pluginName}")
        # 判断是否已启动
        if self.getStaitc() is True:
            logger.warning(f"已启动 pluginName: {self.pluginName}")
            return None

        # 读取插件数据
        self.data = self.__readData__()
        if not self.data:
            logger.error(f"{self.pluginName}插件数据读取失败，启动终止。")
            return None

        try:
            # 动态导入主模块
            self.plugin = importlib.import_module(self.pluginName, "main")
            # 获取Main类
            MainClass = self.plugin.Main
            if MainClass is None:
                logger.error(f"{self.pluginName}模块中没有找到Main类。")
                return None

            # 设置静态状态为启动
            self.setStatic(True)
            return MainClass
        except ImportError as e:
            logger.error(f"导入{self.pluginName}模块失败：{e}, plugin: {self.plugin}")
        except Exception as e:
            logger.error(f"{self.pluginName}模块中发生错误：{e}")

        self.setStatic(False)
        return None

    def off(self) -> bool:
        """禁用这个plugin"""
        logger.info(f"禁用 pluginName: {self.pluginName}")
        if self.getStaitc() is True:
            del sys.modules[self.pluginName]
            if not self.getStaitc():
                self.setStatic(False)
                return True
            self.setStatic(True)
            return False
        else:
            logger.warning(f"未启动 pluginName: {self.pluginName}")
            return False

    def getStaitc(self) -> bool:
        """当前这个plugin的状态"""
        __static = sys.modules.get(self.pluginName)
        if __static:
            return True
        else:
            return False
        
    def setStatic(self, __static: bool) -> bool:
        """更改当前plugin的状态"""
        if __static is False:
            self.data.static = "off"
        else:
            self.data.static = "on"
    
    def __readData__(self) -> Union[dict, None]:
        """
        读取plugin数据
        Return: Union[List[dict], None]
        """
        readResult = self.manager.readDataBypluginName(self.pluginName)
        if not readResult:
            # 读取错误，没有这个plugin
            logger.error(f"Error Reading: There is no such {self.pluginName} plugin.")
        return readResult

    def save(self) -> None:
        """显式写入当前plugin的数据到配置文件"""
        if self.data is not None and self.manager is not None:  # 添加对 self.manager 的检查
            self.manager.writeDataBypluginName(self.pluginName, self.data)
            logger.info(f"{self.pluginName}的数据已保存。")
        elif self.manager is None:
            logger.error(f"Manager instance is None for {self.pluginName}, unable to save.")
        else:
            logger.warning(f"No data to save for {self.pluginName}.")
