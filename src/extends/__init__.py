from .BatteryVoice.main import batteryVoice
from .extend import ExtendType


def initExtend(extend: ExtendType) -> ExtendType:
    extend = extend()
    if extend.InfoJson.isStatic is True:
        extend.start()
    return extend

allExtend = []

allExtend.append(initExtend(batteryVoice))