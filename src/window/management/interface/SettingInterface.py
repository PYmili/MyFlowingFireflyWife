from typing import Union
from qfluentwidgets import (
    PushButton,
    ComboBox,
    LineEdit,
    IconWidget,
    BodyLabel,
    PrimaryPushButton,
    FluentIcon,
    InfoBarIcon,
    SwitchButton, 
    TeachingTip, TeachingTipTailPosition
)
from loguru import logger
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QWidget, QVBoxLayout, QHBoxLayout
from src.window.firefly import FireflyWindowConfig
from src.window.management.interface.groupHeaderCard import GroupHeaderCardWidget


class MainWindow(QFrame):
    def __init__(self, window_name: str, parent: Union[QWidget, None] = None) -> None:
        super().__init__(parent)
        self.setObjectName(window_name.replace(' ', '-'))
        self.MainLayout = QVBoxLayout()
        self.GroupHeaderCard = GroupHeaderCardWidget()
        self.MainLayout.addWidget(self.GroupHeaderCard)
        self.setLayout(self.MainLayout)

        # 人物窗口的更新方法
        self.FireflyWindowUpdate: callable = None

        # 基础设置
        self.initBasicSetting()
        self.updateBasicSetting()

    def initBasicSetting(self) -> None:
        self.GroupHeaderCard.setTitle("基础设置")
        self.GroupHeaderCard.setBorderRadius(8)

        # 人物窗口设置
        self.settingPushButton = PushButton("设置")
        self.settingPushButton.clicked.connect(lambda: self.notWrittenTeachingTip(self.settingPushButton))
        self.settingPushButton.setFixedWidth(120)
        self.GroupHeaderCard.addGroup(FluentIcon.MENU, "人物窗口", "设置人物的窗口外观，性能等", self.settingPushButton)

        # 人物缩放选择
        self.comboBox = ComboBox()
        self.comboBox.setFixedWidth(320)
        self.comboBox.addItems(["0", "2", "4", "8"])
        self.GroupHeaderCard.addGroup(FluentIcon.ZOOM_OUT, "人物缩放", "设置当前人物的缩放倍数", self.comboBox)

        # 是否打开/关闭 启动程序音频和结束程序音频
        self.switchVoiceOnStart = SwitchButton()
        self.switchVoiceOnClose = SwitchButton()
        self.GroupHeaderCard.addGroup(
            FluentIcon.PLAY_SOLID, "启动音频", "设置程序启动时的音频播放", self.switchVoiceOnStart)
        self.GroupHeaderCard.addGroup(
            FluentIcon.PLAY_SOLID, "结束音频", "设置程序结束时的音频播放", self.switchVoiceOnClose)

        # 输入api key
        self.lineEdit = LineEdit()
        self.lineEdit.setFixedWidth(320)
        self.lineEdit.setPlaceholderText("输入你的 api key")
        self.lineEdit.textEdited.connect(lambda: self.notWrittenTeachingTip(self.lineEdit))
        group = self.GroupHeaderCard.addGroup(FluentIcon.CODE, "ApiKey", "请输入正确的ApiKey", self.lineEdit)
        group.setSeparatorVisible(True) # 添加末尾分隔

        # 配置生效确认
        self.hintIcon = IconWidget(InfoBarIcon.INFORMATION)
        self.hintIcon.setFixedSize(16, 16)
        self.hintLabel = BodyLabel("最后的确认 | ٩(๑òωó๑)۶")
        self.OkButton = PrimaryPushButton(FluentIcon.ACCEPT, "生效🥰")
        self.OkButton.clicked.connect(self.writeBasicSetting)
        self.NoButton = PrimaryPushButton(FluentIcon.CANCEL_MEDIUM, "取消😟")
        self.NoButton.clicked.connect(self.updateBasicSetting)

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

    def updateBasicSetting(self) -> None:
        """更新 `BasicSetting` 中的数据"""
        configFile = FireflyWindowConfig.ConfigFile()
        configFile.data = configFile.read()

        # 窗口缩小比例
        scaling = configFile.data.get("scaling", 0)
        for index in range(self.comboBox.count()):
            if self.comboBox.itemText(index) == str(scaling):
                self.comboBox.setCurrentIndex(index)

        # 启动程序音频和结束程序音频
        is_play_VoiceOnStart = configFile.data.get("is_play_VoiceOnStart", True)
        is_play_VoiceOnClose = configFile.data.get("is_play_VoiceOnClose", True)
        self.switchVoiceOnStart.setChecked(is_play_VoiceOnStart)
        self.switchVoiceOnClose.setChecked(is_play_VoiceOnClose)

    def writeBasicSetting(self) -> None:
        """将当前的配置写入"""
        try:
            configFile = FireflyWindowConfig.ConfigFile()
            configFile.set("scaling", int(self.comboBox.itemText(self.comboBox.currentIndex())))
            configFile.set("is_play_VoiceOnStart", self.switchVoiceOnStart.isChecked())
            configFile.set("is_play_VoiceOnClose", self.switchVoiceOnClose.isChecked())
            icon = InfoBarIcon.SUCCESS
            title = "成功！😄"
            content = "成功将数据载入缓存！"
        except Exception as e:
            logger.error(e)
            icon = InfoBarIcon.ERROR
            title = "失败！😶"
            content = "将数据载入缓存失败！"

        self.FireflyWindowUpdate()
        TeachingTip.create(
            target=self.OkButton,
            icon=icon,
            title=title,
            content=content,
            isClosable=True,
            tailPosition=TeachingTipTailPosition.BOTTOM,
            duration=2000,
            parent=self
        )
    
    def notWrittenTeachingTip(self, target):
        TeachingTip.create(
            target=target,
            icon=InfoBarIcon.WARNING,
            title='未响应...😴',
            content="抱歉，暂未编写该功能！😔",
            isClosable=True,
            tailPosition=TeachingTipTailPosition.BOTTOM,
            duration=2000,
            parent=self
        )