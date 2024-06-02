import json
import asyncio
from typing import Dict, Union

import websockets
from loguru import logger

ADDRESS = "wss://www.modelscope.cn/api/v1/studio/yunshansongbai/Liuying-GPT-Sovits/gradio/queue/join" \
          "?backend_url=/api/v1/studio/yunshansongbai/Liuying-GPT-Sovits/gradio/" \
          "&sdk_version=3.47.1"
ADDRESS_FILE = "https://www.modelscope.cn/api/v1/studio/yunshansongbai/Liuying-GPT-Sovits/gradio/file="


class LiuYingGPTSovitesModelScope:
    def __init__(
            self,
            content: str,
            sessionHash: str,
            studioToken: str,
            referenceAudioText: str = "我叫流萤，是鸢尾花家系的译者。"
        ) -> None:
        """
        通过魔撘的Liuying-GPT-Sovits接口进行推理
        :param content: str 需要生成的文本
        :param sessionHash: str 需抓包获取
        :param studioTkoen: str 需抓包获取
        :param referenceAudioText: str 参照音频
        :return None
        """
        logger.info("流萤 GPT-Sovites 魔撘接口")
        self.address = ADDRESS + "&studio_token=" + studioToken
        self.sessionHash = sessionHash
        # 生成请求数据
        self.data = {
            "data":[
                referenceAudioText,
                referenceAudioText,
                "中文", content,
                "中文", "按中文句号。切"
            ],
            "event_data": None,
            "fn_index": 1,
            "dataType": [
                "dropdown", "textbox", "dropdown",
                "textbox", "dropdown", "radio"
            ],
            "session_hash": sessionHash
        }
        
    async def clientSend(
            self,
            websocket: websockets.WebSocketClientProtocol,
            message: Dict[str, Union[int, str]]
        ) -> None:
        """
        发送信息
        :param websocket: websockets.WebSocketClientProtocol
        :param message: Dict[str, Union[int, str]] 需要发送的信息
        :return None
        """
        message = json.dumps(message)
        # logger.info("client send message: " + str(message))
        await websocket.send(message)

    async def clientHands(
            self,
            websocket: websockets.WebSocketClientProtocol
        ) -> Union[None, Dict]:
        """
        处理服务器返回及发送
        :param websocket: websockets.WebSocketClientProtocol
        :return Union[None, Dict]
        """
        while True:
            response = await websocket.recv()
            # logger.info("websocket response text: " + response)
            response = json.loads(response)
            msg = response.get('msg')

            if msg == "send_hash":
                await self.clientSend(
                    websocket, {"fn_index": 1,"session_hash": self.sessionHash}
                )
            elif msg == "send_data":
                await self.clientSend(
                    websocket,
                    self.data
                )
            if msg == "process_completed":
                return response

    async def Main(self) -> Union[str, None]:
        """
        主函数
        :return Union[str, None]
        """
        async with websockets.connect(self.address) as websocket:
            result = await self.clientHands(websocket)
            if not result:
                return None

        return ADDRESS_FILE + result["output"]["data"][0]["name"]


def StartLiuYingGPTSovites(
        content: str,
        sessionHash: str,
        studioToken: str,
        referenceAudioText: Union[str, None] = None
    ) -> None:
    """启动事例"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(
            LiuYingGPTSovitesModelScope(
                content=content,
                sessionHash=sessionHash,
                studioToken=studioToken
            ).Main()
        )
    loop.close()
    return result