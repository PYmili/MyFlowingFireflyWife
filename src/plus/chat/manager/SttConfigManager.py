import os
import json
from typing import Union, Dict, List

DEFAULT: Dict[str, Union[str, None]] = {
    "stt": "BaiduYun",
    "APIKey": None,
    "SecretKey": None
}
PLUS_CONFIG_DIR = os.path.join(os.getcwd(), "data", "config", "plus", "chat")


class sttConfig:
    def __init__(self) -> None:
        """
        对 data\\config\\puls\\chat 下的stt_config.json文件进行管理
        :return None
        """
        self.fileDir: os.PathLike = os.path.join(
            PLUS_CONFIG_DIR, "stt_config.json"
        )
        # 文件不存在，进行新建
        if os.path.isfile(self.fileDir) is False:
            with open(self.fileDir, "w+", encoding="utf-8") as wfp:
                wfp.write(json.dumps(DEFAULT, indent=4))

    
    def read(self, key: str) -> Union[str, None]:
        """
        通过key对数据进行读取
        :param key: str 键
        :return Union[str, None]
        """
        with open(self.fileDir) as rfp:
            __read: Dict[str, str] = json.loads(rfp.read())
            value = __read.get(key)
            if not value:
                return None
            
        return value
