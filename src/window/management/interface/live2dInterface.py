import os.path
from typing import Union
from loguru import logger
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from qfluentwidgets import *
# 导入自定义卡片
from src.window.management.interface.card import AppCard
from src.window.web.live2d import Live2dEngineView


class MainWindow(QFrame):
    def __init__(self, window_name: str, parent: Union[QWidget, None] = None) -> None:
        super().__init__(parent)
        self.setObjectName(window_name.replace(' ', '-'))
        self.live2dEnginView = None

        self.live2dConfigDict = None
        self.__path = os.path.join(
            os.getcwd(),
            "data", "config", "live2d.config.json"
        )
        with open(self.__path, "r", encoding="utf-8") as f:
            self.live2dConfigDict = json.loads(f.read())

        # 主布局
        self.MainLayout = QVBoxLayout()
        # 头部卡片Widget
        self.GroupHeaderCard = GroupHeaderCardWidget()
        self.MainLayout.addWidget(self.GroupHeaderCard)
        self.setLayout(self.MainLayout)
        # 初始化界面
        self.initWindow()

    def initWindow(self) -> None:
        """
        初始化live2d设置界面
        @return: None
        """
        self.GroupHeaderCard.setTitle("设置")
        self.GroupHeaderCard.setBorderRadius(8)
        # 选择模型
        self.selectModelComboBox = ComboBox()
        self.selectModelComboBox.setFixedWidth(320)
        self.selectModelComboBox.addItems(["流萤", "椿"])
        self.selectModelComboBox.setCurrentIndex(
            0 if self.live2dConfigDict['current-model'] == 'firefly' else 1)
        self.GroupHeaderCard.addGroup(
            FluentIcon.ZOOM_OUT,
            "选择模型",
            "选择需要加载的live2d模型",
            self.selectModelComboBox
        )

        # 配置生效确认
        self.hintIcon = IconWidget(InfoBarIcon.INFORMATION)
        self.hintIcon.setFixedSize(16, 16)
        self.hintLabel = BodyLabel("最后的确认 | ٩(๑òωó๑)۶")
        self.OkButton = PrimaryPushButton(FluentIcon.ACCEPT, "生效🥰")
        self.OkButton.clicked.connect(self.OkButtonEvent)
        self.NoButton = PrimaryPushButton(FluentIcon.CANCEL_MEDIUM, "取消😟")
        # self.NoButton.clicked.connect(self.updateBasicSetting)

        # 设置底部工具栏布局
        self.bottomLayout = QHBoxLayout()
        self.bottomLayout.setSpacing(10)
        self.bottomLayout.setContentsMargins(24, 15, 24, 20)
        self.bottomLayout.addWidget(self.hintIcon, 0, Qt.AlignLeft)
        self.bottomLayout.addWidget(self.hintLabel, 0, Qt.AlignLeft)
        self.bottomLayout.addStretch(1)
        self.bottomLayout.addWidget(self.OkButton, 0, Qt.AlignRight)
        self.bottomLayout.addWidget(self.NoButton, 0, Qt.AlignRight)
        self.bottomLayout.setAlignment(Qt.AlignVCenter)
        # 添加底部工具栏
        self.GroupHeaderCard.vBoxLayout.addLayout(self.bottomLayout)

    def showLive2dEngineViewWindow(self) -> None:
        self.live2dEnginView = Live2dEngineView.MainWindow()
        self.live2dEnginView.show()

    def OkButtonEvent(self) -> None:
        """
        确认按钮的触发事件
        @return: None
        """
        # 获取用户选择的model名字
        Live2dModelName = self.selectModelComboBox.itemText(
            self.selectModelComboBox.currentIndex())
        if not Live2dModelName:
            return logger.warning("未获取到Live2D模型名称")
        if self.live2dConfigDict is None:
            return
        self.live2dConfigDict['current-model'] = "firefly" if Live2dModelName == "流萤" else "chun"
        with open(self.__path, "w", encoding="utf-8") as f:
            f.write(json.dumps(self.live2dConfigDict, indent=4, ensure_ascii=False))

        if self.live2dEnginView is None:
            self.showLive2dEngineViewWindow()
