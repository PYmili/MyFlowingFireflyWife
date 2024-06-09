import sys
from PyQt5.QtWidgets import QApplication
from src.gui import main

if __name__ == '__main__':
    # gui init
    main.logger.add("log\\latest.log", rotation="500 MB")
    app = QApplication(sys.argv)
    window = main.MainWindow()
    window.show()
    sys.exit(app.exec_())
