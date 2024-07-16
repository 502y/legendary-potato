from PyQt5.QtCore import QThread, pyqtSignal


class Worker(QThread):
    progressChanged = pyqtSignal(float)
    taskCompleted = pyqtSignal()

    def run(self):
        # 模拟一个耗时操作，例如加载数据
        for i in range(100):
            self.sleep(1)  # 模拟耗时操作
            self.progressChanged.emit(i + 5)
        self.taskCompleted.emit()


from PyQt5.QtWidgets import QApplication, QMainWindow, QProgressBar, QPushButton, QVBoxLayout, QWidget, QMessageBox
import sys


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.loading = False
        self.initUI()

    def initUI(self):
        self.setWindowTitle("加载条示例")
        self.setGeometry(100, 100, 400, 200)

        self.progressBar = QProgressBar(self)
        self.progressBar.setGeometry(30, 40, 340, 25)

        self.button = QPushButton('开始加载', self)
        self.button.setGeometry(150, 80, 100, 30)
        self.button.clicked.connect(self.startLoading)

        self.worker = Worker()
        self.worker.progressChanged.connect(self.onProgressChanged)
        self.worker.taskCompleted.connect(self.onTaskCompleted)

        layout = QVBoxLayout()
        layout.addWidget(self.progressBar)
        layout.addWidget(self.button)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)

    def startLoading(self):
        if not self.loading:
            self.loading = True
            self.progressBar.setValue(0)
            self.worker.start()

    def onProgressChanged(self, value):
        self.progressBar.setValue(value)

    def onTaskCompleted(self):
        self.button.setEnabled(True)
        QMessageBox.information(self, "完成", "加载完成!")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
