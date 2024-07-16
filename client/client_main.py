import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

from client.controller.main_view_controller import MainWindowViewController

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindowViewController()
    window.setWindowIcon(QIcon("../assets/NEUS.png"))
    window.showMaximized()
    sys.exit(app.exec_())
