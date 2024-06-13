import os
import json
import random
from typing import *

from loguru import logger
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QMainWindow,
    QLabel,
    QMenu,
    QAction
)
from PyQt5.QtCore import Qt, QTimer, QRect, pyqtSignal

from .setting import SettingsWidget
from src.events import ActionEvent

INDEX_BG_IMAGE = "data/assets/images/firefly/default/bg.png"


class MainWindow(QMainWindow):
    start_timer_signal = pyqtSignal()
    stop_timer_signal = pyqtSignal()

    def __init__(self) -> None:
        """主窗口"""
        super().__init__()
        self.currentBgImage = INDEX_BG_IMAGE
        self.scaledToWidthSize = 0

        # 初始化action event
        self.actionEventQThread = ActionEvent(self.switchBackground)
        self.actionEventQThread.result.connect(self.ActionEventMethod)
        self.actionEventQThread.start_timer_signal.connect(self.startTimer)
        self.actionEventQThread.stop_timer_signal.connect(self.stopTimer)
        self.actionEventQThread.start()

        # 设置无边框、窗口始终置顶、窗口透明
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 加载并显示指定图片，并缩小一倍
        self.label = QLabel(self)
        if self.scaledToWidthSize > 0:
            self.pixmap = QPixmap(self.currentBgImage).scaledToWidth(self.scaledToWidthSize)
        else:
            self.pixmap = QPixmap(self.currentBgImage)
        self.switchBackground(self.currentBgImage)

        # 设置 QLabel 的大小
        self.label.resize(self.pixmap.size())

        # 将 QLabel 居中放置在窗口中央
        self.label.move(
            (self.width() - self.label.width()) // 2,
            (self.height() - self.label.height()) // 2
        )

        self.resize(self.pixmap.size())

        # 信息label
        self.messageQLabel = QLabel(self)
        self.messageQLabel.setStyleSheet("""
            QLabel {
                background-color: #FFD700; /* 背景颜色 */
                color: black; /* 文本颜色 */
                padding: 5px 10px; /* 内边距 */
                border-radius: 10px; /* 圆角 */
            }
        """)
        self.messageQLabel.adjustSize()
        self.messageQLabel.move(100, 90)
        self.messageQLabel.hide()

        self.menu = QMenu(self)
        # 自定义菜单样式表
        self.menu.setStyleSheet("""
            QMenu {
                background-color: #191919; /* 背景颜色 */
                border: 1px solid #262626; /* 边框颜色 */
                color: #EEEEEE; /* 文本颜色 */
            }
            QMenu::item {
                padding: 5px 20px; /* 菜单项内边距 */
            }
            QMenu::item:selected {
                background-color: #353535; /* 选中项背景颜色 */
            }
        """)

        # 创建设置界面
        self.settingsWidget = SettingsWidget()
        self.settingsWidget.hide()

        # 添加菜单项
        # 设置
        config_action = QAction("设置", self)
        config_action.triggered.connect(self.settingsWidget.show)
        self.menu.addAction(config_action)

        # 喂食
        feeding = QAction("喂食", self)
        feeding.triggered.connect(self.actionEventQThread.eatEvent)
        self.menu.addAction(feeding)

        # 睡觉
        sleepAction = QAction("睡觉", self)
        sleepAction.triggered.connect(self.actionEventQThread.sleepEvent)
        self.menu.addAction(sleepAction)

        # 退出程序
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        self.menu.addAction(exit_action)
        self.menu.hide()

    def mouseMoveEvent(self, event) -> None:
        """
        重写 mouseMoveEvent 以实现窗口拖动
        :return None
        """
        if event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.globalPos() - self.drag_pos)
            self.drag_pos = event.globalPos()
            event.accept()

    def mousePressEvent(self, event) -> None:
        """
        重写 mousePressEvent
        :return None
        """
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos()
            event.accept()
            # 新增摸头事件判断逻辑
            click_x = event.x()
            click_y = event.y()
            # 界面上半部分中心区域为摸头触发区
            trigger_width = int(self.width() / 2)  # 触发区宽度占窗口一半
            trigger_height = int(self.height() / 4)  # 触发区高度占窗口四分之一，位于上半部
            trigger_area = QRect(
                trigger_height - trigger_width // 2,
                0, trigger_width, trigger_height
            )
            
            if trigger_area.contains(event.pos()):
                # 用户点击了摸头触发区，执行摸头事件
                self.actionEventQThread.loveEvent()
            else:
                # 切换提起动作
                self.actionEventQThread.mentionEvent()
        elif event.button() == Qt.RightButton:
            # 在右键点击时显示菜单
            self.showMenu(event.globalPos())
    
    def mouseReleaseEvent(self, event) -> None:
        """
        重写鼠标释放
        :return None
        """
        if event.button() == Qt.LeftButton:
            event.accept()
            # 释放mention action, 重启 standbyAction
            self.actionEventQThread.standbyEvent()

    def close(self, event) -> None:
        """
        重写close
        :return None
        """
        # 判断当前action是否存在，进行释放
        if self.actionEventQThread:
            self.actionEventQThread.requestInterruption = True
            self.actionEventQThread.wait()
        if self.settingsWidget:
            self.settingsWidget.close()
        super().close()

    def changeImage(self, mood: str = None) -> None:
        """
        从 JSON 文件中随机选择并设置新的图片
        :param mood: 心情关键字
        :return None
        """
        emojiPackDir = os.path.join("data", "config", "emoji_pack.json")
        with open(emojiPackDir, "r") as f:
            data = json.load(f)
            if mood is None:
                mood = random.choice(list(data["moods"].keys()))
            try:
                files = random.choice(data['moods'][mood])['path']
                file_path = random.choice(files)
            except KeyError:
                logger.error("错误的关键字：" + mood)
                return None
            
            # 检查文件是否存在
            if os.path.exists(file_path) is False:
                logger.error("File does not exist: "\
                             f"path: {file_path}")
                return None
            
            # 图片重复，将重新获取
            if self.currentBgImage == file_path:
                self.changeImage()
                return None
            
            logger.info(f"mood: {mood}, file: {file_path}")
            self.switchBackground(file_path)
    
    def switchBackground(self, filePath: str) -> None:
        """
        切换背景图片
        :param filePath: str 文件路径
        :return None
        """
        if self.scaledToWidthSize > 0:
            self.pixmap = QPixmap(filePath).scaledToWidth(self.scaledToWidthSize)
        else:
            self.pixmap = QPixmap(filePath)
        self.label.setPixmap(self.pixmap)
        self.label.resize(self.pixmap.size())
        self.label.move(
            (self.width() - self.label.width()) // 2,
            (self.height() - self.label.height()) // 2
        )
        self.resize(self.pixmap.size())
        self.currentBgImage = filePath
            
    def showMenu(self, pos: tuple) -> None:
        """
        创建并显示右键菜单
        :param pos: tuple 当前鼠标坐标
        :return None
        """
        self.menu.show()
        self.menu.exec_(pos)

    def showMessage(self, text: str) -> None:
        """
        显示消息提示
        :param text: str 文本
        :return None
        """
        splitText = text.split("</end>")
        self.changeImage(mood=splitText[-1])
        # 设置定时隐藏信息
        self.timer = QTimer()
        self.timer.timeout.connect(self.timerHideMessageEvent)
        self.timer.start(5000)
    
    def timerHideMessageEvent(self) -> None:
        """
        定时隐藏信息框事件
        :return None
        """
        if self.timer:
            self.messageQLabel.hide()
            self.timer.stop()

    def ActionEventMethod(self, result: bool) -> None:
        """
        动作事件的返回方法
        :param result: bool 判断是否正常结束
        :return None
        """
        if not result:
            return None
        if self.actionEventQThread.sign != "Standby":
            self.actionEventQThread.standbyEvent()

    def startTimer(self) -> None:
        """启动执行动作的定时器"""
        if not hasattr(self, 'action_timer'):
            self.action_timer = QTimer(self)
            self.action_timer.timeout.connect(self.actionEventQThread.playNextImage)
        self.action_timer.start(250)

    def stopTimer(self) -> None:
        """停止执行动作的定时器"""
        if hasattr(self, 'action_timer'):
            self.action_timer.stop()
