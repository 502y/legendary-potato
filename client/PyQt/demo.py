from PyQt5 import QtCore, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
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
        self.menu_Search = QtWidgets.QMenu(self.menubar)
        self.menu_Search.setObjectName("menu_Search")

        # 将菜单添加到菜单栏
        self.menubar.addAction(self.menu_File.menuAction())
        self.menubar.addAction(self.menu_Search.menuAction())

        # 创建动作
        self.openFile = QtWidgets.QAction(MainWindow)
        self.openFile.setObjectName("openFile")
        self.exportReport = QtWidgets.QAction(MainWindow)
        self.exportReport.setObjectName("exportReport")

        # 将动作添加到菜单
        self.menu_File.addAction(self.openFile)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.exportReport)

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

        # 在垂直分割器中添加两个 QTextBrowser
        self.sourceBroswer = QtWidgets.QTextBrowser(self.centralwidget)
        self.sourceBroswer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        vertical_splitter.addWidget(self.sourceBroswer)

        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        vertical_splitter.addWidget(self.textBrowser)

        vertical_splitter.setSizes([700, 300])

        # 在右边添加 QTextBrowser
        self.textBrowser_2 = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser_2.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        horizontal_splitter.addWidget(vertical_splitter)
        horizontal_splitter.addWidget(self.textBrowser_2)

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
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))

        self.menu_File.setTitle(_translate("MainWindow", "文件(&F)"))
        self.menu_Search.setTitle(_translate("MainWindow", "搜索(&S)"))
        self.openFile.setText(_translate("MainWindow", "打开文件"))
        self.openFile.setShortcut(_translate("MainWindow", "Alt+O"))
        self.exportReport.setText(_translate("MainWindow", "导出报告"))
        self.exportReport.setShortcut(_translate("MainWindow", "Alt+E"))
