from typing import List, Any, Dict, Union

from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QListWidget,
    QHBoxLayout,
    QTabWidget,
    QLabel, QPushButton,
    QListWidgetItem
)
from loguru import logger

from src.extends import extend
from src.extends import allExtend as ALLEXTEND
from src.gui.window import InfoWindow


class extendSettingWindow(QWidget):
    def __init__(self, parent=None) -> None:
        """extend的设置界面"""
        super().__init__(parent)
        layout = QHBoxLayout(self)
        self.setLayout(layout)

        # 需要操作的extend
        self.extend: extend.ExtendType = None

        # extend的列表
        self.extendItems: List[extend.ExtendType] = ALLEXTEND
        
        # 左侧列表
        self.extendList = QListWidget()
        # 连接信号与槽
        self.extendList.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.extendList, 20)   # 分配左侧20%的空间
        # 填充左侧列表
        self.fill_extend_list()
        
        # 右侧详情显示区
        self.detailsFrame = QWidget()
        self.detailsLayout = QVBoxLayout(self.detailsFrame)
        self.detailsLabel = QLabel()
        self.detailsLabel.setStyleSheet("font-size: 15px;")
        self.detailsLayout.addWidget(self.detailsLabel)
        self.extendRunOrStopButton = QPushButton()  # 启动或关闭按钮
        layout.addWidget(self.detailsFrame, 80) # 分配右侧80%的空间

    def fill_extend_list(self):
        """填充左侧列表项"""
        for _extend in self.extendItems:
            _extend = _extend()
            item = QListWidgetItem(_extend.InfoJson.name)
            # 可以将整个ExtendType对象作为item的用户数据，以便在槽函数中访问
            item.setData(Qt.UserRole, _extend)
            self.extendList.addItem(item)
    
    def on_item_clicked(self, item: QListWidgetItem):
        """处理列表项点击事件"""
        self.extend: extend.ExtendType = item.data(Qt.UserRole)
        details_text = f"名称: {self.extend.InfoJson.name}\n" \
                    f"作者: {self.extend.InfoJson.author}\n" \
                    f"版本: {self.extend.InfoJson.version}\n" \
                    f"是否启动: {'Yes' if self.extend.InfoJson.isStatic else 'No'}\n" \
                    f"简介: {self.extend.InfoJson.description}"
        self.detailsLabel.setText(details_text)
        self.extendRunOrStopButton.setText("关闭" if self.extend.InfoJson.isStatic else "启动")
        self.extendRunOrStopButton.clicked.connect(self.extendRunOrStopEvent)
        self.detailsLayout.addWidget(self.extendRunOrStopButton)

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


class SettingsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        self.setWindowTitle("设置")
        self.resize(600, 400)
        
        # 创建一个QTabWidget用于管理左右两侧布局
        self.tabWidget = QTabWidget()
        layout.addWidget(self.tabWidget)
        
        # 选项菜单
        self.theextendSettingWindow = extendSettingWindow()
        self.tabWidget.addTab(QWidget(), "基础")
        self.tabWidget.addTab(self.theextendSettingWindow, "extends")
