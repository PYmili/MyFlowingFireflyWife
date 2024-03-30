import sys
import json
import random
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QMenu, QAction
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QObject, Qt, QTimer, QThread, pyqtSignal
from loguru import logger

from firefly import gpt, tts
from VoiceToText import (
    BaiduYun_STT,
    SoundRecording
)

INDEX_BG_IMAGE = "assets/images/firefly/main.gif"


class VoiceToTextThread(QThread):
    recognitionResultReady = pyqtSignal(str)
    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        self.ChatReusltText = ""

    def run(self) -> None:
        api = BaiduYun_STT()
        chat = gpt.Chat(self.getChatReusltCallback)
        while True:
            audio_bytes = SoundRecording()
            if not audio_bytes:
                continue
            result = api.SpeechToText(
                audio_bytes
            )
            if not result:
                continue

            chat.addMessage(result)
            chat.run()
            self.recognitionResultReady.emit(self.ChatReusltText.split("</end>")[0])
    
    def getChatReusltCallback(self, result_json: dict) -> None:
        """
        获取gpt返回数据的回调函数
        """
        if result_json['status_code'] != 200:
            logger.info("未获取到数据，API错误！")
            self.ChatReusltText = "未获取到数据，API错误！</end>Sadness"
            return None
        
        self.ChatReusltText = result_json['content']


class TTSPlayThread(QThread):
    def __init__(self, text: str, label: QLabel, parent = None) -> None:
        super().__init__(parent)
        self.text = text
        self.label = label
    
    def run(self) -> None:
        # 设置消息框的自动换行功能
        tts.FireFlyTTS(self.text).play(self.label)
        self.label.close()


class TransparentWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.FireFlyVoiceToText = VoiceToTextThread()
        self.FireFlyVoiceToText.recognitionResultReady.connect(self.show_message)
        self.FireFlyVoiceToText.start()
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

        self.setGeometry(100, 100, 500, 500)

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

    # 从 JSON 文件中随机选择并设置新的图片
    def change_image(self):
        with open("gif.json", "r") as f:
            data = json.load(f)
            gif_list = data["gif"]
            random_gif = random.choice(gif_list)
            random_path = random.choice(random_gif["path"])
            
            # 检查文件是否存在
            if os.path.exists(random_path) is False:
                print("File does not exist:", random_path)
                return None
            
            # 图片重复，将重新获取
            if self.current_bg_image == random_path:
                self.change_image()
                return None

            self.pixmap = QPixmap(random_path).scaledToWidth(250)
            self.label.setPixmap(self.pixmap)
            self.label.resize(self.pixmap.size())
            self.label.move(
                (self.width() - self.label.width()) // 2,
                (self.height() - self.label.height()) // 2
            )
            self.current_bg_image = random_path
                

    # 创建并显示右键菜单
    def show_menu(self, pos):
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

    # 显示消息提示
    def show_message(self, text):
        # 设置消息显示框的初始位置
        message_label = QLabel(self)
        message_label.setStyleSheet("""
            QLabel {
                background-color: #FFD700; /* 背景颜色 */
                color: black; /* 文本颜色 */
                padding: 5px 10px; /* 内边距 */
                border-radius: 10px; /* 圆角 */
            }
        """)
        message_label.adjustSize()
        message_label.move(100, 90)

        # 显示文本和tts
        self.tts_play = TTSPlayThread(text, message_label)
        self.tts_play.start()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TransparentWindow()
    window.show()
    sys.exit(app.exec_())
