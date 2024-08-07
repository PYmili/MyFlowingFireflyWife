# -*- coding: utf-8 -*-
import sys
from PySide6.QtWidgets import QApplication
from src.window.firefly import FireflyWindow

if __name__ == '__main__':
    # gui init
    FireflyWindow.logger.add("log/latest.log", rotation="500 MB")
    app = QApplication(sys.argv)
    window = FireflyWindow.MainWindow(app)
    window.show()
    app.exec()
    sys.exit(0)