from PyQt5.QtGui import QStandardItem
from PyQt5.QtWidgets import QDialog, QMessageBox

from client.model.threat_model import ThreatModel
from client.view.add_threat_dialog import AddThreatDialog
from client.view.database_editor_view import DatabaseEditorView
from client.view.edit_threat_dialog import EditThreatDialog
from client.view.query_threat_dialog import QueryThreatDialog
from utils.database.database_util import Database


class DatabaseEditor(DatabaseEditorView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.db = Database()

        self.add_button.clicked.connect(self.add_data)
        self.del_button.clicked.connect(self.delete_data)
        self.edit_button.clicked.connect(self.edit_data)
        self.query_button.clicked.connect(self.query_data)

        # 初始加载数据
        self.build_table(self.db.get_all_threat())

    def add_data(self):
        dialog = AddThreatDialog(self)

        if dialog.exec_() == QDialog.Accepted:
            threat, level, description = dialog.get_data()
            self.db.insert_threat(description, level, threat)
            self.build_table(self.db.get_all_threat())

    def delete_data(self):
        indexes = self.table_view.selectedIndexes()
        reply = QMessageBox.question(self, '提示', '确定要删除数据吗？', QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        if indexes:
            for index in indexes:
                row = index.row()
                selected = index.model().index(row, 0)
                threat = selected.data()
                self.db.delete_threat_by_name(threat)
            self.build_table(self.db.get_all_threat())

    def edit_data(self):
        index = self.table_view.selectedIndexes()
        row = index[0].row()
        selected = index[0].model().index(row, 0)
        if selected:
            threat = selected.data()
            dialog = EditThreatDialog(self, threat)
            if dialog.exec_() == QDialog.Accepted:
                new_threat, level, description = dialog.get_data()
                self.db.update_threat(threat, new_threat, description, level)
                self.build_table(self.db.get_all_threat())

    def query_data(self):
        dialog = QueryThreatDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            threat = dialog.get_data()
            if not threat == "":
                self.build_table(self.db.query_by_threat(threat))
            else:
                self.build_table(self.db.get_all_threat())

    def closeEvent(self, event):
        self.db.close()
        event.accept()

    def build_table(self, data):
        self.model.clear()
        self.model.setHorizontalHeaderLabels(['风险函数', '威胁等级', '描述'])
        for row, item in enumerate(data):
            for col, value in enumerate(item):
                if col == 1:
                    value = ThreatModel.number_to_text(value)
                self.model.setItem(row, col, QStandardItem(str(value)))
