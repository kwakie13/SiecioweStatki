from __future__ import unicode_literals
import sys

from PyQt5.Qt import *

nicks = ["Gracz 1", "Gracz 2", "Gracz 3"]
columns = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
buttons = {}

def player_grid(self, nick):
    columns = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
    groupBox = QGroupBox(nick)  # box for player's buttons
    grid = QGridLayout()  # creating grid to place buttons

    for j in range(len(columns)):  # for each column
        for k in range(10):  # for each row
            ID = (nick + "_" + columns[j] + str(k + 1))  # ID for a button

            button = QPushButton()  # creating button with ID as a name
            button.setObjectName(ID)

            button.clicked.connect(self.whenClicked)  # connecting action to click

            grid.addWidget(button, j, k)  # adding button to grid
            self.saveButton(button)  # saving button's name

    groupBox.setLayout(grid)  # setting box's layout (previously created and filled grid)

    return groupBox

class GUI(QWidget):
    def __init__(self, parent=None):
        super().__init__()

        self.interface()

    def interface(self):
        table_scheme = QGridLayout()  # creating table layout for a window

        for i in range(len(nicks)): # loop creating grids for opponents
            box = player_grid(self, nicks[i])
            table_scheme.addWidget(box, 0, i)

        # table_scheme.addWidget(groupBox, 0, i) # adding to main scheme (window)

        self.setLayout(table_scheme)

        self.setGeometry(0, 0, 600, 200)
        window = self.frameGeometry()  # checking window's geometry
        window.moveCenter(
            QDesktopWidget().availableGeometry().center()
        )  # move to the screen's center point
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
        sender.setStyleSheet("background-color : yellow")

        if isinstance(sender, QPushButton):
            pass
            # print(sender.objectName)


app = QApplication(sys.argv)  # creating app
window = GUI()  # creating window with GUI class
sys.exit(app.exec_())  # starting the app