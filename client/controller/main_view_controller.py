import html
import os
import re

from PyQt5.QtCore import QModelIndex
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QMessageBox

from client.controller.database_view_controller import DatabaseEditor
from client.view.custom_treeview import CustomFileSystemModel
from client.view.main_view import MainWindowView
from utils.cmd_utils import compile_and_run
from utils.file_utils import extract_custom_headers_and_sources
from utils.str_utils import is_empty_or_whitespace, search_in_str


class MainWindowViewController(QMainWindow, MainWindowView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.entry_point = ""

        self.setup_ui(self)

        self.openFile.triggered.connect(self.open_File)
        self.exportReport.triggered.connect(self.export_report)
        self.exit.triggered.connect(self.try_exit)
        self.operate_database.triggered.connect(self.show_database_window)
        self.compile.triggered.connect(self.compile_and_run)

        self.treeView.doubleClicked.connect(self.get_selected_file_from_tree)
        self.search_button.clicked.connect(self.do_search)

    def open_File(self):

        dialog = QFileDialog()
        dialog.setNameFilter("C Source Files (*.c)")
        dialog.setViewMode(QFileDialog.Detail)

        if dialog.exec_():
            selected_file = dialog.selectedFiles()[0]
            if selected_file:
                self.entry_point = selected_file
                self.statusbar.showMessage(f"项目入口：{selected_file}")

                custom_headers, custom_sources = extract_custom_headers_and_sources(selected_file)
                paths = [os.path.abspath(header) for header in custom_headers] + [os.path.abspath(source) for source in
                                                                                  custom_sources]

                self.model = CustomFileSystemModel(paths)

                self.treeView.setModel(self.model)
                self.treeView.setRootIsDecorated(True)
                self.treeView.setSortingEnabled(True)
                # self.model.setRootPath(selected_file)
                self.model.setReadOnly(True)
                # 展开所有路径
                common_root = os.path.commonpath(paths)
                index = self.model.index(common_root)
                self.treeView.setRootIndex(index)
                self.treeView.expandAll()


            else:
                self.statusbar.showMessage("选择的文件夹无效")
                return

    def get_selected_file_from_tree(self, index: QModelIndex):
        if index.isValid():
            item = self.model.filePath(index)
            if os.path.isdir(item) or item.endswith(".pyc"):
                return
            if not item.endswith(".c") and not item.endswith(".h"):
                QMessageBox.information(self, "警告", "您选择的不是C源文件或C头文件，程序可能无法正常工作",
                                        QMessageBox.Yes)
            with open(item, "r") as file_:
                content = file_.read()
                self.sourceBroswer.setText(
                    f'<pre><code style="white-space: pre-wrap; font-family: inherit;">{html.escape(content)}</code></pre>')

    def do_search(self):
        content = self.search_line_edit.text()
        if is_empty_or_whitespace(content):
            self.sourceBroswer.setText(
                f'<pre><code style="white-space: pre-wrap; font-family: inherit;">{html.escape(self.sourceBroswer.toPlainText())}</code></pre>')
            return

        source_code = self.sourceBroswer.toPlainText()
        if is_empty_or_whitespace(source_code):
            return

        use_reg = self.regex_checkbox.isChecked()

        try:
            color_text = search_in_str(source_code, content, use_reg, on_match=handle_match,
                                       on_non_match=handle_non_match)
        except Exception as e:
            self.showError(e)
            return
        color_text = f'<pre><code style="white-space: pre-wrap; font-family: inherit;">{color_text}</code></pre>'

        self.sourceBroswer.setText(color_text)

    def export_report(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "",
                                                   "Json文档(*.json);;All Files (*)")
        report = "Some content from report system"
        if file_name:
            try:
                with open(file_name, 'w') as f:
                    f.write(report)
                self.showSuccessMessage(text="保存成功", title="成功")
            except Exception as e:
                self.showError(e)

    def try_exit(self):
        reply = QMessageBox.question(self, '提示', '确定退出吗？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.close()

    def show_database_window(self):
        self.db_window = DatabaseEditor(self)
        self.db_window.show()

    def compile_and_run(self):
        if not self.entry_point:
            self.showError("请先选择项目入口")
            return
        with open(self.entry_point, "r") as file:
            try:
                compile_and_run(file.read())
            except Exception as e:
                self.showError(e)
                return


def handle_non_match(string: str) -> str:
    safe = html.escape(string)
    return safe.replace('\n', '<br>')


def handle_match(match: re.Match) -> str:
    return f'<span style="color: {QColor("red").name()};">{html.escape(match.group())}</span>'
