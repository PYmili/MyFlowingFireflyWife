import os
from typing import Union
import ctypes
from ctypes import wintypes
from qfluentwidgets import (
    ImageLabel, StrongBodyLabel, VBoxLayout, FluentIcon
)
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout
)
from PySide6.QtCore import Qt, QRect, QTimer
from PySide6.QtGui import QGuiApplication, QIcon

DEF_IMG = os.path.join(
    os.getcwd(), "data\\assets\\images\\firefly\\default\\bg.png"
)


class PopupInterface(QWidget):
    def __init__(
            self,
            content: str,
            icon: Union[str, QIcon, FluentIcon] = DEF_IMG,
            closeDelay: int = 5000
        ) -> None:
        super().__init__()
        # 设置窗口标志为无边框
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        # 设置窗口样式
        self.setStyleSheet("""
            QWidget {
                border-radius: 20px; /* 设置圆角大小 */
                background-color: #FFFFFF; /* 设置背景颜色为纯白色 */
            }
        """)

        # 设置窗口大小
        self.resize(350, 120)

        # 创建布局
        self.mainLayout = VBoxLayout(self)

        # 创建带图标的标签和文本
        self.iconLabel = ImageLabel(icon)
        self.iconLabel.scaledToHeight(80)
        self.iconLabel.setBorderRadius(8, 8, 8, 8)
        self.textLabel = StrongBodyLabel(content)
        # 创建内容的布局
        self.contentLayout = QHBoxLayout()
        self.contentLayout.addWidget(self.iconLabel)
        self.contentLayout.addWidget(self.textLabel)
        self.mainLayout.addLayout(self.contentLayout)

        # 设置窗口位置在当前屏幕的右下角，且不与任务栏重叠
        self.adjustPosition()

        # 设置窗口关闭的定时器
        self.close_timer = QTimer(self)  # 创建定时器
        self.close_timer.timeout.connect(self.close)  # 连接定时器信号到窗口关闭槽
        self.close_timer.start(closeDelay)  # 设置定时器时间，单位为毫秒

    def adjustPosition(self):
        # 获取屏幕的尺寸
        screen = QGuiApplication.primaryScreen().size()
        screen_width = screen.width()
        screen_height = screen.height()

        # 获取任务栏的位置和大小
        taskbar_rect = self.getTaskbarRect()
        taskbar_x = taskbar_rect.x()
        taskbar_y = taskbar_rect.y()
        taskbar_width = taskbar_rect.width()
        taskbar_height = taskbar_rect.height()

        # 计算窗口位置，确保不与任务栏重叠
        new_x = screen_width - self.width() - 10
        new_y = screen_height - self.height() - 10
        # 如果任务栏在右侧或左侧，调整窗口X坐标
        if taskbar_x != 0 and taskbar_width > 0:
            new_x -= taskbar_width
        # 如果任务栏在底部，调整窗口Y坐标
        if taskbar_y + taskbar_height == screen_height:
            new_y -= taskbar_height
        # 移动窗口到新位置
        self.move(new_x, new_y)

    def getTaskbarRect(self):
        # 加载 user32 库
        user32 = ctypes.WinDLL('user32.dll')
        # 使用 ctypes 创建 FindWindowW 函数的指针
        FindWindowW = user32.FindWindowW
        # 获取任务栏窗口句柄
        taskbar_handle = FindWindowW("Shell_TrayWnd", None)
        
        if taskbar_handle:
            # 获取任务栏窗口的矩形区域
            rectangle = wintypes.RECT()
            if user32.GetWindowRect(taskbar_handle, ctypes.byref(rectangle)):
                return QRect(
                    rectangle.left, rectangle.top, 
                    rectangle.right - rectangle.left,
                    rectangle.bottom - rectangle.top
                )
        
        return QRect(0, 0, 0, 0)

    def mouseDoubleClickEvent(self, event):
        """处理鼠标双击事件，关闭窗口"""
        if event.button() == Qt.LeftButton:
            self.close()

    def showEvent(self, event) -> None:
        """重写showEvent， 让当前窗口大小适应内容大小。"""
        self.resize(int(self.textLabel.width()*1.5), self.height())
        self.adjustPosition()
        super().showEvent(event)


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = PopupInterface(
        "test"
    )
    window.show()
    app.exec()