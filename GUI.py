import typing
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import pyqtSignal, QEvent
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtGui, QtCore
import sys
import os
import csv
from PyQt5.Qt import Qt
from pynput import keyboard
import time

class CreateAccountPage(QMainWindow):
    keylogger_started = pyqtSignal()

    def __init__(self):
        super(CreateAccountPage, self).__init__()
        loadUi("ui/create_account_page.ui", self)
        self.background_label.setGeometry(50, 50, 1320, 700)
        self.background_label.setPixmap(QPixmap("images/las.jpg"))
        self.back_button.setIcon(QtGui.QIcon("images/back.png"))
        self.back_button.clicked.connect(self.go_to_first_page)
        self.password_lineEdit.hide()
        self.info_label.hide()
        QApplication.instance().installEventFilter(self)
        self.username = None

    def eventFilter(self, obj, event):
        if obj == self.username_lineEdit and event.type() == QEvent.KeyPress:
            key_event = event
            if key_event.key() == Qt.Key_Return:
                self.username = self.username_lineEdit.text()
                self.login(self.username.lower())
                print("Wpisano:", self.username_lineEdit.text())
                return True

        if obj == self.password_lineEdit and event.type() == QEvent.KeyPress:
            key_event = event
            if key_event.text():
                print("Wpisano:", key_event.text())
            return False
        return super().eventFilter(obj, event)

    def keyPressEvent(self, event):
        print(event.text())


    def go_to_first_page(self):
        first_page = FirstPage()
        widget.addWidget(first_page)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def check_value_in_csv(self, target_value):
        if not os.path.exists('keystroke4.csv'):
            with open('keystroke4.csv', 'w', newline='') as new_file:
                pass

        with open('keystroke4.csv', 'r', newline='') as csvfile:
            csv_reader = csv.reader(csvfile)
            headers = next(csv_reader, None)
            if headers is None:
                return False

            for row in csv_reader:
                if target_value in row:
                    return True
        return False

    def login(self, username):
        if self.check_value_in_csv(username):
            self.username_info_label.setText("Username is taken!")
            print("Nazwa użytkownika jest zajęta, wprowadź inną!")
        else:
            print(f'Witaj w naszym systemie, {username}!.')
            self.username_info_label.setStyleSheet("color: rgb(153, 255, 153)")
            self.username_info_label.setText("The correct username. :)")
            self.password_lineEdit.show()
            self.info_label.show()
            self.username_lineEdit.setEnabled(False)

        return username


class FirstPage(QMainWindow):
    def __init__(self):
        super(FirstPage, self).__init__()
        loadUi("ui/first_page.ui", self)
        self.setGeometry(50, 50, 1370, 750)
        self.setFixedSize(1420, 800)
        self.login_button.clicked.connect(self.go_to_login_page)
        self.create_account_button.clicked.connect(self.go_to_create_account_page)
        self.background_label.setGeometry(50, 50, 1320, 700)
        self.background_label.setPixmap(QPixmap("images/las.jpg"))

    def go_to_create_account_page(self):
        create_account_page = CreateAccountPage()
        widget.addWidget(create_account_page)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def go_to_login_page(self):
        login_page = LoginPage()
        widget.addWidget(login_page)
        widget.setCurrentIndex(widget.currentIndex() + 1)

class LoginPage(QMainWindow):
    def __init__(self):
        super(LoginPage, self).__init__()
        loadUi("ui/login_page1.ui", self)
        self.background_label.setGeometry(50, 50, 1320, 700)
        self.background_label.setPixmap(QPixmap("images/las.jpg"))
        self.back_button.setIcon(QtGui.QIcon("images/back.png"))
        self.back_button.clicked.connect(self.go_to_first_page)

    def go_to_first_page(self):
        first_page = FirstPage()
        widget.addWidget(first_page)
        widget.setCurrentIndex(widget.currentIndex() + 1)


app = QApplication(sys.argv)
widget = QtWidgets.QStackedWidget()
first_page = FirstPage()
widget.addWidget(first_page)
widget.show()

try:
    sys.exit(app.exec_())
except:
    print("Exiting")
