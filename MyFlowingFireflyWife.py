import os
import sys
import json
import random
from typing import *

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QMenu,
    QAction
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from loguru import logger

from firefly import gpt, tts
from VoiceToText import (
    BaiduYun_STT,
    Funasr_STT,
    SoundRecording
)

INDEX_BG_IMAGE = "assets/images/firefly/Lovely/peeping.png"


def readConfig() -> dict:
    """
    读取config.json文件的数据
    :return dict
    """
    configJsonDir = os.path.join(os.getcwd(), "config.json")
    if os.path.isfile(configJsonDir) is False:
        with open(configJsonDir, "w+",encoding="utf-8") as fp:
            fp.write(json.dumps({
                "tts": "funasr"
            }))
        return {}
    with open(configJsonDir, "r", encoding="utf-8") as fp:
        __data = fp.read()
        if not __data:
            return {}

    return json.loads(__data)


def loadingSTT() -> Any:
    """
    对TTS进行加载。
    :return TTS_OBJECT
    """
    configData = readConfig()
    logger.info(f"read Config File: {configData}")
    stt = BaiduYun_STT()
    if configData.get('stt') == 'funasr':
        stt = Funasr_STT()
    else:
        stt = BaiduYun_STT()

    return stt


class VoiceToTextThread(QThread):
    recognitionResultReady = pyqtSignal(str)
    def __init__(self, stt: Any) -> None:
        """STT 线程"""
        super().__init__()
        self.tts = stt
        self.ChatReusltText = ""

    def run(self) -> None:
        chat = gpt.Chat(self.getChatReusltCallback)
        while True:
            audio_bytes = SoundRecording()
            if not audio_bytes:
                continue
            
            logger.info("start STT.")
            result = self.tts.SpeechToText(
                audio_bytes
            )
            if not result:
                continue

            chat.addMessage(result)
            chat.run()
            self.recognitionResultReady.emit(self.ChatReusltText)
    
    def getChatReusltCallback(self, result_json: dict) -> None:
        """
        获取gpt返回数据的回调函数
        """
        if result_json['status_code'] != 200:
            logger.info("未获取到数据，API错误！")
            self.ChatReusltText = "未获取到数据，API错误！</end>Sadness"
            return None
        
        self.ChatReusltText = result_json['content']


class TTSthread(QThread):
    ttsFinished = pyqtSignal(bool)

    def __init__(self, text: str, label: QLabel) -> None:
        super().__init__()
        self.text = text
        self.label = label

    def run(self) -> None:
        try:
            result = tts.FireFlyTTS(self.text).play(self.label)
            logger.info(f"TTS 结果: {result}")
            self.label.close()
            if not result:
                self.ttsFinished.emit(False)
            else:
                self.ttsFinished.emit(True)
        except Exception as e:
            logger.error(f"TTS 错误: {e}")
            self.ttsFinished.emit(False)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        """主窗口"""
        super().__init__()
        self.FireFlyVoiceToText = VoiceToTextThread(stt=loadingSTT())
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
    def change_image(self, mood: str = None):
        with open("emoji_pack.json", "r") as f:
            data = json.load(f)
            if mood is None:
                mood = random.choice(list(data["moods"].keys()))

            files = random.choice(data['moods'][mood])['path']
            file_path = random.choice(files)
            
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
                
    # 创建并显示右键菜单
    def show_menu(self, pos) -> None:
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
    def show_message(self, text) -> None:
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
        
        self.split_text = text.split("</end>")

        # 显示文本和tts
        self.tts_play = TTSthread(self.split_text[0], message_label)
        self.tts_play.ttsFinished.connect(self.on_tts_finished)
        self.tts_play.start()

    def on_tts_finished(self, success: bool) -> None:
        if not success:
            logger.error("TTS 播放失败。")
            return None
        
        logger.info("TTS 播放成功。")
        # 变换表情
        if self.split_text:
            self.change_image(mood=self.split_text[1])


if __name__ == '__main__':
    # gui init
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
