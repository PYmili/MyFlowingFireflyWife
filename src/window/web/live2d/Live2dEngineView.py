import os.path
import sys
import json
from PySide6.QtWidgets import QMainWindow, QApplication, QMenu
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtGui import QAction  # 正确的导入位置
from src.window.web.live2d import Live2dHttpServer


def readConfig() -> dict:
    """
    读取live2d的配置
    @return: dict
    """
    path = os.path.join(
        os.getcwd(),
        'data', 'config',
        'live2d.config.json')
    with open(path, 'r', encoding='utf-8') as f:
        return json.loads(f.read())


class CustomWebEngineView(QWebEngineView):
    # 定义一个信号，可以传递需要的数据
    pageLoaded = Signal(str)
    """
    自定义 QWebEngineView 类，添加右键菜单和窗口移动事件。
    """

    def __init__(self, parent=None):
        super(CustomWebEngineView, self).__init__(parent)
        # 全局变量，保存模型名称
        self.model_name = 'firefly'

        self.rightClickMenu = QMenu(self)
        # 刷新页面的 QAction
        self.refreshAction = QAction("刷新", self)
        self.refreshAction.triggered.connect(self.reload)

        # 切换模型链接 - 二级菜单
        self.modelMenu = QMenu("切换模型", self)
        self.fireflyAction = QAction("流萤", self)
        self.fireflyAction.triggered.connect(lambda: self.loadModel('firefly'))
        self.chunAction = QAction("椿", self)
        self.chunAction.triggered.connect(lambda: self.loadModel('chun'))
        self.modelMenu.addAction(self.fireflyAction)
        self.modelMenu.addAction(self.chunAction)
        self.rightClickMenu.addMenu(self.modelMenu)

        # 隐藏窗口的 QAction
        self.hideAction = QAction("退出", self)
        self.hideAction.triggered.connect(self.parent().close)
        # 添加右键菜单
        self.rightClickMenu.addAction(self.refreshAction)
        self.rightClickMenu.addAction(self.hideAction)

    def loadModel(self, model_name: str) -> None:
        """
        切换模型链接。
        :param model_name: 模型名称。
        """
        self.model_name = model_name
        url = f'http://127.0.0.1:8080/{model_name}'
        self.load(QUrl(url))

    # 当页面加载完成时，发出信号
    def loadFinished(self, result):
        if result:
            if self.model_name == 'chun':
                self.pageLoaded.emit('chun-reload')
            else:
                self.pageLoaded.emit(self.model_name)  # 发射信号，并传递模型名称

    def contextMenuEvent(self, event):
        """
        处理上下文菜单事件，显示自定义的右键菜单。

        @param event: 鼠标事件对象。
        """
        self.rightClickMenu.exec(event.globalPos())

    def closeEvent(self, event):
        """
        重写关闭窗口事件
        @param event:
        @return: None
        """
        sys.exit(1)


class MainWindow(QMainWindow):
    """
    主窗口类，负责创建和管理Live2D查看器的界面和交互。
    """

    def __init__(self):
        super().__init__()
        self.live2dConfigDict = readConfig()
        self.model_name = self.live2dConfigDict['current-model']
        self.server_thread = Live2dHttpServer.FlaskThread(8080)
        # 启动HTTP服务器线程
        self.server_thread.started.connect(self.startedConnection)
        self.server_thread.start()

        self.browser = CustomWebEngineView(self)
        # 设置自定义的 QWebEngineView
        self.browser.setMouseTracking(True)  # 开启鼠标跟踪
        self.browser.page().setBackgroundColor(Qt.transparent)  # 设置浏览器背景透明
        self.browser.pageLoaded.connect(self.adjustWindowSize)  # 连接信号
        self.setCentralWidget(self.browser)

        url = f'http://127.0.0.1:8080/{self.model_name}'
        # 设置HTML文件的路径
        self.browser.load(QUrl(url))

        self.setWindowTitle('Live2D Viewer')
        self.adjustWindowSize(self.model_name)

        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        # 设置窗口属性，包括无边框和始终置顶
        self.setAttribute(Qt.WA_TranslucentBackground)
        # 设置窗口背景透明
        self.browser.setAttribute(Qt.WA_TranslucentBackground)
        # 设置浏览器背景透明

        geometry = QApplication.primaryScreen().geometry()
        # 获取屏幕的几何信息
        self.move(geometry.width() - self.width() - 10, (geometry.height() - self.height()) - 50)
        # 设置窗口位置在屏幕的右下角

    def adjustWindowSize(self, model_name: str):
        """
        根据模型名称调整窗口大小。
        """
        if model_name == 'firefly':
            self.resize(int(self.width() / 1.5), int(self.height() / 1.5))
        elif model_name == 'chun':
            self.resize(self.width() // 2, self.height() + 85)
        elif model_name == 'chun-reload':
            self.resize(self.width() // 2, 960)

    def closeEvent(self, event):
        """
        窗口关闭事件处理，关闭HTTP服务器线程。
        @param event: 窗口事件对象。
        """
        self.server_thread.requestInterruption()
        self.server_thread.exit()
        self.server_thread.quit()
        return super().closeEvent(event)

    @staticmethod
    def startedConnection():
        """
        处理HTTP服务器连接启动事件。
        """
        print('startedConnection')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
