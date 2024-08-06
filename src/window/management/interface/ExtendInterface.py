from typing import Union, Dict
from loguru import logger
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QFrame, QWidget, QVBoxLayout
from src.window.management.interface.card import AppCard
from src.extends import extend, allExtend as ALLEXTEND


class EnableExtendQThread(QThread):
    ButtonText = Signal(str)
    def __init__(self, _extend: extend.ExtendType) -> None:
        """启动或关闭 extend"""
        super().__init__(parent=None)
        self.extend = _extend

    def run(self) -> None:
        try:
            if self.extend.InfoJson.isStatic is True:
                # 关闭 extend
                result = "成功" if self.extend.stop() else "失败"
                logger.debug(f"关闭 extend name: {self.extend.InfoJson.name} {result}")
            else:
                # 启动 extend
                result = "成功" if self.extend.start() else "失败"
                logger.debug(f"启动 extend name: {self.extend.InfoJson.name} {result}")
        finally:
            self.ButtonText.emit("关闭" if self.extend.InfoJson.isStatic else "启动")


class MainWindow(QFrame):
    def __init__(self, windowName: str, parent: Union[QWidget, None] = None) -> None:
        super().__init__(parent)
        self.setObjectName(windowName.replace(' ', '-'))

        self.CardLayout = QVBoxLayout()
        self.setLayout(self.CardLayout)

        # card items，存储AppCard，方便调用
        self.cardItems: Dict[str, AppCard] = {}

        # 需要操作的extend
        self.extend: extend.ExtendType = None
        # extend的列表
        self.extendItems: Dict[str, extend.ExtendType] = ALLEXTEND
        self.initExtends()

    def initExtends(self) -> None:
        for _extend in self.extendItems.values():
            if not _extend:
                _extend = _extend()
            item = _extend.InfoJson
            _card = AppCard(
                icon="data/assets/images/icon/battery.png",
                title=item.name,
                content=item.description,
            )
            _card.openButton.setText("启动" if item.isStatic is False else "关闭")
            _card.openButton.clicked.connect(lambda: self.openButtonEvent(item.name))
            self.cardItems[item.name] = _card
            self.CardLayout.addWidget(_card)
            self.CardLayout.addStretch(1)

    def openButtonEvent(self, extendName: str) -> None:
        """
        开启/关闭 extends 按钮的事件。`将与crad中的按钮绑定事件`

        Params:
            extendName: str | 扩展的名称

        Returns:
            None
        """
        self.cardItems[extendName].openButton.setDisabled(True)
        _extend = self.extendItems.get(extendName)
        if not _extend:
            logger.error(f"从 extendItems 中， 未找到key: {extendName}。")
            return None
        
        def enableExtendEvent(result: str):
            self.cardItems[extendName].openButton.setText(result)
            self.cardItems[extendName].openButton.setDisabled(False)
        
        self.enableExtendThread = EnableExtendQThread(_extend)
        self.enableExtendThread.ButtonText.connect(enableExtendEvent)
        self.enableExtendThread.start()
