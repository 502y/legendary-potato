import html
import json
import os
import re

from PyQt5.QtCore import QModelIndex
from PyQt5.QtGui import QColor, QTextCursor
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QMessageBox
from ordered_set import OrderedSet

from client.controller.database_view_controller import DatabaseEditor
from client.model.LLVMGeneratedModel import cursor_kind_dict
from client.view.custom_treeview import CustomFileSystemModel
from client.view.main_view import MainWindowView
from funcTrace.AstTreeJson import AST_Tree_json
from utils.cmd_utils import compile_and_run
from utils.file_utils import extract_custom_headers_and_sources
from utils.str_utils import is_empty_or_whitespace, search_in_str


class MainWindowViewController(QMainWindow, MainWindowView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.var_set = OrderedSet([])
        self.entry_point = ""
        self.info_text = ""

        self.setup_ui(self)

        self.openFile.triggered.connect(self.open_File)
        self.exportReport.triggered.connect(self.export_report)
        self.exit.triggered.connect(self.try_exit)
        self.operate_database.triggered.connect(self.show_database_window)
        self.compile.triggered.connect(self.compile_and_run)

        self.treeView.doubleClicked.connect(self.get_selected_file_from_tree)
        self.search_button.clicked.connect(self.do_search)
        self.sourceBroswer.selectionChanged.connect(self.select_in_source)

        self.riskBrowser.selectionChanged.connect(self.select_in_risk)
        # self.riskBrowser.installEventFilter(self.riskBrowser)

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
            self.statusbar.showMessage(f"文件：{item}")
            self.riskBrowser.setText("")
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
        use_reg = self.regex_checkbox.isChecked()
        self.do_search_with_text(content, use_reg)

    def do_search_with_text(self, content, use_reg):
        if is_empty_or_whitespace(content):
            self.sourceBroswer.setText(
                f'<pre><code style="white-space: pre-wrap; font-family: inherit;">{html.escape(self.sourceBroswer.toPlainText())}</code></pre>')
            return

        source_code = self.sourceBroswer.toPlainText()
        if is_empty_or_whitespace(source_code):
            return

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

    def select_in_source(self):
        selection = self.sourceBroswer.textCursor().selectedText()
        if is_empty_or_whitespace(selection):
            return

        pattern = r'\b' + selection + r'\b'
        text = ""
        for item in self.var_set:
            if bool(re.search(pattern, item)):
                text += item
        self.riskBrowser.setText(text)
        print(selection)

    def select_in_risk(self):
        cursor = self.riskBrowser.textCursor()

        # 获取选中文本的开始位置
        start_pos = cursor.selectionStart()

        # 移动光标到行的开始
        cursor.setPosition(start_pos)
        cursor.movePosition(cursor.StartOfLine)

        # 获取选中文本所在行的结束位置（即下一行的开始位置）
        cursor.movePosition(cursor.EndOfLine, cursor.KeepAnchor)

        # 获取整行的文本
        full_line_text = cursor.selectedText()
        pattern = r'\d+'
        match = re.findall(pattern, full_line_text)
        if match:
            var = re.search(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\b(?=\s+line)", full_line_text)
            if var:
                var_pattern = r"\b" + var.group(1) + r"\b"
                self.do_search_with_text(var_pattern, True)
            self.scroll_to_line(int(match[-1]))
        else:
            return

    def scroll_to_line(self, line):
        doc = self.sourceBroswer.document()
        block = doc.findBlockByNumber(line - 1)

        print(f"Block position: {block.position()}, Block number: {block.blockNumber()}")  # 调试输出
        if not block.isValid():  # 检查块是否有效
            print("Block is not valid.")
            return

        cursor = QTextCursor(self.sourceBroswer.textCursor())
        cursor.setPosition(block.position(), QTextCursor.MoveAnchor)
        self.sourceBroswer.setTextCursor(cursor)
        self.sourceBroswer.ensureCursorVisible()

    def generate_ast(self, path):
        ast_obj = AST_Tree_json(path)
        json_ = ast_obj.start()
        data = json.loads(json_)
        try:
            # self.ast_instance = LLVMGeneratedModel.from_dict(data)
            self.ast_instance = ast_obj.get_AST_Root()
        except Exception as e:
            print(e)

    def analyze_ast(self, ast_ins, file):
        while True:
            has_child = False
            if ast_ins and hasattr(ast_ins.extent.start, "file") and ast_ins.extent.start.file is not None:
                if ast_ins.extent.start.file.name == file and ast_ins.spelling != file:
                    if str(ast_ins.kind) in cursor_kind_dict:
                        if ast_ins and ast_ins.kind is not None and ast_ins.location is not None:
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
                            # elif str(ast_ins.kind) in cursor_kind_ignore_set:
                            #     pass

                            self.var_set.add(
                                f"{cursor_kind_dict.get(str(ast_ins.kind))}：{ast_ins.spelling} line {ast_ins.location.line}<br><br>")

            for child in ast_ins.get_children():
                has_child = True
                break
            if not has_child:
                break
            else:
                for child in ast_ins.get_children():
                    self.analyze_ast(child, file)
                break


def handle_non_match(string: str) -> str:
    safe = html.escape(string)
    return safe  # .replace('\n', '<br>')


def handle_match(match: re.Match) -> str:
    return f'<span style="color: {QColor("red").name()};">{html.escape(match.group())}</span>'
