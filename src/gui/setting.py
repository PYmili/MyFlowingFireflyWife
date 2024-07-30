from typing import List, Any, Union

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QListWidget,
    QHBoxLayout,
    QTabWidget,
    QLabel, QPushButton,
    QListWidgetItem,
    QComboBox
)
from loguru import logger

from src.extends import extend
from src.extends import allExtend as ALLEXTEND
from src.gui.window import InfoWindow
from src.gui.mainConfig import mainConfigFile


class UniversalWidget(QWidget):
    """setting通用的QWidget"""
    def __init__(self) -> None:
        super().__init__(parent=None)
        self.layout = QHBoxLayout(self)
        self.setLayout(self.layout)

        # 左侧列表
        self.LeftList = QListWidget()
        self.LeftList.itemClicked.connect(self.onItemClickedEvent)
        self.layout.addWidget(self.LeftList, 20)   # 分配左侧20%的空间

        # 右侧详情显示区
        self.detailsFrame = QWidget()
        self.detailsLayout = QVBoxLayout(self.detailsFrame)
        self.layout.addWidget(self.detailsFrame, 80) # 分配右侧80%的空间

    def onItemClickedEvent(self, item: QListWidgetItem) -> None:
        logger.debug(item)

    def clearLayout(self, layout: Union[QHBoxLayout, QVBoxLayout]):
        # 遍历布局中的所有控件
        while layout.count():
            # 移除并删除控件
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                # 如果是子布局，递归调用
                self.clearLayout(child.layout())
                # 删除子布局
                child.layout().deleteLater()


class ExtendSettingWindow(UniversalWidget):
    def __init__(self) -> None:
        """extend的设置界面"""
        super().__init__()

        # 需要操作的extend
        self.extend: extend.ExtendType = None
        # extend的列表
        self.extendItems: List[extend.ExtendType] = ALLEXTEND
        
        # 填充左侧列表
        self.fillExtendList()
        # 右侧的显示区域添加
        self.detailsLabel = QLabel()
        self.detailsLabel.setStyleSheet("font-size: 15px;")
        self.detailsLayout.addWidget(self.detailsLabel)
        self.extendRunOrStopButton = QPushButton()  # 启动或关闭按钮

    def fillExtendList(self):
        """填充左侧列表项"""
        for _extend in self.extendItems:
            if not _extend:
                _extend = _extend()
            item = QListWidgetItem(_extend.InfoJson.name)
            # 可以将整个ExtendType对象作为item的用户数据，以便在槽函数中访问
            item.setData(Qt.UserRole, _extend)
            self.LeftList.addItem(item)
    
    def onItemClickedEvent(self, item: QListWidgetItem):
        """处理列表项点击事件"""
        self.extend: extend.ExtendType = item.data(Qt.UserRole)
        detailsText = f"名称: {self.extend.InfoJson.name}\n" \
                    f"作者: {self.extend.InfoJson.author}\n" \
                    f"版本: {self.extend.InfoJson.version}\n" \
                    f"是否启动: {'Yes' if self.extend.InfoJson.isStatic else 'No'}\n" \
                    f"简介: {self.extend.InfoJson.description}"
        self.detailsLabel.setText(detailsText)
        self.extendRunOrStopButton.setText("关闭" if self.extend.InfoJson.isStatic else "启动")
        self.extendRunOrStopButton.clicked.connect(self.extendRunOrStopEvent)
        self.detailsLayout.addWidget(self.extendRunOrStopButton)
        return super().onItemClickedEvent(item)

    def extendRunOrStopEvent(self) -> None:
        """启动或关闭扩展事件"""
        if not self.extend:
            logger.error("未正确载入extend!")
            return
        
        self.extendRunOrStopButton.setEnabled(False)
        if self.extend.InfoJson.isStatic is False:
            logger.info(f"启动 extend: {self.extend.InfoJson.name}")
            self.extend.start()
        elif self.extend.InfoJson.isStatic is True:
            logger.info(f"关闭 extend: {self.extend.InfoJson.name}")
            self.extend.stop()
        self.extendRunOrStopButton.setText("关闭" if self.extend.InfoJson.isStatic else "启动")
        self.infoWindow = InfoWindow(f"操作extend: {self.extend.InfoJson.name}成功！")
        self.infoWindow.show()
        self.extendRunOrStopButton.setEnabled(True)


class BasicsSettingWindow(UniversalWidget):
    def __init__(self, mainUpdateConfig: Any) -> None:
        super().__init__()
        self.LeftList.addItem(QListWidgetItem("外观"))
        self.LeftList.addItem(QListWidgetItem("关于"))

    def onItemClickedEvent(self, item: QListWidgetItem) -> None:
        if item.text() == "外观":
            self.appearanceSettingWindow()
        self.clearLayout(self.detailsLayout)
        return super().onItemClickedEvent(item)
    
    def appearanceSettingWindow(self) -> None:
        self.appearanceSettingWindowLayout = QHBoxLayout()

        # 窗口人物的缩小倍数配置 scaledToWidthSize
        self.SetScaledToWidthSizeLabel = QLabel("人物缩小倍数：")
        self.appearanceSettingWindowLayout.addWidget(self.SetScaledToWidthSizeLabel, 1)
        self.comboBox = QComboBox()
        self.comboBox.addItems(["0", "2", "4", "8"])
        self.appearanceSettingWindowLayout.addWidget(self.comboBox, 9)

        self.detailsLayout.addLayout(self.appearanceSettingWindowLayout)
    

class SettingsWidget(QWidget):
    def __init__(self, mainUpdateConfig: Any):
        super().__init__(parent=None)
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        self.setWindowTitle("设置")
        self.resize(600, 400)
        
        # 创建一个QTabWidget用于管理左右两侧布局
        self.tabWidget = QTabWidget()
        self.tabWidget.setStyleSheet("""
            QTabWidget::tab-bar {
                alignment: left; /* 将标签对齐到左侧 */
            }
            QTabBar::tab {
                background: white;
                color: black; /* 设置默认标签背景色 */
                border: 1px solid #888; /* 设置标签边框 */
            }
            QTabBar::tab:selected {
                background: aterrimus; /* 设置选中标签背景色 */
                color: grey; /* 设置选中标签文字颜色 */
            }
            QTabBar::tab:hover {
                background: black; /* 设置悬停标签背景色 */
                border-top: 2px solid white; /* 设置悬停标签边框颜色 */
            }
        """)
        layout.addWidget(self.tabWidget)
        
        # 选项菜单
        self.IconSize = QSize(128, 128)
        self.basicsSettingWindowObj = BasicsSettingWindow(mainUpdateConfig)
        self.extendSettingWindowObj = ExtendSettingWindow()
        self.basicsSettingWindowTabIcon = QIcon("data/assets/images/icon/function-icon.png").pixmap(self.IconSize)
        self.extendSettingWindowTabIcon = QIcon("data/assets/images/icon/extend-icon.png").pixmap(self.IconSize)
        self.tabWidget.addTab(self.basicsSettingWindowObj, self.basicsSettingWindowTabIcon, "基础")
        self.tabWidget.addTab(self.extendSettingWindowObj, self.extendSettingWindowTabIcon, "扩展")
