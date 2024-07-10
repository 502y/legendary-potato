from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QWidget, QTableView, QHeaderView, \
    QAbstractItemView, QMainWindow


class DatabaseEditorView(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("风险管理")
        self.resize(800, 600)

        self.init_ui()

    def init_ui(self):
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)

        layout = QVBoxLayout(self.main_widget)

        # 表格视图
        self.model = QStandardItemModel(self)
        self.table_view = QTableView(self)
        self.table_view.setModel(self.model)
        self.table_view.setSortingEnabled(True)
        self.table_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        layout.addWidget(self.table_view)

        # 控制按钮
        button_layout = QVBoxLayout()
        self.add_button = QPushButton("添加", self)
        button_layout.addWidget(self.add_button)

        self.del_button = QPushButton("删除", self)
        button_layout.addWidget(self.del_button)

        self.edit_button = QPushButton("修改", self)
        button_layout.addWidget(self.edit_button)

        self.query_button = QPushButton("查询", self)
        button_layout.addWidget(self.query_button)

        layout.addLayout(button_layout)
