import os
from loguru import logger


PLUS_CONFIG_DIR = os.path.join(os.getcwd(), "data", "config", "plus", "chat")
if os.path.isdir(PLUS_CONFIG_DIR) is False:
    try:
        os.makedirs(PLUS_CONFIG_DIR)
    except Exception as e:
        logger.error(f"创建 {PLUS_CONFIG_DIR} 路径时出现错误：" + e)


from .main import sttQThread
