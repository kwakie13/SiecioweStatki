from __future__ import unicode_literals

import sys

from PyQt5.Qt import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

nicks = ["Gracz 1", "Gracz 2", "Gracz 3"]
columns = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
buttons = {}
square_address = {}

local_player_grid = str()

for i in range(100):
    local_player_grid = local_player_grid + '0'

counter = 1

for i in range(10):
    for j in range(len(columns)):
        square_address[str("{}{}".format(columns[j], i + 1))] = counter
        counter = counter + 1


def indicate_player_label(self, label):  # function indicating player move (changing label background color)
    label.setStyleSheet("background-color: lightgreen; border: 1 solid black; border-radius: 15; padding: 5")

    return label


def reset_player_label(self, label):  # function resetting move indicator
    label.setStyleSheet("border: 1 solid black; border-radius: 15; padding: 5")

    return label


def player_grid(self, nick, saving, flat):
    group = QGroupBox()  # box for player's buttons
    grid = QGridLayout()  # creating grid to place buttons

    for i in range(len(columns)):
        label = QLabel()
        label.setText(columns[i])
        label.setAlignment(Qt.AlignCenter)

        grid.addWidget(label, 0, i + 1)

    for i in range(10):
        label = QLabel()
        label.setText(str(i + 1))
        label.setAlignment(Qt.AlignCenter)

        grid.addWidget(label, i + 1, 0)

    for j in range(10):  # for each row
        for k in range(len(columns)):  # for each column
            ID = (nick + "_" + columns[k] + str(j + 1))  # ID for a button

            button = QPushButton()
            button.setObjectName(ID)
            button.clicked.connect(self.whenClicked)  # connecting action to click

            if flat:
                button.setEnabled(False)

            button.setStyleSheet("background-color: #f0f0f0; border: 1 solid black")
            button.setFixedSize(20, 20)

            grid.addWidget(button, j + 1, k + 1)  # adding button to grid

            if saving:
                self.saveButton(button)  # saving button's name

    group.setLayout(grid)  # setting box's layout (previously created and filled grid)

    return group


def player_label(self, nick):
    groupBox = QGroupBox()
    groupBox.setStyleSheet("border : none")

    label = QLabel(nick)
    label.setObjectName("{0}_label".format(nick))
    self.saveButton(label)

    reset_player_label(self, label)  # indicating it's player move
    label.setFont(QFont('Calibri', 15))

    row = QHBoxLayout()
    row.addWidget(label, alignment=Qt.AlignCenter)

    groupBox.setLayout(row)

    return groupBox


def setting_ships_color_change(self, button):
    color = button.palette().button().color()

    if color.name() == "#f0f0f0":
        button.setStyleSheet("background-color: green; border: 1 solid black")
    else:
        button.setStyleSheet("background-color: #f0f0f0; border: 1 solid black")


def index_finder(self, button_name):
    name_len = len(button_name)
    for i in range(name_len - 1, -1, -1):
        if button_name[i] == "_":
            return square_address[button_name[i + 1:]]


def change_grid_string_value(self, index, grid, new_value):
    grid = grid[:index] + str(new_value) + grid[index + 1:]
    return grid


def neighbour_checker(self):
    for i in range(10):
        for j in range(10):
            index = i * 10 + j
            if i == 0:
                if j == 0:
                    if (local_player_grid[index] == '1' and local_player_grid[index + 1] == '1') and (local_player_grid[index] == '1' and local_player_grid[index + 10] == '1'):
                        return False

                if j == 9:
                    if (local_player_grid[index] == '1' and local_player_grid[index - 1] == '1') and (local_player_grid[index] == '1' and local_player_grid[index + 10] == '1'):
                        return False

                else:
                    if (local_player_grid[index] == '1' and local_player_grid[index + 10] == '1') and (local_player_grid[index + 1] == '1' or local_player_grid[index - 1] == '1'):
                        return False

            if i == 9:
                if j == 0:
                    if (local_player_grid[index] == '1' and local_player_grid[index + 1] == '1') and (local_player_grid[index] == '1' and local_player_grid[index - 10] == '1'):
                        return False

                if j == 9:
                    if (local_player_grid[index] == '1' and local_player_grid[index - 1] == '1') and (local_player_grid[index] == '1' and local_player_grid[index - 10] == '1'):
                        return False

                else:
                    if (local_player_grid[index] == '1' and local_player_grid[index - 10] == '1') and (local_player_grid[index + 1] == '1' or local_player_grid[index - 1] == '1'):
                        return False

            else:
                if j == 0:
                    if (local_player_grid[index] == '1' and local_player_grid[index + 1] == '1') and (local_player_grid[index + 10] == '1' or local_player_grid[index - 10] == '1'):
                        return False

                if j == 9:
                    if (local_player_grid[index] == '1' and local_player_grid[index - 1] == '1') and (local_player_grid[index + 10] == '1' or local_player_grid[index - 10] == '1'):
                        return False

                else:
                    if local_player_grid[index] == '1' and (local_player_grid[index + 1] == '1' or local_player_grid[index - 1] == '1') and (local_player_grid[index + 10] == '1' or local_player_grid[index - 10] == '1'):
                        return False
    return True


def duplicate_checker(self, list_of_values, value):
    for i in list_of_values:
        if i == value:
            return False

    return True


def ships_checker(self):
    indexes = []
    ships = []

    for i in range(10):
        for j in range(10):
            index = i * 10 + j

            if local_player_grid[index] == '1' and duplicate_checker(self, indexes, index):
                indexes.append(index)
                ship = [index]
                row_number = index // 10
                column_number = index % 10

                if index + 1 <= 99 and local_player_grid[index + 1] == '1' and duplicate_checker(self, indexes, index + 1) and (index + 1) // 10 == row_number:
                    indexes.append(index + 1)
                    ship.append(index + 1)

                    moving_index = index + 2

                    while local_player_grid[moving_index] == '1' and moving_index // 10 == row_number:
                        indexes.append(moving_index)
                        ship.append(moving_index)
                        moving_index = moving_index + 1

                elif index + 10 <= 99 and local_player_grid[index + 10] == '1' and duplicate_checker(self, indexes, index + 10) and (index + 10) % 10 == column_number:
                    indexes.append(index + 10)
                    ship.append(index + 10)

                    moving_index = index + 20

                    while local_player_grid[moving_index] == '1' and moving_index % 10 == column_number:
                        indexes.append(moving_index)
                        ship.append(moving_index)
                        moving_index = moving_index + 10

                ships.append(len(ship))

    ships.sort()

    if ships == [1, 1, 1, 1, 2, 2, 2, 3, 3, 4]:
        return True
    else:
        return False


class IntroScreen(QWidget):
    def __init__(self):
        super().__init__()

        self.interface()

        self.centerWindow()

        self.setWindowTitle("Statki")
        self.setWindowIcon(QIcon("ship.png"))

        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)  # blocking window maximizing
        self.setMaximumSize(self.size())  # prevent resizing

        self.show()

    def interface(self):
        rows = QVBoxLayout()

        groupBox = QGroupBox()
        nick_line = QHBoxLayout()

        text_line_label = QLabel("Podaj nick:", self)
        nick_line.addWidget(text_line_label)

        self.text_line = QLineEdit()
        nick_line.addWidget(self.text_line)

        groupBox.setLayout(nick_line)
        rows.addWidget(groupBox)

        grid = player_grid(self, "setting_ships", True, False)
        rows.addWidget(grid)

        proceed = QPushButton("Dalej", self)

        proceed.clicked.connect(self.nextWindow)
        rows.addWidget(proceed)

        self.setLayout(rows)

    def saveButton(self, obj):
        buttons[obj.objectName()] = obj

    def centerWindow(self):
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def nextWindow(self):
        self.user_nick = self.text_line.text()

        if self.text_line.text() == "":
            QMessageBox.critical(self, "Brak nicku", "Podaj nick!")
        elif not neighbour_checker(self):
            QMessageBox.critical(self, "Błąd ustawienia", "Statki nie mogą ze sobą sąsiadować!")
        elif not ships_checker(self):
            QMessageBox.critical(self, "Błąd ustawienia", "Twoje statki są nieprawidłowe! Sprawdź ich liczbę i wielkość.")
        else:
            self.w = GameScreen(self.user_nick)
            self.w.show()
            self.close()

    def whenClicked(self):
        sender = self.sender()
        setting_ships_color_change(self, sender)

        global local_player_grid
        if local_player_grid[index_finder(self, sender.objectName()) - 1] == '1':
            local_player_grid = change_grid_string_value(self, index_finder(self, sender.objectName()) - 1, local_player_grid, 0)
        else:
            local_player_grid = change_grid_string_value(self, index_finder(self, sender.objectName()) - 1, local_player_grid, 1)


class GameScreen(QWidget):
    def __init__(self, user_nick):
        super().__init__()

        self.interface(user_nick)

        self.centerWindow()

        self.setWindowTitle("Statki")
        self.setWindowIcon(QIcon("ship.png"))

        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)  # blocking window maximizing
        self.setMaximumSize(self.size())  # prevent resizing

        self.show()

    def interface(self, my_nick):
        table_scheme = QGridLayout()  # creating table layout for a window

        for i in range(len(nicks)):  # loop creating labels with indicators for opponents
            row = player_label(self, nicks[i])
            table_scheme.addWidget(row, 0, i)

        for i in range(len(nicks)):  # loop creating grids for opponents
            box = player_grid(self, nicks[i], True, False)
            table_scheme.addWidget(box, 1, i)

        box = player_grid(self, my_nick, True, True)
        table_scheme.addWidget(box, 2, 1)

        row = player_label(self, my_nick)
        table_scheme.addWidget(row, 3, 1)

        self.setLayout(table_scheme)

    def saveButton(self, obj):
        buttons[obj.objectName()] = obj

    def findButton(self, text):
        return buttons[text]

    def centerWindow(self):
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    # def closeEvent(self, event):  # are you sure to quit?
    #     odp = QMessageBox.question(
    #         self,
    #         "Wyjście",
    #         "Czy na pewno koniec?",
    #         QMessageBox.Yes | QMessageBox.No,
    #         QMessageBox.No,  # default option
    #     )
    #
    #     if odp == QMessageBox.Yes:
    #         event.accept()
    #     else:
    #         event.ignore()

    def keyPressEvent(self, e):  # exit with Escape button
        if e.key() == Qt.Key_Escape:
            self.close()

    def whenClicked(self):
        sender = self.sender()

        if isinstance(sender, QPushButton):
            pass
            # print(sender.objectName)


app = QApplication(sys.argv)  # creating app
window = IntroScreen()
window.text_line.setFocus()
sys.exit(app.exec_())  # starting the app
