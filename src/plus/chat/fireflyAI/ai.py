import json
import os
import random
from datetime import datetime
from typing import Callable, Union
from http import HTTPStatus

import dashscope
from dashscope import Generation
from dashscope.api_entities.dashscope_response import Role
from loguru import logger

from .configuration import Configuration

PLUS_CONFIG_DIR = os.path.join(os.getcwd(), "data", "config", "plus", "chat")


class Chat:
    def __init__(
            self,
            callback: Callable,
            messagesJsonFile: str = os.path.join(
                PLUS_CONFIG_DIR,
                "cache.json"
            )
    ) -> None:
        """
        与QWen-72b模型交互
        :param messagesJsonFile:
        """
        self.ChatCallback = callback
        self.send = random.randint(1, 10000)

        # 读取配置文件
        self.configuration = Configuration()
        self.configuration.read()
        dashscope.api_key = self.configuration.QWen_API_KEY

        self.messageJsonFile = messagesJsonFile
        # 读取messages缓存
        logger.info(f"读取缓存文件：{messagesJsonFile}")
        self.messages = self.readMessages()
        if self.messages:
            logger.info(f"读取成功！共{len(self.messages)}条信息")
        else:
            logger.error("读取失败！")

    def addMessage(self, msg: str) -> bool:
        """
        添加用户发送的信息
        :param msg:
        :return: bool
        """
        logger.info(f"添加信息：{msg}")
        if not msg:
            return False
        self.messages.append({"role": Role.USER, "content": msg})
        return True
    
    def __get_full_content(self, responses: Generation.call) -> Union[str, None]:
        """
        获取返回内容。
        :return Union[str, None]
        """
        full_content = ""  # 用于存放回复内容
        for response in responses:
            if response.status_code == HTTPStatus.OK:
                # 提取内容
                full_content = response.output.choices[0]['message']['content']
            else:
                return None
            
            self.ChatCallback(
                {
                    "content": full_content,
                    "status_code": response.status_code
                }
            )
        return full_content

    def run(self, is_stream: bool = True) -> None:
        """
        启动程序
        :return: dict
        """
        if not self.messages:
            return None

        # 调用官方sdk
        responses = Generation.call(
            model="qwen2-72b-instruct",
            messages=self.messages,
            send=self.send,
            result_format="message",
            stream=is_stream,
            output_in_full=True
        )
        
        full_content = ""
        if is_stream is True:
            full_content = self.__get_full_content(responses)
        else:
            full_content = self.__get_full_content([responses])

        # 写入对话缓存文件
        self.messages.append(
            {
                'role': Role.ASSISTANT,
                'content': full_content
            }
        )
        if self.writeMessages() is False:
            logger.error("写入缓存失败！")
        else:
            logger.info("写入缓存成功！")

    def readMessages(self) -> list:
        """
        读取对话的缓存
        :return: list
        """
        logger.info("读取对话缓存")
        result = []
        with open(self.messageJsonFile, "r", encoding="utf-8") as rfp:
            data = json.loads(rfp.read())
            for __value in data.values():
                for msg in __value:
                    result.append(msg)

        return result

    def writeMessages(self) -> bool:
        """
        向对话缓存文件写入
        :return: bool
        """
        logger.info("写入对话缓存")
        result = True
        nowDateTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(self.messageJsonFile, "w+", encoding="utf-8") as wfp:
                # 以当前时间为key存储messages
                WriteData = json.dumps(
                    {nowDateTime: self.messages},
                    indent=4,
                    ensure_ascii=False
                )
                wfp.write(WriteData)
        except OSError:
            result = False

        return result


def callbackDemo(data: dict) -> None:
    """
    回调函数实例
    :param data: dict
    :return:
    """
    if data['status_code'] == 200:
        logger.info(data['content'])
    else:
        logger.error(data['content'])
