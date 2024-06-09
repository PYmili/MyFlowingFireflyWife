import asyncio
from typing import Union

from gradio_client import Client
from loguru import logger

DEFAULT = "嗯，所以每天只能吃一个。"
API_URL = "https://s5k.cn/api/v1/studio/LHXCxyw/Liuying-GPT-Sovits/gradio/"


class LiuYingGPTSovitsGradio:
    def __init__(self, content: str) -> None:
        self.content = content
        self.client = Client(API_URL)
    
    async def run(self) -> Union[str, None]:
        try:
            result = self.client.predict(
                    DEFAULT,
                    DEFAULT,
                    "中文",
                    self.content,
                    "中文",
                    "按中文句号。切",
                    fn_index=1
            )
            return result
        except Exception as e:
            logger.error(e)
            return None


def StartLiuYingGPTSovites(content: str) -> None:
    """启动事例"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(
            LiuYingGPTSovitsGradio(
                content=content
            ).run()
        )
    loop.close()
    return result
