import os
import sys
import json
import random
from typing import *

from loguru import logger
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QMenu,
    QAction
)
from PyQt5.QtCore import Qt, QTimer

from Threads import *

INDEX_BG_IMAGE = "assets/images/firefly/Lovely/peeping.png"


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        """主窗口"""
        super().__init__()
        self.current_bg_image = INDEX_BG_IMAGE

        # 设置无边框、窗口始终置顶、窗口透明
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 加载并显示指定图片，并缩小一倍
        self.pixmap = QPixmap(self.current_bg_image).scaledToWidth(250)
        self.label = QLabel(self)
        self.label.setPixmap(self.pixmap)

        # 设置 QLabel 的大小为图片的大小
        self.label.resize(self.pixmap.size())

        # 将 QLabel 居中放置在窗口中央
        self.label.move(
            (self.width() - self.label.width()) // 2,
            (self.height() - self.label.height()) // 2
        )

        # 信息label
        self.message_label = QLabel(self)
        self.message_label.setStyleSheet("""
            QLabel {
                background-color: #FFD700; /* 背景颜色 */
                color: black; /* 文本颜色 */
                padding: 5px 10px; /* 内边距 */
                border-radius: 10px; /* 圆角 */
            }
        """)
        self.message_label.adjustSize()
        self.message_label.move(100, 90)
        self.message_label.hide()
        
        self.setGeometry(100, 100, 500, 500)

        # 启动线程
        self.start_stt_thread()

    # 重写 mouseMoveEvent 以实现窗口拖动
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.globalPos() - self.drag_pos)
            self.drag_pos = event.globalPos()
            event.accept()

    # 重写 mousePressEvent 以记录拖动起始位置，并切换图片
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos()
            event.accept()
            
            # 在点击时切换图片
            self.change_image()
        elif event.button() == Qt.RightButton:
            # 在右键点击时显示菜单
            self.show_menu(event.globalPos())

    def change_image(self, mood: str = None) -> None:
        """
        从 JSON 文件中随机选择并设置新的图片
        :param mood: 心情关键字
        :return None
        """
        with open("emoji_pack.json", "r") as f:
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
            if self.current_bg_image == file_path:
                self.change_image()
                return None
            
            logger.info(f"mood: {mood}, file: {file_path}")

            self.pixmap = QPixmap(file_path).scaledToWidth(250)
            self.label.setPixmap(self.pixmap)
            self.label.resize(self.pixmap.size())
            self.label.move(
                (self.width() - self.label.width()) // 2,
                (self.height() - self.label.height()) // 2
            )
            self.current_bg_image = file_path
                
    def show_menu(self, pos) -> None:
        """
        创建并显示右键菜单
        :return None
        """
        menu = QMenu(self)

        # 自定义菜单样式表
        menu.setStyleSheet("""
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

        # 添加菜单项
        config_action = QAction("设置", self)
        # config_action.triggered.connect()
        menu.addAction(config_action)
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        menu.addAction(exit_action)
        menu.exec_(pos)

    def show_message(self, text: str) -> None:
        """
        显示消息提示
        :return None
        """
        splitText = text.split("</end>")
        # 设置消息显示框的初始位置
        self.change_image(mood=splitText[-1])
        self.timer = QTimer()
        self.timer.timeout.connect(self.timerHideMessageEvent)
        self.timer.start(5000)
    
    def timerHideMessageEvent(self) -> None:
        """
        定时隐藏信息框事件
        :return None
        """
        if self.timer:
            self.message_label.hide()
            self.timer.stop()

    def start_stt_thread(self):
        """启动stt线程"""
        self.FireflysttQThread = sttQThread(loadingSTT(), self.message_label)
        self.FireflysttQThread.recognitionResultReady.connect(self.show_message)
        self.FireflysttQThread.start()


if __name__ == '__main__':
    # gui init
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
