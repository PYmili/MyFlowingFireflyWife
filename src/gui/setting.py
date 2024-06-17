from typing import List, Any, Dict, Union

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QListWidget,
    QHBoxLayout,
    QTabWidget,
    QLabel, QPushButton,
    QListWidgetItem
)

from plugins import plugin


class StartPluginThread(QThread):
    result = Signal(bool)
    def __init__(self, _callback: callable) -> None:
        """使用线程启动Plugin"""
        super().__init__()
        self.__callback = _callback

    def run(self) -> None:
        self.__callback()
        self.result.emit(True)


class pluginSettingWindow(QWidget):
    def __init__(self, parent=None) -> None:
        """plugin的设置界面"""
        super().__init__(parent)
        layout = QHBoxLayout(self)
        self.setLayout(layout)

        # plugin的列表
        self.loader: Union[plugin.pluginLoader, None] = None
        self.pluginItems: List[Dict[Any, plugin.pluginDataType]] = []
        self.getpluginItems()
        self._callback: Union[plugin.pluginCallableType, None] = None
        self.pluginThread: Union[QThread, None] = None
        self.startPluginThread: Union[StartPluginThread, None] = None
        
        # 左侧列表
        self.pluginList = QListWidget()
        self.pluginList.itemClicked.connect(self.displaypluginDetails)
        self.populatepluginList()
        layout.addWidget(self.pluginList, 20)  # 分配左侧20%的空间
        
        # 右侧详情显示区
        self.detailsFrame = QWidget()
        self.detailsLayout = QVBoxLayout(self.detailsFrame)
        self.detailsLabel = QLabel()
        self.detailsLayout.addWidget(self.detailsLabel)
        layout.addWidget(self.detailsFrame, 80)  # 分配右侧80%的空间
    
    def getpluginItems(self):
        """获取所有pluginItems"""
        manager = plugin.pluginConfigManager()
        result = manager.readDataBypluginName()
        if result:
           self.pluginItems = result 
    
    def populatepluginList(self):
        """填充plugin列表"""
        for pluginItem in self.pluginItems:
            for name in pluginItem.keys():
                listItem = QListWidgetItem(name)
                self.pluginList.addItem(listItem)

    def displaypluginDetails(self, item):
        """显示选中plugin的详细信息"""
        for pluginItem in self.pluginItems:
            if item.text() not in pluginItem.keys():
                break
            value = pluginItem[item.text()]
            static = "启用" if value.static == "off" else "关闭"
            self.startPluginThread = StartPluginThread(lambda: self.enableOrDisablepluginEvent(item.text()))
            self.updateDetails(value)
            self.onOrOffButton = QPushButton(static)
            self.onOrOffButton.clicked.connect(self.startPluginThread.start)
            self.detailsLayout.addWidget(self.onOrOffButton)

    def enableOrDisablepluginEvent(self, pluginName: str) -> None:
        """启用指定的plugin"""
        # 使用加载器加载plugin
        self.loader = plugin.pluginLoader(pluginName)

        # 关闭plugin
        if self.onOrOffButton.text() == "关闭":
            if not self._callback:
                return None
            if self.loader.getStaitc() is False:
                return None
            result = self._callback.stop(self.pluginThread)
            if not result:
                return None
            self.onOrOffButton.setText("启动")
            self.loader.off()
            self.loader.save()
            return None
        
        # 启用plugin
        self._callback: plugin.pluginCallableType = self.loader.on()
        if not self._callback:
            return None
        self._callback = self._callback() # 将加载后的模块进行启动
        if self._callback is not None:
            self.pluginThread: QThread = self._callback.run()()
            self.pluginThread.start()
            self.onOrOffButton.setText("关闭")
            self.loader.save()

    def updateDetails(self, pluginData: plugin.pluginDataType):
        """更新右侧的详细信息显示"""
        static = "启动" if pluginData.static == "on" else "关闭"
        address = "\n\t".join(
            [key+':'+value for key, value in pluginData.address.items() if value != "null"]
        )
        self.detailsLabel.setText(
            f"作者: {pluginData.author}\n" +
            f"版本: {pluginData.version}\n"+
            f"简介: {pluginData.description}\n" +
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
        tabWidget.addTab(pluginSettingWindow(), "plugin")
