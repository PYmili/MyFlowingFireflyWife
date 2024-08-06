from typing import Dict
from .BatteryVoice.main import batteryVoice
from .extend import ExtendType


def initExtend(extend: ExtendType) -> ExtendType:
    extend = extend()
    if extend.InfoJson.isStatic is True:
        extend.start()
    return extend

allExtend: Dict[str, ExtendType] = {}

allExtend['BatteryVoice'] = initExtend(batteryVoice)