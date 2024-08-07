import os
import json
from typing import Union, Any
from loguru import logger

CONDIF_FILE = os.path.join(os.getcwd(), "data", "config", "main.json")
if os.path.isfile(CONDIF_FILE) is False:
    try:
        os.makedirs(CONDIF_FILE)
    except Exception as e:
        logger.info(e)


class ConfigFile:
    def __init__(self) -> None:
        self.data = self.read()

    def read(self) -> Union[dict, Any]:
        """
        读取 CONDFIG_FILE 中的json数据
        :return Union[dict, Any]
        """
        try:
            with open(CONDIF_FILE, "r", encoding="utf-8") as rfp:
                return json.loads(rfp.read())
        except Exception as e:
            logger.error(e)
            return {}
    
    def write(self) -> bool:
        """
        写入数据到配置文件
        :return bool
        """
        if not self.data:
            self.data = self.read()
            return self.write()
        with open(CONDIF_FILE, "w+", encoding="utf-8") as wfp:
            wfp.write(json.dumps(self.data, indent=4, ensure_ascii=False))
        return True

    def set(self, key: str, value: Union[str, bool, int]) -> None:
        """
        根据`key`值对配置文件内容修改。
        Params:
            key: str                | 需要匹配的关键字
            value: Union[str, bool] | 修改后的数据
        Returns:
            None
        """
        byKeyData = self.data.get(key)
        if byKeyData == None:
            logger.error(f"未找到: {key}")
            return 
        self.data[key] = value
        self.write()
