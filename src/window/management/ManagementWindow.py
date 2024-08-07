from typing import List, Any, Union

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QIcon, QDesktopServices
from PySide6.QtWidgets import (
    QFrame, QMainWindow,
    QHBoxLayout
)
from qfluentwidgets import (NavigationItemPosition, MessageBox, setTheme, Theme, MSFluentWindow,
                            NavigationAvatarWidget, qrouter, SubtitleLabel, setFont)
from qfluentwidgets import FluentIcon as FIF
from loguru import logger

from src.window.management.interface import ExtendInterface, SettingInterface


class UniversalWidget(QFrame):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = SubtitleLabel(text, self)
        self.hBoxLayout = QHBoxLayout(self)

        setFont(self.label, 24)
        self.label.setAlignment(Qt.AlignCenter)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)
        self.setObjectName(text.replace(' ', '-'))


class MainWindow(MSFluentWindow):
    def __init__(self, FireflyWindowParent: Union[QMainWindow, None] = None):
        super().__init__(parent=None)
        # 用于管理 firefly window
        self.SelfFireflyWindow: Union[QMainWindow, None] = FireflyWindowParent

        # create sub interface
        self.homeInterface = UniversalWidget('Home Interface', self)
        self.extendInterface = ExtendInterface.MainWindow('Extends Interface', self)
        self.settingface = SettingInterface.MainWindow('Setting Interface', self)
        self.settingface.FireflyWindowUpdate = FireflyWindowParent.updateConfig

        self.initNavigation()
        self.initWindow()

    def initNavigation(self):
        self.addSubInterface(self.homeInterface, FIF.HOME, '主页', FIF.HOME_FILL)
        self.addSubInterface(self.extendInterface, FIF.APPLICATION, '扩展')

        self.addSubInterface(self.settingface, FIF.SETTING, '设置', FIF.SETTING, NavigationItemPosition.BOTTOM)

        # 添加自定义导航组件
        self.navigationInterface.addItem(
            routeKey='Help',
            icon=FIF.HELP,
            text='帮助',
            onClick=self.helpMessageBox,
            selectable=False,
            position=NavigationItemPosition.BOTTOM,
        )

        self.navigationInterface.setCurrentItem(self.homeInterface.objectName())

    def initWindow(self):
        self.resize(960, 540)
        self.setWindowIcon(QIcon('data/assets/images/firefly/icon/icon.png'))
        self.setWindowTitle('MyFlowingFireflyWife')

    def helpMessageBox(self):
        messagebox = MessageBox(
            '支持作者🥰',
            '开发不易，如果您喜欢项目，可以考虑请开发者喝一瓶快乐水🥤。您的支持就是我们开发和维护项目的动力🚀',
            self
        )
        messagebox.yesButton.setText('必须滴！')
        messagebox.cancelButton.setText('下次一定')
        if messagebox.exec():
            QDesktopServices.openUrl(QUrl("https://github.com/PYmili/MyFlowingFireflyWife"))


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()