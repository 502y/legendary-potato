import os

from PyQt5.QtCore import QModelIndex
from PyQt5.QtWidgets import QTreeView, QFileSystemModel, QVBoxLayout


class CustomFileSystemModel(QFileSystemModel):
    def __init__(self, paths):
        super().__init__()
        self.paths = {os.path.normpath(path) for path in paths}
        self.setRootPath('')

    def filterAcceptsRow(self, source_row, source_parent):
        index = self.index(source_row, 0, source_parent)
        file_path = os.path.normpath(self.filePath(index))
        return any(file_path.startswith(path) for path in self.paths)

    def hasChildren(self, parent=QModelIndex()):
        if not parent.isValid():
            return True
        file_path = os.path.normpath(self.filePath(parent))
        if os.path.isdir(file_path):
            return any(path.startswith(file_path) for path in self.paths)
        return False

    def isDir(self, index):
        file_path = os.path.normpath(self.filePath(index))
        return os.path.isdir(file_path)


class FileTreeViewer(QTreeView):
    def __init__(self, paths):
        super().__init__()

        self.tree = QTreeView()

        # # 展开所有路径
        # common_root = os.path.commonpath(paths)
        # index = self.model.index(common_root)
        # self.tree.setRootIndex(index)
        # self.tree.expandAll()

        layout = QVBoxLayout()
        layout.addWidget(self.tree)
        self.setLayout(layout)
