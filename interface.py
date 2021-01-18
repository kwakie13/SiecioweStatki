from __future__ import unicode_literals

import sys

from PyQt5.Qt import *

nicks = ["Gracz 1", "Gracz 2", "Gracz 3"]
columns = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
buttons = {}

def indicate_player_label(self, label): # function indicating player move (changing label background color)
    label.setStyleSheet("background-color: lightgreen; border: 1 solid black; border-radius: 15; padding: 5")

    return label

def reset_player_label(self, label): # function resetting move indicator
    label.setStyleSheet("border: 1 solid black; border-radius: 15; padding: 5")

    return label

def player_grid(self, nick):
    groupBox = QGroupBox()  # box for player's buttons
    grid = QGridLayout()  # creating grid to place buttons

    for j in range(len(columns)):  # for each column
        for k in range(10):  # for each row
            ID = (nick + "_" + columns[j] + str(k + 1))  # ID for a button

            button = QPushButton()  # creating button with ID as a name
            button.setObjectName(ID)
            button.setMaximumSize(20, 20)

            button.clicked.connect(self.whenClicked)  # connecting action to click

            grid.addWidget(button, j, k)  # adding button to grid
            self.saveButton(button)  # saving button's name

    groupBox.setLayout(grid)  # setting box's layout (previously created and filled grid)

    return groupBox

def player_label(self, nick):
    groupBox = QGroupBox()
    groupBox.setStyleSheet("border : none")

    label = QLabel(nick)
    label.setObjectName("{0}_label".format(nick))
    self.saveButton(label)

    reset_player_label(self, label) # indicating it's player move
    label.setFont(QFont('Calibri', 15))

    row = QHBoxLayout()
    row.addWidget(label, alignment = Qt.AlignCenter)

    groupBox.setLayout(row)

    return groupBox

class GUI(QWidget):
    def __init__(self, parent=None):
        super().__init__()

        self.interface()

    def interface(self):
        table_scheme = QGridLayout()  # creating table layout for a window

        for i in range(len(nicks)): # loop creating labels with indicators for opponents
            row = player_label(self, nicks[i])
            table_scheme.addWidget(row, 0, i)

        for i in range(len(nicks)):  # loop creating grids for opponents
            box = player_grid(self, nicks[i])
            table_scheme.addWidget(box, 1, i)

        self.setLayout(table_scheme)

        self.setGeometry(0, 0, 600, 200)
        window = self.frameGeometry()  # checking window's geometry
        window.moveCenter(QDesktopWidget().availableGeometry().center())  # move to the screen's center point
        self.move(window.topLeft())
        # self.setWindowIcon(QIcon("kalkulator.png"))
        self.setWindowTitle("Statki")
        self.show()

    def saveButton(self, obj):
        buttons[obj.objectName()] = obj

    def findButton(self, text):
        return buttons[text]

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
window = GUI()  # creating window with GUI class
sys.exit(app.exec_())  # starting the app
