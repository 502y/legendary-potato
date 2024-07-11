from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QComboBox

from client.model.threat_model import ThreatModel


class EditThreatDialog(QDialog):
    def __init__(self, parent=None, threat=None):
        super().__init__(parent)
        self.setWindowTitle("修改")

        layout = QFormLayout(self)
        self.threat_input = QLineEdit(self)
        self.level_input = QComboBox(self)
        self.level_input.addItems(["高", "中", "低", "警告", "提示"])
        self.description_input = QLineEdit(self)

        layout.addRow("风险函数：", self.threat_input)
        layout.addRow("威胁等级：", self.level_input)
        layout.addRow("描述：", self.description_input)

        # 根据 index 加载数据
        data = parent.db.query_by_threat(threat)
        self.threat_input.setText(data[0][0])
        self.level_input.setEditText(ThreatModel.number_to_text(data[0][1]))
        self.description_input.setText(data[0][2])

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)  # 连接“确定”按钮到accept方法
        buttons.rejected.connect(self.reject)  # 连接“取消”按钮到reject方法
        layout.addRow(buttons)

    def get_data(self):
        return self.threat_input.text(), ThreatModel.text_to_number(
            self.level_input.currentText()), self.description_input.text()
