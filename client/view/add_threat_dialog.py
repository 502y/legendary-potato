from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QComboBox

from client.model.threat_model import ThreatModel


class AddThreatDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加")

        layout = QFormLayout(self)
        self.threat_input = QLineEdit(self)
        self.level_input = QComboBox(self)
        self.level_input.addItems(["高", "中", "低", "警告", "提示"])
        self.description_input = QLineEdit(self)

        layout.addRow("风险函数：", self.threat_input)
        layout.addRow("威胁等级：", self.level_input)
        layout.addRow("描述：", self.description_input)

        # 添加按钮盒，包含“确定”和“取消”按钮
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)  # 连接“确定”按钮到accept方法
        buttons.rejected.connect(self.reject)  # 连接“取消”按钮到reject方法
        layout.addRow(buttons)

    def get_data(self):
        return (
            self.threat_input.text(), ThreatModel.text_to_number(self.level_input.currentText()),
            self.description_input.text())
