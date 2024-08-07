import random
from typing import *

from loguru import logger
from PySide6.QtGui import QPixmap, QMouseEvent
from PySide6.QtWidgets import (
    QMainWindow,
    QLabel
)
from PySide6.QtCore import Qt, QTimer, QRect, Signal
from PySide6.QtWidgets import QApplication

from src.window.firefly.FireflyWindowConfig import ConfigFile
from src.ActionEvent import ActionEvent
from src.window.message.interface import PopupInterface, DEF_IMG
from src.FireflyVoicePack.main import FireflyVoicePackQThread
from src.ActionEvent.RoleProperties import Firefly as FireflyRole
from src.window.firefly.menu import Menu


class MainWindow(QMainWindow):
    startActionEventTimerSignal = Signal()
    stopActionEventTimerSignal = Signal()

    def __init__(self, app: QApplication) -> None:
        """主窗口"""
        super().__init__()
        self.app = app
        self.mainConfigFileObject = ConfigFile()    # 用于读取主窗口的配置文件

        self.currentBgImage = self.mainConfigFileObject.data.get(
            "currentBgImage", DEF_IMG)               # 当前背景图片
        self.scaling = self.mainConfigFileObject.data.get(
            "scaling", 0)                   # 背景图片缩小比例
        self.isPlayVoiceOnStart: bool = self.mainConfigFileObject.data.get(
            "is_play_VoiceOnStart", False)  # 是否播放程序启动音频
        self.isPlayVoiceOnClose: bool = self.mainConfigFileObject.data.get(
            "is_play_VoiceOnClose", False)  # 是否播放程序结束音频
        
        self.isFreeWalking = False  # 用于判断当前是否正在移动
        self.walkingDirection = random.choice(["left", "right"])    # 移动事件，从那个方向走动

        # 语言包配置
        self.fireflyVoicePackThread = None
        self.fireflyRoleObject = FireflyRole()

        # 初始化action event
        self.actionEventQThread = ActionEvent(self.switchBackground)
        self.actionEventQThread.result.connect(self.ActionEventMethod)
        self.actionEventQThread.startActionEventTimerSignal.connect(self.startTimer)
        self.actionEventQThread.stopActionEventTimerSignal.connect(self.stopTimer)
        self.actionEventQThread.start()

        # 设置无边框、窗口始终置顶、窗口透明、标题
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle("MyFlowingFireflyWife")

        # 加载并显示指定图片，并缩小指定倍
        self.label = QLabel(self)
        self.switchBackground(self.currentBgImage)

        # 右键菜单
        self.RightClickMenu = Menu(self)

    def contextMenuEvent(self, event):
        """右键菜单事件"""
        return self.RightClickMenu.contextMenuEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """重写 mouseMoveEvent 以实现窗口拖动"""
        if event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.globalPos() - self.drag_pos)
            self.drag_pos = event.globalPos()
            event.accept()
        return super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        重写 mousePressEvent
        :return None
        """
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos()
            event.accept()
            # 界面上半部分为摸头触发区
            trigger_height = self.height() / 4  # 触发区高度占窗口一半
            trigger_area = QRect(0, 0, self.width(), int(trigger_height))

            # 检查点击是否在摸头触发区域内
            if trigger_area.contains(event.pos()):
                self.actionEventQThread.loveEvent()  # 执行摸头动作
            else:
                # 切换提起动作
                self.actionEventQThread.mentionEvent()
        return super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """
        重写鼠标释放
        :return None
        """
        if event.button() == Qt.LeftButton:
            event.accept()
            # 释放mention action, 重启 standbyAction
            self.actionEventQThread.standbyEvent()
            self.isFreeWalking = False
        return super().mouseReleaseEvent(event)

    def closeEvent(self, event) -> None:
        """重写closeEvent"""
        # 播放退出语音
        self.hide()
        if self.isPlayVoiceOnClose is True:
            self.playFireflyVoice("VoiceOnClose")
        if self.fireflyVoicePackThread:
            self.fireflyVoicePackThread.exec_()

        try:
            self.stopTimer()
            # 判断当前action是否存在，进行释放
            if self.actionEventQThread:
                self.actionEventQThread.requestInterruption = True
                self.actionEventQThread.exit()
                self.actionEventQThread.wait()
        except Exception as e:
            logger.error(e)
        finally:
            return super().closeEvent(event)
    
    def showEvent(self, event) -> None:
        # 播放启动语音
        try:
            if self.isPlayVoiceOnStart is True:
                self.playFireflyVoice("VoiceOnStart")
        except Exception as e:
            logger.error(e)
        finally:
            return super().showEvent(event)

    def playFireflyVoice(self, key: str) -> None:
        """
        通过`key`值生成播放指定语音的线程
        :param key: str | 需要播放语音的key
        """
        self.fireflyVoicePackThread = FireflyVoicePackQThread(key)
        self.fireflyVoicePackThread.started.connect(self.VoicePackStartedCallback)
        self.fireflyVoicePackThread.start()

    def VoicePackStartedCallback(self, result: dict) -> None:
        """
        语音包播放后，获取`result`，并生成弹窗`PopupInterface`
        :param result: dict | 返回值
        """
        self.popupFace = PopupInterface(
            result['title'],
            result.get('img') if result.get('img') else DEF_IMG
        )
        self.popupFace.show()
    
    def switchBackground(self, filePath: str) -> None:
        """
        根据`filePath`值，切换背景图片
        :param filePath: str | 文件路径
        """
        pixmap = QPixmap(filePath)
        if self.scaling > 0:
            pixmap = pixmap.scaled(
                pixmap.width() // self.scaling,
                pixmap.height() // self.scaling,
                Qt.KeepAspectRatio
            )
        
        self.label.setPixmap(pixmap)
        self.label.resize(pixmap.size())
        self.resize(pixmap.size())
        self.currentBgImage = filePath

    def ActionEventMethod(self, result: str) -> None:
        """
        动作事件的返回方法
        :param result: bool | 判断是否正常结束
        """
        if not result:
            return None
        if result != "Standby" and self.isFreeWalking is False:
            self.actionEventQThread.standbyEvent()

        if self.isFreeWalking is True:
            self.actionEventQThread.load(self.walkingDirection)
            if self.walkingDirection == "left":
                moveFunc = self.FireflyMove("left")
            elif self.walkingDirection == "right":
                moveFunc = self.FireflyMove("right")
            moveFunc(self)
            # 检查是否到达屏幕边缘并改变方向
            if self.isFreeWalking:
                screen_geometry = self.app.primaryScreen().geometry()
                if (self.walkingDirection == "left" and self.x() <= screen_geometry.x()) or \
                   (self.walkingDirection == "right" and self.x() + self.width() >= screen_geometry.right()):
                    self.walkingDirection = "right" if self.walkingDirection == "left" else "left"
                    logger.info(f"Reached screen edge, turning to {self.walkingDirection}")
            
    def setFreeWalking(self) -> None:
        """设置为自由行动状态"""
        logger.info(f"If free walking: {self.isFreeWalking}")
        self.isFreeWalking = not self.isFreeWalking
        self.actionEventQThread.load(self.walkingDirection)

    def FireflyMove(self, direction: str) -> callable:
        """
        向指定方向移动`左右`
        :param direction: str | 方向， left or right
        :return callable~
        """
        def left(self):
            x = self.x()
            # 窗口向左移动，直到撞到屏幕左边界
            if x > 0:
                self.move(x - 15, self.y())

        def right(self):
            # 获取当前窗口位置和屏幕的尺寸
            x = self.x()
            screen = QApplication.primaryScreen().geometry()
            # 窗口向右移动，直到撞到屏幕右边界
            if x + self.width() < screen.width():
                self.move(x + 15, self.y())
        return left if direction == "left" else right

    def startTimer(self) -> None:
        """启动执行动作的定时器"""
        if not hasattr(self, 'action_timer'):
            self.action_timer = QTimer(self)
            self.action_timer.timeout.connect(self.actionEventQThread.playNextImage)
        self.action_timer.start(200)

    def stopTimer(self) -> None:
        """停止执行动作的定时器"""
        if hasattr(self, 'action_timer'):
            self.action_timer.stop()

    def updateConfig(self) -> None:
        """更新当前窗口的配置"""
        self.mainConfigFileObject = ConfigFile()
        self.mainConfigFileObject.data = self.mainConfigFileObject.read()
        # 更新数据
        self.scaling = self.mainConfigFileObject.data.get("scaling", 0)
        self.isPlayVoiceOnStart = self.mainConfigFileObject.data.get("is_play_VoiceOnStart", True)
        self.isPlayVoiceOnClose = self.mainConfigFileObject.data.get("is_play_VoiceOnClose", True)
