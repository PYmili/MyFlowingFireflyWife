from typing import List, Any, Dict, Union

from PyQt5.QtCore import Qt, QThread
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QListWidget,
    QHBoxLayout,
    QTabWidget,
    QLabel, QPushButton,
    QListWidgetItem
)

from src import plus


class PlusSettingWindow(QWidget):
    def __init__(self, parent=None) -> None:
        """plus的设置界面"""
        super().__init__(parent)
        layout = QHBoxLayout(self)
        self.setLayout(layout)

        # plus的列表
        self.plusItems: List[Dict[Any, plus.plusDataType]] = []
        self.getPlusItems()
        self.plusCallback: Union[QThread, None] = None
        
        # 左侧列表
        self.plusList = QListWidget()
        self.plusList.itemClicked.connect(self.displayPlusDetails)
        self.populatePlusList()
        layout.addWidget(self.plusList, 20)  # 分配左侧20%的空间
        
        # 右侧详情显示区
        self.detailsFrame = QWidget()
        self.detailsLayout = QVBoxLayout(self.detailsFrame)
        self.detailsLabel = QLabel()
        self.detailsLayout.addWidget(self.detailsLabel)
        layout.addWidget(self.detailsFrame, 80)  # 分配右侧80%的空间
    
    def getPlusItems(self):
        """获取所有plusItems"""
        manager = plus.plusConfigManager()
        result = manager.readDataByPlusName()
        if result:
           self.plusItems = result 
    
    def populatePlusList(self):
        """填充plus列表"""
        for plusItem in self.plusItems:
            for name in plusItem.keys():
                listItem = QListWidgetItem(name)
                self.plusList.addItem(listItem)

    def displayPlusDetails(self, item):
        """显示选中plus的详细信息"""
        for plusItem in self.plusItems:
            if item.text() not in plusItem.keys():
                break
            value = plusItem[item.text()]
            static = "启用" if value.static == "off" else "关闭"
            self.updateDetails(value)
            self.onOrOffButton = QPushButton(static)
            self.onOrOffButton.clicked.connect(lambda: self.enableOrDisablePlusEvent(item.text()))
            self.detailsLayout.addWidget(self.onOrOffButton)

    def enableOrDisablePlusEvent(self, plusName: str) -> None:
        """启用指定的plus"""
        # 使用加载器加载plus
        loader = plus.plusLoader("src.plus." + plusName)

        # 关闭plus
        if self.onOrOffButton.text() == "关闭":
            if self.plusCallback:
                self.plusCallback.requestInterruption = True
                self.plusCallback.wait()
            self.onOrOffButton.setText("启动")
            loader.off()
            loader.save()
            return None
        
        # 启用plus
        _callback: plus.PlusCallableType = loader.on()
        if not _callback:
            return None
        _callback = _callback() # 将加载后的模块进行启动
        if _callback is not None:
            self.plusCallback: QThread = _callback.run()()
            self.plusCallback.start()
        self.onOrOffButton.setText("关闭")
        loader.save()

    def updateDetails(self, plusData: plus.plusDataType):
        """更新右侧的详细信息显示"""
        static = "启动" if plusData.static == "on" else "关闭"
        address = "\n\t".join(
            [key+':'+value for key, value in plusData.address.items() if value != "null"]
        )
        self.detailsLabel.setText(
            f"作者: {plusData.author}\n" +
            f"版本: {plusData.version}\n"+
            f"简介: {plusData.description}\n" +
            f"当前状态: {static}\n" + 
            f"开源地址: \n\t{address}" 
        )

class SettingsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        self.setWindowTitle("设置")
        self.resize(600, 400)
        
        # 创建一个QTabWidget用于管理左右两侧布局
        tabWidget = QTabWidget()
        layout.addWidget(tabWidget)
        
        # 选项菜单
        tabWidget.addTab(QWidget(), "基础")
        tabWidget.addTab(PlusSettingWindow(), "plus")
        
        