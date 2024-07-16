from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMessageBox

stylesheet = """
QTextEdit {
    background-color: #cccccc; /* 灰色 */
}
"""

label_style = "QLabel { font-weight: bold; }"


class MainWindowView(object):

    def setup_ui(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 720)
        MainWindow.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        # 设置菜单栏
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, MainWindow.width(), 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        # 创建菜单
        self.menu_File = QtWidgets.QMenu(self.menubar)
        self.menu_File.setObjectName("menu_File")
        self.menu_tool = QtWidgets.QMenu(self.menubar)
        self.menu_tool.setObjectName("menu_tool")

        # 将菜单添加到菜单栏
        self.menubar.addAction(self.menu_File.menuAction())
        self.menubar.addAction(self.menu_tool.menuAction())
        # self.menubar.addAction(self.menu_Search.menuAction())

        # 创建动作
        self.openFile = QtWidgets.QAction(MainWindow)
        self.openFile.setObjectName("openFile")
        self.recentFile = QtWidgets.QMenu(MainWindow)
        self.recentFile.setObjectName("recentFile")
        self.exportReport = QtWidgets.QAction(MainWindow)
        self.exportReport.setObjectName("exportReport")
        self.operate_database = QtWidgets.QAction(MainWindow)
        self.operate_database.setObjectName("operate_database")
        self.compile = QtWidgets.QAction("compile")
        self.compile.setObjectName("compile")
        self.exit = QtWidgets.QAction(MainWindow)
        self.exit.setObjectName("exit")

        # 将动作添加到菜单
        self.menu_File.addAction(self.openFile)
        self.menu_File.addMenu(self.recentFile)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.exportReport)

        self.menu_tool.addAction(self.operate_database)
        self.menu_tool.addSeparator()
        self.menu_tool.addAction(self.compile)
        self.menu_tool.addSeparator()
        self.menu_tool.addAction(self.exit)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # 创建水平的 QSplitter
        horizontal_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal, self.centralwidget)

        # 在左边添加 QTreeView
        self.treeView = QtWidgets.QTreeView(self.centralwidget)
        self.treeView.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        horizontal_splitter.addWidget(self.treeView)

        # 创建垂直的 QSplitter
        vertical_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical, self.centralwidget)

        # 创建搜索栏布局
        search_layout = QtWidgets.QHBoxLayout()
        search_widget = QtWidgets.QWidget()

        # 创建搜索输入框
        self.search_line_edit = QtWidgets.QLineEdit()
        search_layout.addWidget(self.search_line_edit)

        # 创建搜索按钮
        self.search_button = QtWidgets.QPushButton("搜索")
        search_layout.addWidget(self.search_button)

        search_widget.setLayout(search_layout)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_widget.setMaximumHeight(50)
        vertical_splitter.addWidget(search_widget)

        # 创建正则选择器
        self.regex_checkbox = QtWidgets.QCheckBox("使用正则表达式", self)

        checkbox_layout = QtWidgets.QVBoxLayout()
        checkbox_layout.addWidget(self.regex_checkbox)
        checkbox_layout.setContentsMargins(0, 0, 0, 0)

        checkbox_widget = QtWidgets.QWidget()
        checkbox_widget.setLayout(checkbox_layout)
        vertical_splitter.addWidget(checkbox_widget)

        # 添加 QLabel
        label_risk = QtWidgets.QLabel("信息提示区", self.centralwidget)
        label_var = QtWidgets.QLabel("变量关系树列表", self.centralwidget)

        # 设置 QLabel 的样式
        label_risk.setStyleSheet(label_style)
        label_var.setStyleSheet(label_style)

        # 在垂直分割器中添加两个 QTextBrowser
        self.sourceBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.sourceBrowser.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        vertical_splitter.addWidget(self.sourceBrowser)

        self.riskBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.riskBrowser.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        vertical_splitter.addWidget(label_risk)
        vertical_splitter.addWidget(self.riskBrowser)

        vertical_splitter.setSizes([10, 10, 680, 10, 290])

        # 在右边添加垂直分割器
        right_vertical_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical, self.centralwidget)

        # 在垂直分割器中添加 QTextBrowser
        self.varBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.varBrowser.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        right_vertical_splitter.addWidget(label_var)
        right_vertical_splitter.addWidget(self.varBrowser)

        right_vertical_splitter.setSizes([10, 990])

        horizontal_splitter.addWidget(vertical_splitter)
        horizontal_splitter.addWidget(right_vertical_splitter)

        # 设置分割器的初始比例
        horizontal_splitter.setSizes([200, 400, 200])

        # 设置 centralwidget 作为 MainWindow 的中心部件，并将分割器添加到其中
        layout = QtWidgets.QVBoxLayout(self.centralwidget)
        layout.addWidget(horizontal_splitter)
        MainWindow.setCentralWidget(self.centralwidget)

        # 设置状态栏
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))

        self.menu_File.setTitle(_translate("MainWindow", "文件(&F)"))
        self.menu_tool.setTitle(_translate("MainWindow", "工具(&T)"))

        self.recentFile.setTitle(_translate("MainWindow", "最近打开的文件"))
        self.openFile.setText(_translate("MainWindow", "打开文件"))
        self.openFile.setShortcut(_translate("MainWindow", "Alt+O"))
        self.exportReport.setText(_translate("MainWindow", "导出报告"))
        self.exportReport.setShortcut(_translate("MainWindow", "Alt+E"))

        self.operate_database.setText(_translate("MainWindow", "修改风险库"))
        self.operate_database.setShortcut(_translate("MainWindow", "Alt+D"))
        self.compile.setText(_translate("MainWindow", "编译并运行"))
        self.compile.setShortcut(_translate("MainWindow", "Alt+C"))
        self.exit.setText(_translate("MainWindow", "退出"))
        self.exit.setShortcut(_translate("MainWindow", "Alt+X"))

    def showSuccessMessage(self, text: str, title: str):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText(text)
        msgBox.setWindowTitle(title)
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec_()

    def showError(self, error):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Critical)
        msgBox.setText(str(error))
        msgBox.setWindowTitle("错误")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec_()
