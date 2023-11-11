from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys
from PyQt5.QtGui import QPixmap
class FirstPage(QMainWindow):
    def __init__(self):
        super(FirstPage, self).__init__()
        loadUi("ui/first_page.ui", self)
        self.setGeometry(50,50,1370, 750)
        self.setFixedSize(1420, 800)
        self.login_button.clicked.connect(self.go_to_login_page)
        self.create_account_button.clicked.connect(self.go_to_create_account_page)
        self.background_label.setGeometry(50, 50, 1320, 700)
        self.background_label.setPixmap(QPixmap("images/las.jpg"))

    def go_to_create_account_page(self):
        create_account_page = CreateAccountPage()
        widget.addWidget(create_account_page)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def go_to_login_page(self):
        create_account_page = LoginPage()
        widget.addWidget(create_account_page)
        widget.setCurrentIndex(widget.currentIndex()+1)
class CreateAccountPage(QMainWindow):
    def __init__(self):
        super(CreateAccountPage, self).__init__()
        loadUi("ui/create_account_page.ui", self)
        self.background_label.setGeometry(50, 50, 1320, 700)
        self.background_label.setPixmap(QPixmap("images/las.jpg"))
        self.back_button.setIcon(QtGui.QIcon("images/back.png"))
        self.back_button.clicked.connect(self.go_to_firsr_page)
    def go_to_firsr_page(self):
        firts_page = FirstPage()
        widget.addWidget(firts_page)
        widget.setCurrentIndex(widget.currentIndex() + 1)
class LoginPage(QMainWindow):
    def __init__(self):
        super(LoginPage, self).__init__()
        loadUi("ui/login_page.ui", self)
        self.background_label.setGeometry(50, 50, 1320, 700)
        self.background_label.setPixmap(QPixmap("images/las.jpg"))
        self.back_button.setIcon(QtGui.QIcon("images/back.png"))
        self.back_button.clicked.connect(self.go_to_firsr_page)

    def go_to_firsr_page(self):
        firts_page = FirstPage()
        widget.addWidget(firts_page)
        widget.setCurrentIndex(widget.currentIndex() + 1)

app = QApplication(sys.argv)
widget = QtWidgets.QStackedWidget()
firts_page = FirstPage()
widget.addWidget(firts_page)
widget.show()

try:
    sys.exit(app.exec_())
except:
    print("Exiting")