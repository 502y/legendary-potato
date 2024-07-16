from PyQt5.QtCore import QRect
from PyQt5.QtGui import QPainter, QFontMetrics
from PyQt5.QtWidgets import QWidget


class NumberBar(QWidget):
    def __init__(self, editor):
        QWidget.__init__(self, editor)

        self.editor = editor
        self.editor.document().contentsChanged.connect(self.update_width_and_contents)

        self.current_line = -1
        self.update_width_and_contents()

    def update_width_and_contents(self):
        self.update_width()
        self.update_contents(QRect(), 0)

    def update_width(self):
        self.setFixedWidth(self.number_bar_width())

    def number_bar_width(self):
        metrics = QFontMetrics(self.font())
        return metrics.boundingRect(str(self.editor.document().lineCount())).width() + 5

    def paintEvent(self, event):
        painter = QPainter(self)
        metrics = QFontMetrics(self.font())
        block = self.editor.document().begin()
        scrollbar_value = self.editor.verticalScrollBar().value()
        while block.isValid():
            blockNumber = block.blockNumber()
            block_top = scrollbar_value + self.editor.blockBoundingGeometry(block).translated(
                self.editor.viewport().contentsMargins()).top()
            if block_top >= event.rect().bottom():
                break

            # Draw the line number right justified at the position of the line.
            painter.drawText(self.width() - metrics.boundingRect(str(blockNumber)).width() - 5,
                             int(block_top),
                             str(blockNumber))

            block = block.next()

        painter.end()

    def resizeEvent(self, event):
        cr = self.editor.viewport().contentsRect()
        self.move(cr.left(), cr.top())
        self.setFixedWidth(self.number_bar_width())

    def update_contents(self, rect, dy):
        if dy:
            self.scroll(0, dy)
        else:
            self.update(0, rect.y(), self.width(), rect.height())

        if rect.contains(self.editor.viewport().rect()):
            self.update_width()
