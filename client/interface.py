from __future__ import unicode_literals

import sys

from PyQt5.Qt import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtNetwork import *

import tcpconnector
import game
import protocol
import os

FILE_BLOCK_SIZE = 4096

game_data = game.Game()
tcp_manager = tcpconnector.TcpManager()

nicks = []
columns = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
buttons = {}
square_address = {}

local_player_grid = str('0') * 100

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

                elif j == 9:
                    if (local_player_grid[index] == '1' and local_player_grid[index - 1] == '1') and (local_player_grid[index] == '1' and local_player_grid[index + 10] == '1'):
                        return False

                else:
                    if (local_player_grid[index] == '1' and local_player_grid[index + 10] == '1') and (local_player_grid[index + 1] == '1' or local_player_grid[index - 1] == '1'):
                        return False

            elif i == 9:
                if j == 0:
                    if (local_player_grid[index] == '1' and local_player_grid[index + 1] == '1') and (local_player_grid[index] == '1' and local_player_grid[index - 10] == '1'):
                        return False

                elif j == 9:
                    if (local_player_grid[index] == '1' and local_player_grid[index - 1] == '1') and (local_player_grid[index] == '1' and local_player_grid[index - 10] == '1'):
                        return False

                else:
                    if (local_player_grid[index] == '1' and local_player_grid[index - 10] == '1') and (local_player_grid[index + 1] == '1' or local_player_grid[index - 1] == '1'):
                        return False

            else:
                if j == 0:
                    if (local_player_grid[index] == '1' and local_player_grid[index + 1] == '1') and (local_player_grid[index + 10] == '1' or local_player_grid[index - 10] == '1'):
                        return False

                elif j == 9:
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
                        if moving_index + 1 <= 99:
                            moving_index = moving_index + 1
                        else:
                            break

                elif index + 10 <= 99 and local_player_grid[index + 10] == '1' and duplicate_checker(self, indexes, index + 10) and (index + 10) % 10 == column_number:
                    indexes.append(index + 10)
                    ship.append(index + 10)

                    moving_index = index + 20

                    while local_player_grid[moving_index] == '1' and moving_index % 10 == column_number:
                        indexes.append(moving_index)
                        ship.append(moving_index)
                        if moving_index + 10 <= 99:
                            moving_index = moving_index + 10
                        else:
                            break

                ships.append(len(ship))

    ships.sort()

    if ships == [1, 1, 1, 1, 2, 2, 2, 3, 3, 4]:
        return True
    else:
        return False


def ships_format_change(self, grid):
    tuples_for_server = []
    for i in range(len(grid)):
        if grid[i] == '1':
            x = i % 10 + 1
            y = i // 10 + 1
            tuples_for_server.append((x, y))

    return tuples_for_server


def change_name_to_tuple(self, button_name):
    name_len = len(button_name)
    button_index = int()

    for i in range(name_len - 1, -1, -1):
        if button_name[i] == "_":
            button_index = square_address[button_name[i + 1:]]
            break

    x = (button_index - 1) % 10 + 1
    y = (button_index - 1) // 10 + 1

    button_index_tuple = (x, y)

    return button_index_tuple


def get_nick_from_button(self, button_name):
    name_len = len(button_name)
    player_nick = str()

    for i in range(name_len - 1, -1, -1):
        if button_name[i] == "_":
            player_nick = button_name[:i]
            break
    return player_nick


# indicating success or its lack after shot
def change_button_color(self, position_tuple, success, player_id):
    button_address = get_address_from_tuple(self, position_tuple)
    player_nick = game_data.players_dictionary[player_id]

    button = buttons[player_nick + "_" + button_address]

    if success == 1:
        button.setStyleSheet("background-color: green; border: 1 solid black")
    else:
        button.setStyleSheet("background-color: red; border: 1 solid black")


# get button address (A10) from tuple
def get_address_from_tuple(self, position_tuple):
    x = position_tuple[0]
    y = position_tuple[1]

    address = columns[x - 1] + str(y)

    return address


class IntroScreen(QWidget):
    def __init__(self):
        super().__init__()

        self.w = 0
        self.interface()

        self.centerWindow()

        self.setWindowTitle("Statki")
        self.setWindowIcon(QIcon("ship.png"))
        self.dont_want_ready = False

        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)  # blocking window maximizing
        self.setMaximumSize(self.size())  # prevent resizing

        self.header = protocol.PktHeader()

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
            sender = self.sender()
            sender.setEnabled(False)
            tcp_manager.sendPktLogin(self.user_nick, ships_format_change(self, local_player_grid), sock) #SENDING OUR LOGIN


            sock.readyRead.connect(self.onReadyRead)



    def onReadyRead(self):
        print("onReadyRead {}".format(sock.bytesAvailable()))
        while not self.dont_want_ready:
            if self.header.type == 0 and sock.bytesAvailable() >= 8:
                packet_header = sock.read(8)
                self.header.decode(packet_header)
                print("header {} {}", self.header.type, self.header.size)
            elif self.header.type != 0 and sock.bytesAvailable() >= self.header.size:
                packet_payload = sock.read(self.header.size)
                tcp_manager.receivePacket(packet_payload, self.header.type, game_data)
                print("wow {0} {1}".format(self.header.type, self.header.size))

                if self.header.type == protocol.PKT_LOGIN_ACK_ID:
                    print("otrzymano id")
                    if not (game_data.your_id == 0) and not (game_data.id == 0):
                        print("ODPALANIE GAME SCREEN Z PKT_LOGIN_ACK")
                        self.dont_want_ready = True
                        sock.readyRead.disconnect(self.onReadyRead)
                        self.w = GameScreen(self.user_nick)
                        self.w.show()
                        self.close()

                elif self.header.type == protocol.PKT_GAME_START_ID:
                    print("gra rozpoczeta")
                    if not (game_data.your_id == 0) and not (game_data.id == 0):
                        print("ODPALANIE GAME SCREEN Z PKT_GAME_START")
                        self.dont_want_ready = True
                        sock.readyRead.disconnect(self.onReadyRead)
                        self.w = GameScreen(self.user_nick)
                        self.w.show()
                        self.close()

                print("game {} {}".format(game_data.your_id, game_data.id))

                self.header.type = 0 # ZEROWANIE HEADER TYPE
            else:
                break

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
        self.position_chosen = ()
        self.attacked_player_ID = int()
        self.clicked = False

        self.setWindowTitle("Statki")
        self.setWindowIcon(QIcon("ship.png"))

        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)  # blocking window maximizing
        self.setMaximumSize(self.size())  # prevent resizing

        self.header = protocol.PktHeader()

        self.show()

        self.onReadyRead()

    def interface(self, my_nick):
        table_scheme = QGridLayout()  # creating table layout for a window

        nicks = [game_data.players_dictionary[1], game_data.players_dictionary[2], game_data.players_dictionary[3], game_data.players_dictionary[4]]
        nicks.remove(game_data.players_dictionary[game_data.your_id])

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

        sock.readyRead.connect(self.onReadyRead)

        self.setLayout(table_scheme)

    def onReadyRead(self):
        print("onReadyRead2 {}".format(sock.bytesAvailable()))
        while True:
            if self.header.type == 0 and sock.bytesAvailable() >= 8:
                packet_header = sock.read(8)
                self.header.decode(packet_header)
                print("header2 {} {}", self.header.type, self.header.size)

            elif self.header.type != 0 and sock.bytesAvailable() >= self.header.size:
                packet_payload = sock.read(self.header.size)
                tcp_manager.receivePacket(packet_payload, self.header.type, game_data)
                print("wow2 {0} {1}".format(self.header.type, self.header.size))


                if game_data.winner_player_id != 0:
                    # KONIEC GRY
                    if game_data.winner_player_id == game_data.your_id: # WYGRANA
                        self.victory = VictoryWindow()
                        self.victory.show()
                        self.close()

                    else: # PRZEGRANA
                        print("PRZEGRALES")
                        self.close()

                elif self.header.type == protocol.PKT_TURN_START_ID:
                    self.clicked = False
                    if game_data.whose_turn_player_id == 0:
                        print("NIE PRZEKAZANO ID DO GAME_DATA")
                        break

                    for reset_i in range(1, 5):
                        reset_player_label(self, buttons[str(game_data.players_dictionary[reset_i]) + "_label"])

                    indicate_player_label(self, buttons[str(game_data.players_dictionary[game_data.whose_turn_player_id]) + "_label"])

                elif self.header.type == protocol.PKT_TURN_END_ID:
                    change_button_color(self, game_data.position_attacked[0], game_data.success_of_attack, game_data.attacked_player)

                self.header.type = 0  # ZEROWANIE HEADERA
            else:
                break

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

    def closeEvent(self, event):  # are you sure to quit?
        odp = QMessageBox.question(self, "Wyjście", "Czy na pewno koniec?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)  # default option

        if odp == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def keyPressEvent(self, e):  # exit with Escape button
        if e.key() == Qt.Key_Escape:
            self.close()

    def whenClicked(self):
        sender = self.sender()
        self.position_chosen = change_name_to_tuple(self, sender.objectName())

        for iterd in range(1, 5):
            if iterd == game_data.your_id:
                continue
            elif get_nick_from_button(self, sender.objectName()) == game_data.players_dictionary[iterd]:
                self.attacked_player_ID = iterd
                break

        if game_data.whose_turn_player_id == game_data.your_id and not self.clicked:
            self.clicked = True
            tcp_manager.sendPktTurnMove(game_data.turn, self.attacked_player_ID, self.position_chosen, sock)

        print("WYBRANA POZYCJA: {0}  WYBRANY GRACZ: {1}".format(self.position_chosen, self.attacked_player_ID))


class VictoryWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.interface()

        self.centerWindow()

        self.setWindowTitle("Wygrana!")
        self.setWindowIcon(QIcon("ship.png"))

        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)  # blocking window maximizing
        self.setMaximumSize(self.size())  # prevent resizing

        self.open_file = None
        self.data_to_send = 0
        self.finished = False

        self.show()

    def interface(self):
        layout = QVBoxLayout()

        message = QLabel()
        message.setText("Gratulacje! Wygrałeś!\nW nagrodę możesz przesłać plik na serwer.")
        message.setAlignment(Qt.AlignCenter)
        layout.addWidget(message)

        find = QPushButton()
        find.setText("Szukaj...")
        find.clicked.connect(self.on_click)
        layout.addWidget(find)

        sock.bytesWritten.connect(self.bytesWritten)

        self.setLayout(layout)

    def centerWindow(self):
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def closeEvent(self, event):  # are you sure to quit?
        odp = QMessageBox.question(self, "Wyjście", "Czy na pewno koniec?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)  # default option

        if odp == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def keyPressEvent(self, e):  # exit with Escape button
        if e.key() == Qt.Key_Escape:
            self.close()

    def bytesWritten(self):
        if self.finished:
            self.close()

        print("bytes Written sie odpala")
        if not self.open_file or self.data_to_send <= 0:
            print("plik nie otwarty lub brak danych do przeslania")
            return
        print("wysylamy bloczek1")
        print(self.data_to_send)
        if self.data_to_send >= FILE_BLOCK_SIZE:
            data = self.open_file.read(FILE_BLOCK_SIZE)
            print("wysylamy bloczek11")
            tcp_manager.sendPktFileBlock(data, sock)
            self.data_to_send = self.data_to_send - FILE_BLOCK_SIZE
        else:
            data = self.open_file.read(self.data_to_send)
            print("wysylamy bloczek12")
            tcp_manager.sendPktFileBlock(data, sock)
            self.data_to_send = 0
        print("wysylamy bloczek2")
        print(self.data_to_send)

        if self.data_to_send == 0:
            self.finished = True

    def on_click(self):
        filename = QFileDialog.getOpenFileName()

        path_to_file = filename[0]
        print(path_to_file)

        tcp_manager.sendPktFileStart(path_to_file, sock)

        left_data = os.stat(path_to_file).st_size
        print(left_data)

        self.open_file = open(path_to_file, "rb")
        self.data_to_send = left_data


app = QApplication(sys.argv)  # creating app

sock = QTcpSocket()
sock.connectToHost('10.50.140.221', 3124)


window = IntroScreen()
window.text_line.setFocus()
sys.exit(app.exec_())  # starting the app


