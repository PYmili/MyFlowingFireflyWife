import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QMainWindow, QLabel, QProgressBar

LOADING_GIF = os.path.join(
    os.path.split(__file__)[0], "data",
    "assets", "images", "firefly", "rotate.gif"
)


class loadingWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        
        # 初始化加载动画的QLabel
        self.loadingLabel = QLabel(self)
        self.loadingMovie = QMovie(LOADING_GIF)
        self.loadingMovie.setCacheMode(QMovie.CacheAll)  # 缓存所有帧
        self.loadingLabel.setMovie(self.loadingMovie)
        
        # 设置窗口属性
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(218, 300)  # 增加高度以容纳进度条

        # 设置QLabel的尺寸和位置
        self.loadingLabel.resize(self.width(), 200)  # 减去进度条的高度

        # 初始化进度条
        self.progressBar = QProgressBar(self)
         # 设置进度条样式表
        self.progressBar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #3a3a3a; /* 边框颜色 */
                border-radius: 20px; /* 圆角 */
                text-align: center; /* 文字居中 */
                color: #000000; /* 文字颜色 */
            }
            QProgressBar::chunk {
                background-color: #FFD700; /* 萤火虫黄色 */
                width: 20px; /* 进度块宽度 */
            }
        """)
        self.progressBar.setGeometry(0, 200, self.width(), 20)  # 位置在动画下方
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)

        # 启动动画
        self.loadingMovie.start()

    def update_progress_bar(self, number: int):
        """更新进度条"""
        self.progressBar.setValue(number)

    def hideLoadingAnimation(self):
        """隐藏加载动画和进度条"""
        self.loadingLabel.hide()
        self.progressBar.hide()

