import html
import json
import os
import re

from PyQt5.QtCore import QModelIndex
from PyQt5.QtGui import QColor, QTextCursor
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QMessageBox, QAction
from ordered_set import OrderedSet

from client.controller.database_view_controller import DatabaseEditor
from client.model.LLVMGeneratedModel import cursor_kind_dict, cursor_kind_ignore_set
from client.model.recent_file_model import recent_file_from_dict, RecentProjectElement, recent_file_to_dict
from client.view.custom_treeview import CustomFileSystemModel
from client.view.main_view import MainWindowView
from funcTrace.AstTreeJson import AST_Tree_json
from utils.cmd_utils import compile_and_run
from utils.file_utils import extract_custom_headers_and_sources, export_report_to_txt, export_report_to_doc
from utils.str_utils import is_empty_or_whitespace, search_in_str

count = 0


class MainWindowViewController(QMainWindow, MainWindowView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.var_set = OrderedSet([])
        self.entry_point = ""
        self.info_text = ""

        self.setup_ui(self)

        self.openFile.triggered.connect(self.select_file_and_open)
        self.exportReport.triggered.connect(self.export_report)
        self.exit.triggered.connect(self.try_exit)
        self.operate_database.triggered.connect(self.show_database_window)
        self.compile.triggered.connect(self.compile_and_run)

        self.treeView.doubleClicked.connect(self.get_selected_file_from_tree)
        self.search_button.clicked.connect(self.do_search)
        self.sourceBrowser.selectionChanged.connect(self.select_in_source)

        self.riskBrowser.selectionChanged.connect(self.select_in_risk)
        self.varBrowser.selectionChanged.connect(self.select_in_var)

        self.load_recent_file(self.recentFile)

    def load_recent_file(self, menu):
        encrypted_file = os.path.join(os.getcwd(), "recent_file.json")
        with open(encrypted_file, "r") as enc_file:
            recent_file_json_set = json.loads(enc_file.read())
            self.recent_file_dict = recent_file_from_dict(recent_file_json_set)
            for line in self.recent_file_dict:
                action = QAction(line.project_name, self)
                action.triggered.connect(lambda checked, p=line.project_path: self.open_File(p))
                menu.addAction(action)

    def select_file_and_open(self):
        dialog = QFileDialog()
        dialog.setNameFilter("C源文件(*.c)")
        dialog.setViewMode(QFileDialog.Detail)

        if dialog.exec_():
            selected_file = dialog.selectedFiles()[0]
            # 判断是否包含C入口
            if selected_file:
                with open(selected_file, "r") as file:
                    content = file.read()

                pattern = r"\b(int|void)\b\s+main\s*\(\s*(?:int\s+argc,\s*(?:char\s*\*\s*){1,2}argv\[\])?\s*\)\s*\{.*\}"
                if len(re.findall(pattern, content)):
                    QMessageBox.information(self, "警告", "请选择包含main函数的C源文件", QMessageBox.Yes)
                    return

                self.open_File(selected_file)

            else:
                self.statusbar.showMessage("选择的文件无效")
                return

    def open_File(self, path):
        try:
            self.entry_point = path

            self.insert_into_recent(path)

            # 包含头文件、源文件分析
            self.custom_headers, self.custom_sources = extract_custom_headers_and_sources(path)
            paths = [os.path.abspath(header) for header in self.custom_headers] + [os.path.abspath(source) for source in
                                                                                   self.custom_sources]
            if len(paths) == 0:
                paths.append(path)

            if len(self.custom_sources) ==0:
                self.custom_sources.add(path)

            self.common_prefix = os.path.commonpath(paths)

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

            self.show_source_code(path)
        except Exception as e:
            self.showError(e)

    def insert_into_recent(self, path):
        exist = False
        for instance in self.recent_file_dict:
            if instance.project_path == path:
                exist = True
                break
        if not exist:
            new_ins = RecentProjectElement(name=path, path=path)
            self.recent_file_dict.append(new_ins)

            with open(os.path.join(os.getcwd(), "recent_file.json"), "w") as enc_file:
                json.dump(recent_file_to_dict(self.recent_file_dict), enc_file)
            self.load_recent_file(self.recentFile)

    def get_selected_file_from_tree(self, index: QModelIndex):
        if index.isValid():
            item = self.model.filePath(index)
            if os.path.isdir(item) or item.endswith(".pyc"):
                return
            if not item.endswith(".c") and not item.endswith(".h"):
                QMessageBox.information(self, "警告", "您选择的不是C源文件或C头文件，程序可能无法正常工作",
                                        QMessageBox.Yes)
            self.statusbar.showMessage(f"文件：{item}")
            self.riskBrowser.setText("")
            self.show_source_code(item)

    def show_source_code(self, path):
        try:
            with open(path, "r") as file_:
                content = file_.read()
                self.sourceBrowser.setText(
                    f'<pre><code style="white-space: pre-wrap; font-family: inherit;">{html.escape(content)}</code></pre>')
        except Exception as e:
            self.sourceBrowser.setText(f"无法打开文件{path}")
        finally:
            self.var_set = OrderedSet([])
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
            self.sourceBrowser.setText(
                f'<pre><code style="white-space: pre-wrap; font-family: inherit;">{html.escape(self.sourceBrowser.toPlainText())}</code></pre>')
            return

        source_code = self.sourceBrowser.toPlainText()
        if is_empty_or_whitespace(source_code):
            return

        try:
            color_text = search_in_str(source_code, content, use_reg, on_match=handle_match,
                                       on_non_match=handle_non_match)
        except Exception as e:
            self.showError(e)
            return
        color_text = f'<pre><code style="white-space: pre-wrap; font-family: inherit;">{color_text}</code></pre>'

        self.sourceBrowser.setText(color_text)

    def export_report(self):
        if is_empty_or_whitespace(self.entry_point):
            self.showError("请先选择程序")
            return
        file_name, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "",
                                                   "文本文档(*.txt);;Microsoft Word 文档 (*.docx)")
        if not file_name:
            return


        try:
            if file_name.endswith(".txt"):
                export_report_to_txt(file_name, self.custom_sources)
            if file_name.endswith(".docx"):
                export_report_to_doc(file_name, self.custom_sources)
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
        selection = self.sourceBrowser.textCursor().selectedText()
        if is_empty_or_whitespace(selection):
            return

        pattern = r'\b' + selection + r'\b'
        text = ""
        for item in self.var_set:
            if bool(re.search(pattern, item)):
                text += item
        self.riskBrowser.setText(text)

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

    def select_in_var(self):
        cursor = self.varBrowser.textCursor()

        # 获取选中文本的开始位置
        start_pos = cursor.selectionStart()

        # 移动光标到行的开始
        cursor.setPosition(start_pos)
        cursor.movePosition(cursor.StartOfLine)

        # 获取选中文本所在行的结束位置
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
        # 获取格式文档
        doc = self.sourceBrowser.document()
        # 获取行号对应内容
        block = doc.findBlockByNumber(line - 1)

        # 创建游标并滚动到行号
        cursor = QTextCursor(self.sourceBrowser.textCursor())
        cursor.setPosition(block.position(), QTextCursor.MoveAnchor)
        self.sourceBrowser.setTextCursor(cursor)
        self.sourceBrowser.ensureCursorVisible()

    def generate_ast(self, path):
        ast_obj = AST_Tree_json(path)
        try:
            self.ast_instance = ast_obj.get_AST_Root(path)
        except Exception as e:
            print(e)

    def analyze_ast(self, ast_ins, file):
        while True:
            # AST对象存在、能够获取其文件路径
            if ast_ins and hasattr(ast_ins.extent.start, "file") and ast_ins.extent.start.file is not None:
                # 对象属于正在查看的文件且不为根对象
                if ast_ins.extent.start.file.name == file and ast_ins.spelling != file:
                    # 对象存在有效类型且无需忽略
                    if ast_ins.kind is not None and str(ast_ins.kind) not in cursor_kind_ignore_set:
                        # 对象存在行数且包含有效解析
                        if ast_ins.location is not None and not is_empty_or_whitespace(
                                ast_ins.spelling):
                            # 未命名的内容
                            if str(ast_ins.kind) not in cursor_kind_dict:
                                global count
                                count += 1
                                print(count)
                                print(f"{str(ast_ins.kind)}：{ast_ins.spelling} line {ast_ins.location.line}<br><br>")
                                self.var_set.add(
                                    f"{str(ast_ins.kind)}：{ast_ins.spelling} line {ast_ins.location.line}<br><br>")
                            # 命名内容
                            else:
                                self.var_set.add(
                                    f"{cursor_kind_dict.get(str(ast_ins.kind))}：{ast_ins.spelling} line {ast_ins.location.line}<br><br>")

            if not any(ast_ins.get_children()):
                break
            for child in ast_ins.get_children():
                self.analyze_ast(child, file)
            break


def handle_non_match(string: str) -> str:
    return html.escape(string)


def handle_match(match: re.Match) -> str:
    return f'<span style="color: {QColor("red").name()};">{html.escape(match.group())}</span>'
