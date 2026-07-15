from PySide6.QtWidgets import QFrame
from player_case import PlayerCase
from PySide6.QtCore import Qt

class PlayerTrash(QFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.setAcceptDrops(True)
        self.clear_all_cases_function = print

    def mouseDoubleClickEvent(self, event, /):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.clear_all_cases_function()

    def dragEnterEvent(self, event, /):
        source = event.source()
        if isinstance(source, PlayerCase):
            if not source.empty:
                event.accept()

    def dropEvent(self, event, /):
        source = event.source()

        if isinstance(source, PlayerCase):
            source.clear()
            event.accept()