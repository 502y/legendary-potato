import sys

from PyQt5.QtWidgets import QApplication

from client.controller.main_view_controller import MainWindowViewController

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindowViewController()
    window.show()
    sys.exit(app.exec_())
