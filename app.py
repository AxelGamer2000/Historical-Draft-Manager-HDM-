import sys
import json
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PySide6.QtGui import QPixmap
from player_case import PlayerCase, PlayerCaseTransfer
from player_trash import PlayerTrash
from urllib.request import urlretrieve
from pathlib import Path
from typing import Literal

tabs_content = ["⚔️ Attacking Trios", "🛡️ Defenders Pairs", "💼 Reserve", "🧍 Add Player", "🔎 Search"]

from his_ui import Ui_MainWindow


class HockeyDraftApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()

        self.setupUi(self)
        self.setWindowTitle("Historical Draft Manager")

        self.cases_list: list[PlayerCase] = self.findChildren(PlayerCase)
        self.cases_link_table = {
            "forwards": {
                1: {"lw": self.forward_case_trio1_lw, "c": self.forward_case_trio1_c, "rw": self.forward_case_trio1_rw},
                2: {"lw": self.forward_case_trio2_lw, "c": self.forward_case_trio2_c, "rw": self.forward_case_trio2_rw},
                3: {"lw": self.forward_case_trio3_lw, "c": self.forward_case_trio3_c, "rw": self.forward_case_trio3_rw},
                4: {"lw": self.forward_case_trio4_lw, "c": self.forward_case_trio4_c, "rw": self.forward_case_trio4_rw},
            },
            "defenders": {
                1: {"ld": self.defender_case_pair1_ld, "rd": self.defender_case_pair1_rd},
                2: {"ld": self.defender_case_pair2_ld, "rd": self.defender_case_pair2_rd},
                3: {"ld": self.defender_case_pair3_ld, "rd": self.defender_case_pair3_rd},
            },
            "goalies": {
                "starter": self.goalkeeper_case_starter,
                "backup": self.goalkeeper_case_backup
            },
            "reserve": {
                "lw": {1: self.reserve_case_lw_1, 2: self.reserve_case_lw_2},
                "rw": {1: self.reserve_case_rw_1, 2: self.reserve_case_rw_2},
                "c": {1: self.reserve_case_c_1, 2: self.reserve_case_c_2},
                "ld": {1: self.reserve_case_ld_1, 2: self.reserve_case_ld_2},
                "rd": {1: self.reserve_case_rd_1, 2: self.reserve_case_rd_2},
                "g": {1: self.reserve_case_g_1, 2: self.reserve_case_g_2},
            }
        }
        self.robot_role = "🧑‍💻 Draft Logger"
        self.user_role = "🧑‍💼 GM"
        self.message_state = 0
        self.message_cache: dict[str, str] = {
            "player_name": "",
            "former_team": "",
            "season": "",
            "type": "",
            "image_path": "",
            "position": "",
            "role": "",
        }
        self.image_dir = Path("images/")
        self.image_dir.mkdir(exist_ok=True)
        self.save_dir = Path("saves/")
        self.save_dir.mkdir(exist_ok=True)
        self.reset_command = "!reset"
        self.action_state = "default"
        self.crt_case: PlayerCase = None

        for case in self.cases_list:
            case: PlayerCase
            case.start_config()
            case.transfer_function = self.transfer_player
            case.change_role_trigger_function = self.change_role_trigger
            case.case_clicked_event_function = self.case_clicked_event

        for trash in self.findChildren(PlayerTrash):
            trash: PlayerTrash
            trash.clear_all_cases_function = self.clear_all_cases

        self.message_input.returnPressed.connect(self.send_message)
        self.action_clear.triggered.connect(self.clear_all_cases)
        self.action_report.triggered.connect(self.report_trigger)

    def clear_message_cache(self):
        for key in self.message_cache.keys():
            self.message_cache[key] = ""

    def verify_image_existed(self, player_name):
        for file in self.image_dir.iterdir():
            if file.is_file() and file.stem == player_name:
                return file

        return None

    def add_player(self, player_name: str, season: str, image: QPixmap, player_type: str, position: Literal["roster", "reserve"], role: str, former_team: str, image_path: str):
        if position == "roster":
            if player_type == "goalie":
                selected_case: PlayerCase = self.cases_link_table["goalies"][role]

                if selected_case.empty:
                    selected_case.player_name_label.setText(player_name)
                    selected_case.season_label.setText(season)
                    selected_case.image_label.setPixmap(image)
                    selected_case.empty = False
                    selected_case.former_team = former_team
                    selected_case.image_path = image_path
                    return True
            else:
                location = role.split(",")
                selected_case: PlayerCase = self.cases_link_table["forwards"][int(location[0].strip().replace("e", ""))][location[1].strip()] \
                    if player_type == "forward" else self.cases_link_table["defenders"][int(location[0].strip().replace("e", ""))][location[1].strip()]

                if selected_case.empty:
                    selected_case.player_name_label.setText(player_name)
                    selected_case.season_label.setText(season)
                    selected_case.image_label.setPixmap(image)
                    selected_case.empty = False
                    selected_case.former_team = former_team
                    selected_case.image_path = image_path
                    return True
        elif position == "reserve":
            selected_case: PlayerCase = self.cases_link_table["reserve"][role][1]

            if selected_case.empty:
                selected_case.player_name_label.setText(player_name)
                selected_case.season_label.setText(season)
                selected_case.image_label.setPixmap(image)
                selected_case.empty = False
                selected_case.former_team = former_team
                selected_case.image_path = image_path
                return True
            elif self.cases_link_table["reserve"][role][2].empty:
                second_case: PlayerCase = self.cases_link_table["reserve"][role][2]
                second_case.player_name_label.setText(player_name)
                second_case.season_label.setText(season)
                second_case.image_label.setPixmap(image)
                second_case.empty = False
                second_case.former_team = former_team
                second_case.image_path = image_path
                return True

        return False

    def transfer_player(self, case_from: PlayerCase, case_to: PlayerCase):
        transfer_from = PlayerCaseTransfer.from_player_case(case_from)
        transfer_to = PlayerCaseTransfer.from_player_case(case_to)

        case_to.receive_transfer(transfer_from)
        case_from.receive_transfer(transfer_to)

    def clear_all_cases(self):
        for case in self.cases_list:
            case.clear()

    def add_player_with_message_cache(self, message_cache: dict[str, str]):
        return self.add_player(message_cache["player_name"], message_cache["season"],
                        QPixmap(message_cache["image_path"]), self.message_cache["type"], self.message_cache["position"], self.message_cache["role"], self.message_cache["former_team"], self.message_cache["image_path"])

    def append_chat_message(self, role: str, message: str):
        self.chat_widget.appendPlainText(f"\n({role}) {message}")

    def reset_with_if(self, message: str, command: str):
        if message == command:
            self.message_state = -1
            self.clear_message_cache()
            self.chat_widget.appendPlainText("\n\n")
            self.append_chat_message(self.robot_role, "To begin, I'll need the name of the player you'd like, please. 🙂")

    def commands(self, message_input_text: str):
        if "!save" in message_input_text:
            arg = message_input_text.replace("!save ", "") + ".json"
            path = Path("saves/") / arg
            save_content = {}

            for case in self.cases_list:
                save_content[case.objectName()] = {
                    "player_name": case.player_name_label.text(),
                    "former_team": case.former_team,
                    "season": case.season_label.text(),
                    "empty": case.empty,
                    "image_path": case.image_path
                }

            path.write_text(json.dumps(save_content, indent=4, default=str), encoding="utf-8")

            self.message_state = -1
            self.clear_message_cache()
            self.chat_widget.appendPlainText("\n\n")
            self.append_chat_message(self.robot_role, "To begin, I'll need the name of the player you'd like, please. 🙂")
        elif "!load" in message_input_text:
            arg = message_input_text.replace("!load ", "") + ".json"
            path = Path("saves/") / arg
            save_content_raw = path.read_text(encoding="utf-8")
            save_content: dict = json.loads(save_content_raw)

            for key in save_content.keys():
                case: PlayerCase = self.findChild(PlayerCase, name=key)

                case.player_name_label.setText(save_content[key]["player_name"])
                case.season_label.setText(save_content[key]["season"])
                case.empty = save_content[key]["empty"]
                case.former_team = save_content[key]["former_team"]
                case.image_path = save_content[key]["image_path"]
                case.image_label.setPixmap(QPixmap(save_content[key]["image_path"]))

            self.message_state = -1
            self.clear_message_cache()
            self.chat_widget.appendPlainText("\n\n")
            self.append_chat_message(self.robot_role, "To begin, I'll need the name of the player you'd like, please. 🙂")


    def send_message(self):
        message = self.message_input.text()
        self.message_input.setText("")

        self.commands(message)
        self.reset_with_if(message, self.reset_command)

        if self.message_state == 0:
            self.append_chat_message(self.user_role, message)
            self.append_chat_message(self.robot_role, f"Okay perfect 😁! What season would you like to see for {message} and what team was he on before? 🧐")

            already_image_path = self.verify_image_existed(
                message.strip().lower().replace(" ", "_"))

            if already_image_path is not None:
                self.message_cache["image_path"] = already_image_path

            self.message_cache["player_name"] = message.strip()
            self.message_state += 1
        elif self.message_state == 1:
            responses = message.strip().split(",")

            self.append_chat_message(self.user_role, message)
            self.append_chat_message(self.robot_role, f"From {responses[1].strip()}, the season {responses[0].strip()} will be for {self.message_cache["player_name"]}. Is he a forward, a defender, or a goalie? 🤔")

            self.message_cache["season"] = responses[0].strip()
            self.message_cache["former_team"] = responses[1].strip()
            self.message_state += 1
        elif self.message_state == 2:
            self.append_chat_message(self.user_role, message)
            self.append_chat_message(self.robot_role,f"The {self.message_cache["former_team"]} {message} {self.message_cache["player_name"]} from season {self.message_cache["season"]} has been added to the historical draft database. 👌 \n"
                                                     f"{"You need an image for the player; I'll need the image link. 😁" if self.message_cache["image_path"] == "" else "(You can skip this by sending anything)"}")

            self.message_cache["type"] = message
            self.message_state += 1
        elif self.message_state == 3:
            if self.message_cache["image_path"] == "":
                self.message_cache["image_path"] = f"images/{self.message_cache["player_name"].strip().lower().replace(" ", "_")}.jpg"
                urlretrieve(message, self.message_cache["image_path"])

            self.message_state += 1

            self.append_chat_message(self.user_role, message)
            self.append_chat_message(self.robot_role, "Do you want to put him on the roster or in the reserve? 🤔")
        elif self.message_state == 4:
            self.message_cache["position"] = message
            self.message_state += 1

            self.append_chat_message(self.user_role, message)

            if self.message_cache["position"] == "roster":
                if self.message_cache["type"] == "forward":
                    self.append_chat_message(self.robot_role, "Which trio should he be on (1st, 2nd, 3rd, 4th (only marks the number)) and what would his role be between lw, c, and rw? 🙂")
                elif self.message_cache["type"] == "defender":
                    self.append_chat_message(self.robot_role, "Which pair should he be on (1st, 2nd, 3rd (only marks the number)) and what would its role be between ld and rd? 🙂")
                elif self.message_cache["type"] == "goalie":
                    self.append_chat_message(self.robot_role, "Is he a starting goalie (starter) or a backup goalie (backup)? 🙂")
            elif self.message_cache["position"] == "reserve":
                if self.message_cache["type"] == "forward":
                    self.append_chat_message(self.robot_role, "Which role between lw, c, and rw? 🙂")
                elif self.message_cache["type"] == "defender":
                    self.append_chat_message(self.robot_role, "Which role between ld and rd? 🙂")
                elif self.message_cache["type"] == "goalie":
                    self.message_state = 0
                    self.message_cache["role"] = "g"

                    if self.add_player_with_message_cache(self.message_cache):
                        self.chat_widget.appendPlainText("\n\n")
                        self.clear_message_cache()
                        self.append_chat_message(self.robot_role, "To begin, I'll need the name of the player you'd like, please. 🙂")
                    else:
                        self.message_state = -2
        elif self.message_state == 5:
            self.message_state = 0
            self.message_cache["role"] = message

            if self.add_player_with_message_cache(self.message_cache):
                self.chat_widget.appendPlainText("\n\n")
                self.clear_message_cache()
                self.append_chat_message(self.robot_role, "To begin, I'll need the name of the player you'd like, please. 🙂")
            else:
                self.message_state = -2
        else:
            if self.message_state == -2:
                self.append_chat_message(self.robot_role, "This place is already taken. 🫤\n(You can skip this by sending anything)")
                self.message_state = 3
            else:
                self.message_state = 0

    def change_role_trigger(self, crt_case: PlayerCase):
        QMessageBox.information(self, "Change role to this player", "You can click on a another empty case for this action.")
        self.crt_case = crt_case
        self.action_state = "change_role"

    def report_trigger(self):
        QMessageBox.information(self, "Report a player",
                                "You can click on a another player case for this action.")
        self.action_state = "report"

    def case_clicked_event(self, to_case: PlayerCase):
        if self.action_state == "change_role":
            if not self.crt_case.empty and to_case.empty:
                self.transfer_player(self.crt_case, to_case)
                self.action_state = "default"
                self.crt_case = None
            else:
                self.action_state = "default"
                self.crt_case = None
        elif self.action_state == "report":
            if not to_case.empty:
                to_case.report_player()
                self.action_state = "default"
                self.crt_case = None
            else:
                self.action_state = "default"
                self.crt_case = None

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = HockeyDraftApp()
    window.show()

    sys.exit(app.exec())