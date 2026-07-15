from typing import Callable
from PySide6.QtWidgets import QFrame, QLabel, QMenu, QMessageBox, QInputDialog
from PySide6.QtCore import Qt, QMimeData
from PySide6.QtGui import QDrag, QPixmap, QAction, QGuiApplication

class PlayerCase(QFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.setAcceptDrops(True)

        self.player_name_label: QLabel = None
        self.season_label: QLabel = None
        self.image_label: QLabel = None
        self.former_team = ""
        self.empty = True

        self.transfer_function: Callable[[PlayerCase, PlayerCase], None] = print
        self.change_role_trigger_function: Callable[[PlayerCase], None] = print
        self.case_clicked_event_function: Callable[[PlayerCase], None] = print

    def start_config(self):
        for label in self.findChildren(QLabel):
            label: QLabel

            name = label.objectName()

            if "player_name" in name:
                self.player_name_label: QLabel = label
            elif "season" in name:
                self.season_label: QLabel = label
            elif "image" in name:
                self.image_label: QLabel = label

        self.player_name_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.season_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.image_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

    def receive_transfer(self, transfer:PlayerCaseTransfer):
        self.player_name_label.setText(transfer.player_name)
        self.season_label.setText(transfer.season)
        self.image_label.setPixmap(transfer.image)
        self.empty = transfer.empty
        self.former_team = transfer.former_team

    def clear(self):
        self.empty = True
        self.player_name_label.setText("")
        self.season_label.setText("")
        self.image_label.setPixmap(QPixmap())

    def show_former_team_dialog(self):
        window = self.window()

        QMessageBox.information(window, "", self.former_team)
        print(f"Former Team: {self.former_team}")

    def report_player(self):
        reason, ok = QInputDialog.getMultiLineText(
            self.window(),
            "Report",
            f"Why you chose {self.player_name_label.text()}?"
        )

        if ok:
            report = \
                f"""
            Drafting Player Report:

            Player -> {self.player_name_label.text()}
            Former Team -> {self.former_team}
            Season -> {self.season_label.text()}
            
            Reason -> {reason}
            """

            print(report)
            QGuiApplication.clipboard().setText(report)


    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            drag.setMimeData(mime)
            drag.exec(Qt.DropAction.MoveAction)

    def dragEnterEvent(self, event, /):
        source = event.source()
        if isinstance(source, PlayerCase):
            if not source.empty:
                event.accept()

    def dropEvent(self, event, /):
        source = event.source()

        if isinstance(source, PlayerCase):
            self.transfer_function(source, self)
            event.accept()

    def mousePressEvent(self, event, /):
        self.case_clicked_event_function(self)

    def contextMenuEvent(self, event, /):
        if not self.empty:
            menu = QMenu(self)

            former_team_action = QAction("Former Team", self)
            change_role_action = QAction("Change Role", self)

            change_role_action.triggered.connect(lambda x: self.change_role_trigger_function(self))
            former_team_action.triggered.connect(self.show_former_team_dialog)

            menu.addAction(former_team_action)
            menu.addAction(change_role_action)

            menu.exec(event.globalPos())


class PlayerCaseTransfer:
    def __init__(self, player_name: str, season: str, image: QPixmap, empty: bool, former_team: str):
        self.player_name = player_name
        self.season = season
        self.image = image
        self.empty = empty
        self.former_team = former_team

    @staticmethod
    def from_player_case(player_case:PlayerCase):
        return PlayerCaseTransfer(player_case.player_name_label.text(), player_case.season_label.text(), player_case.image_label.pixmap(), player_case.empty, player_case.former_team)
