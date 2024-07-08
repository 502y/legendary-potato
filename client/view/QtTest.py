import os.path
import sys

from PyQt5.QtCore import QModelIndex
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QFileSystemModel, QMessageBox

from client.PyQt.demo import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = QFileSystemModel()
        self.setupUi(self)
        self.openFile.triggered.connect(self.open_File)
        self.treeView.doubleClicked.connect(self.getSelectedFileFromTree)

    def open_File(self):
        # file, file_type = QFileDialog.getOpenFileName(self, "打开文件", "", "C源文件(*.c);;所有文件(*)")
        #
        # if not file:  # 检查文件路径是否为空
        #     QMessageBox.information(self, "警告", "未选择任何文件！", QMessageBox.Yes)
        #     return
        #
        # if not file_type.startswith("C源文件"):
        #     QMessageBox.information(self, "警告", "您选择的不是C源文件，程序可能无法正常工作", QMessageBox.Yes)
        #
        # try:
        #     with open(file, "r") as file_:
        #         content = file_.read()
        #         # Enter point check
        #         print(content)
        #     self.statusbar.showMessage(f"程序入口：{file}")
        # except Exception as e:
        #     QMessageBox.critical(self, "错误", f"读取文件时发生错误：{str(e)}")
        dictionary = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if dictionary:
            self.statusbar.showMessage(f"项目路径：{dictionary}")

            self.model.setRootPath(dictionary)
            self.model.setReadOnly(True)

            self.treeView.setModel(self.model)
            self.treeView.setRootIndex(self.model.index(dictionary))

        else:
            self.statusbar.showMessage("选择的文件夹无效")

    def getSelectedFileFromTree(self, index: QModelIndex):
        if index.isValid():
            item = self.model.filePath(index)
            if os.path.isdir(item):
                return
            if not item.endswith(".c"):
                QMessageBox.information(self, "警告", "您选择的不是C源文件，程序可能无法正常工作", QMessageBox.Yes)
                with open(item, "r") as file_:
                    content = file_.read()
                    self.sourceBroswer.setText(content)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
