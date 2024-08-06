from loguru import logger


class Firefly:
    def __init__(self) -> None:
        self.__moodValue = 100         # 心情值
        self.__satietyValue = 100      # 饱食度
        self.__staminaValue = 100      # 体力值
    
    # get

    def getMoodValue(self) -> int:
        return self.__moodValue
    
    def getSatieyValue(self) -> int:
        return self.__satietyValue
    
    def getStaminaValue(self) -> int:
        return self.__staminaValue

    # set

    def setMoodValue(self, value: int) -> None:
        self.__moodValue = value

    def setSatieyValue(self, value: int) -> None:
        self.__satietyValue = value

    def setStaminaValue(self, value: int) -> None:
        self.__staminaValue = value

    def info(self) -> str:
        return f"Mood value: {self.__moodValue}; " \
            f"Satiey value: {self.__satietyValue}; " \
            f"Stamina value: {self.__staminaValue}; "
