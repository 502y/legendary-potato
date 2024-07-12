import html
import json
import os
import re

from PyQt5.QtCore import QModelIndex
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QMessageBox
from ordered_set import OrderedSet

from client.controller.database_view_controller import DatabaseEditor
from client.model.LLVMGeneratedModel import LLVMGeneratedModel, cursor_kind_dict, cursor_kind_ignore_set
from client.view.custom_treeview import CustomFileSystemModel
from client.view.main_view import MainWindowView
from funcTrace.AstTreeJson import AST_Tree_json
from utils.cmd_utils import compile_and_run
from utils.file_utils import extract_custom_headers_and_sources
from utils.str_utils import is_empty_or_whitespace, search_in_str


class MainWindowViewController(QMainWindow, MainWindowView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.entry_point = ""
        self.ast_instance: LLVMGeneratedModel

        self.setup_ui(self)

        self.openFile.triggered.connect(self.open_File)
        self.exportReport.triggered.connect(self.export_report)
        self.exit.triggered.connect(self.try_exit)
        self.operate_database.triggered.connect(self.show_database_window)
        self.compile.triggered.connect(self.compile_and_run)

        self.treeView.doubleClicked.connect(self.get_selected_file_from_tree)
        self.search_button.clicked.connect(self.do_search)

        self.var_set = OrderedSet()
        self.info_text = ""

    def open_File(self):

        dialog = QFileDialog()
        dialog.setNameFilter("C Source Files (*.c)")
        dialog.setViewMode(QFileDialog.Detail)

        if dialog.exec_():
            selected_file = dialog.selectedFiles()[0]
            # 判断是否包含C入口
            with open(selected_file, "r") as file:
                content = file.read()

                pattern = r"\b(int|void)\b\s+main\s*\(\s*(?:int\s+argc,\s*(?:char\s*\*\s*){1,2}argv\[\])?\s*\)\s*\{.*\}"
                if len(re.findall(pattern, content)):
                    QMessageBox.information(self, "警告", "请选择包含main函数的C源文件", QMessageBox.Yes)
                    return

            if selected_file:
                self.entry_point = selected_file
                self.statusbar.showMessage(f"项目入口：{selected_file}")

                # 包含头文件、源文件分析
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

                self.show_source_code(selected_file)

            else:
                self.statusbar.showMessage("选择的文件无效")
                return

    def get_selected_file_from_tree(self, index: QModelIndex):
        if index.isValid():
            item = self.model.filePath(index)
            if os.path.isdir(item) or item.endswith(".pyc"):
                return
            if not item.endswith(".c"):
                QMessageBox.information(self, "警告", "您选择的不是C源文件，程序可能无法正常工作",
                                        QMessageBox.Yes)
            self.show_source_code(item)

    def show_source_code(self, path):
        with open(path, "r") as file_:
            content = file_.read()
            self.sourceBroswer.setText(
                f'<pre><code style="white-space: pre-wrap; font-family: inherit;">{html.escape(content)}</code></pre>')
        self.var_set = OrderedSet()
        var_text = ""
        try:
            self.generate_ast(path)
            self.analyze_ast(self.ast_instance, path)

        except Exception as e:
            print(e)
        finally:
            for item in self.var_set:
                var_text = var_text + item
            self.varBrowser.setText(var_text)

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

    def generate_ast(self, path):
        ast_obj = AST_Tree_json(path)
        json_ = ast_obj.start()
        data = json.loads(json_)
        try:
            self.ast_instance = LLVMGeneratedModel.from_dict(data)
        except Exception as e:
            print(e)

    def analyze_ast(self, ast_ins, file):
        while True:
            has_child = False
            if ast_ins.file == file and ast_ins.spelling != file:
                if ast_ins.kind in cursor_kind_dict:
                    if ast_ins and ast_ins.spelling is not None and ast_ins.kind is not None and ast_ins.file is not None and ast_ins.location is not None:
                        # if ast_ins.kind is CursorKind.VAR_DECL:
                        #    self.var_set.add(f"变量声明：{ast_ins.spelling} line {ast_ins.location[0]}<br>")
                        # elif ast_ins.kind is CursorKind.TYPE_REF:
                        #     self.var_set.add(f"变量类型：{ast_ins.spelling}<br><br>")
                        # elif ast_ins.kind is CursorKind.FUNCTION_DECL:
                        #     self.var_set.add(f"函数声明：{ast_ins.spelling}() line {ast_ins.location[0]}<br><br>")
                        # elif ast_ins.kind is CursorKind.PARM_DECL:
                        #     self.var_set.add(f"参数声明：{ast_ins.spelling}() line {ast_ins.location[0]}<br><br>")
                        # elif ast_ins.kind is CursorKind.MEMBER_REF:
                        #     self.var_set.add(f"成员声明：{ast_ins.spelling} line {ast_ins.location[0]}<br><br>")
                        # elif ast_ins.kind is CursorKind.CALL_EXPR:
                        #     self.var_set.add(f"函数调用：{ast_ins.spelling} line {ast_ins.location[0]}<br><br>")
                        if ast_ins.kind in cursor_kind_ignore_set:
                            pass
                        else:
                            self.var_set.add(
                                f"{cursor_kind_dict.get(ast_ins.kind)}：{ast_ins.spelling} line {ast_ins.location[0]}<br><br>")
                        print(
                            f"{cursor_kind_dict.get(ast_ins.kind)}：{ast_ins.spelling} line {ast_ins.location[0]}<br><br>")

            if len(ast_ins.children) != 0:
                has_child = True
            if not has_child:
                break
            else:
                for child in ast_ins.children:
                    self.analyze_ast(child, file)
                break


def handle_non_match(string: str) -> str:
    safe = html.escape(string)
    return safe.replace('\n', '<br>')


def handle_match(match: re.Match) -> str:
    return f'<span style="color: {QColor("red").name()};">{html.escape(match.group())}</span>'
