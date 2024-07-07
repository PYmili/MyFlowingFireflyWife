import os
import json
from typing import Union
from dataclasses import dataclass

extendsDir = os.path.join(os.getcwd(), "data", "config", "extends")


@dataclass
class ExtendInfoType:
    name: str = None
    author: str = None
    version: str = None
    isStatic: bool = False
    description: str = None


class ExtendType:
    def __init__(self) -> None:
        self.InfoJson: ExtendInfoType = ExtendInfoType

    def start() -> None:
        pass

    def stop() -> None:
        pass

    def settingWindow() -> None:
        pass

    @staticmethod
    def __infoJsonIsfile(extendName: str) -> Union[str, None]:
        if os.path.isdir(extendsDir) is False:
            os.makedirs(extendsDir)

        infoJsonFile = os.path.join(extendsDir, extendName, "info.json")
        if os.path.isfile(infoJsonFile) is False:
            with open(infoJsonFile, "w+", encoding="utf-8") as wfp:
                wfp.write(json.dumps(ExtendInfoType.__dict__, indent=4, ensure_ascii=False))
                
        return infoJsonFile

    @staticmethod
    def readInfoJson(extendName: str) -> ExtendInfoType:
        result = ExtendInfoType.__dict__
        infoJsonFile = ExtendType.__infoJsonIsfile(extendName)
        with open(infoJsonFile, "r", encoding="utf-8") as rfp:
            result = ExtendInfoType(**json.loads(rfp.read()))
        
        return result
    
    @staticmethod
    def writeInfoJson(extendName: str, newInfoJson: ExtendInfoType) -> None:
        infoJsonFile = ExtendType.__infoJsonIsfile(extendName)
        with open(infoJsonFile, "w+", encoding="utf-8") as wfp:
            wfp.write(json.dumps(newInfoJson.__dict__, indent=4, ensure_ascii=False))

