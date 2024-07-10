from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QDialogButtonBox


class QueryThreatDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("查询")

        layout = QFormLayout(self)
        self.threat_input = QLineEdit(self)

        layout.addRow("风险函数：", self.threat_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)  # 连接“确定”按钮到accept方法
        buttons.rejected.connect(self.reject)  # 连接“取消”按钮到reject方法
        layout.addRow(buttons)

    def get_data(self):
        return self.threat_input.text()
