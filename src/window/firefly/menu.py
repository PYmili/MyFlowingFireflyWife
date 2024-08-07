from qfluentwidgets import (
    Action,
    FluentIcon,
    RoundMenu,
    MenuAnimationType
)
from PySide6.QtGui import QActionGroup
from src.window.management import ManagementWindow


class Menu:
    def __init__(self, parent=None) -> None:
        self.parent = parent

        self.manageAction = Action(
            FluentIcon.HOME_FILL, "管理",
            triggered=lambda: ManagementWindow.MainWindow(self.parent).show()
        )
        self.freeWalkingAction = Action(
            FluentIcon.APPLICATION, "游动",
            triggered=lambda: self.parent.setFreeWalking()
        )
        self.feedingAction = Action(
            FluentIcon.APPLICATION, "喂食",
            triggered=lambda: self.parent.actionEventQThread.eatEvent()
        )
        self.sleepAction = Action(
            FluentIcon.APPLICATION, "睡觉",
            triggered=lambda: self.parent.actionEventQThread.sleepEvent()
        )
        self.exitAction = Action(
            FluentIcon.EMBED, "退出",
            triggered=lambda: self.parent.close()
        )
        
    def contextMenuEvent(self, e):
        self.menu = RoundMenu()

        self.menu.addActions([self.manageAction])
        self.menu.addSeparator()
        self.menu.addActions([
            self.freeWalkingAction,
            self.sleepAction,
            self.feedingAction
        ])
        self.menu.addSeparator()
        self.menu.addAction(self.exitAction)

        self.menu.exec(e.globalPos(), aniType=MenuAnimationType.DROP_DOWN)
