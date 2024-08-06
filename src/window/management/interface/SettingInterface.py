from typing import Union
from qfluentwidgets import (
    PushButton,
    ComboBox,
    LineEdit,
    IconWidget,
    BodyLabel,
    PrimaryPushButton,
    FluentIcon,
    InfoBarIcon
)
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QWidget, QVBoxLayout, QHBoxLayout
from src.window.management.interface.groupHeaderCard import GroupHeaderCardWidget


class MainWindow(QFrame):
    def __init__(self, windowName: str, parent: Union[QWidget, None] = None) -> None:
        super().__init__(parent)
        self.setObjectName(windowName.replace(' ', '-'))
        self.MainLayout = QVBoxLayout()
        self.GoupHeaderCard = GroupHeaderCardWidget()
        self.MainLayout.addWidget(self.GoupHeaderCard)
        self.setLayout(self.MainLayout)

        # 基础设置
        self.initBasicSetting()

    def initBasicSetting(self) -> None:
        self.GoupHeaderCard.setTitle("基础设置")
        self.GoupHeaderCard.setBorderRadius(8)

        self.settingPushButton = PushButton("设置")
        self.comboBox = ComboBox()
        self.lineEdit = LineEdit()

        self.hintIcon = IconWidget(InfoBarIcon.INFORMATION)
        self.hintLabel = BodyLabel("最后的确认 | ٩(๑òωó๑)۶")
        self.OkButton = PrimaryPushButton(FluentIcon.ACCEPT, "生效🥰")
        self.NoButton = PrimaryPushButton(FluentIcon.CANCEL_MEDIUM, "取消😟")
        self.bottomLayout = QHBoxLayout()

        self.settingPushButton.setFixedWidth(120)
        self.lineEdit.setFixedWidth(320)
        self.comboBox.setFixedWidth(320)
        self.comboBox.addItems(["不缩放", "2", "4", "8"])
        self.lineEdit.setPlaceholderText("输入你的 api key")

        # 设置底部工具栏布局
        self.hintIcon.setFixedSize(16, 16)
        self.bottomLayout.setSpacing(10)
        self.bottomLayout.setContentsMargins(24, 15, 24, 20)
        self.bottomLayout.addWidget(self.hintIcon, 0, Qt.AlignLeft)
        self.bottomLayout.addWidget(self.hintLabel, 0, Qt.AlignLeft)
        self.bottomLayout.addStretch(1)
        self.bottomLayout.addWidget(self.OkButton, 0, Qt.AlignRight)
        self.bottomLayout.addWidget(self.NoButton, 0, Qt.AlignRight)
        self.bottomLayout.setAlignment(Qt.AlignVCenter)

        # 添加组件到分组中
        self.GoupHeaderCard.addGroup(FluentIcon.MENU, "人物窗口", "设置人物的窗口外观，性能等", self.settingPushButton)
        self.GoupHeaderCard.addGroup(FluentIcon.ZOOM_OUT, "人物缩放", "设置当前人物的缩放倍数", self.comboBox)
        group = self.GoupHeaderCard.addGroup(FluentIcon.CODE, "ApiKey", "请输入正确的ApiKey", self.lineEdit)
        group.setSeparatorVisible(True)

        # 添加底部工具栏
        self.GoupHeaderCard.vBoxLayout.addLayout(self.bottomLayout)