import difflib
import random
import typing

import Levenshtein
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import pyqtSignal, QEvent, QThread, pyqtSlot
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtGui
import sys
import os
import csv
from PyQt5.Qt import Qt
from pynput import keyboard
import time
from EER import evaluateEER
from scipy.spatial.distance import euclidean, cityblock
import pandas as pd

class KeyPressInterceptor(QThread):
    keyPressed = pyqtSignal(str)
    password_info_signal = pyqtSignal(str)
    good_password_info_signal = pyqtSignal(str)
    clear_password_label_signal = pyqtSignal(bool)
    user_time_list_signal = pyqtSignal(list)
    end_session_signal = pyqtSignal(bool)
    def __init__(self):
        super().__init__()
        self.take_key = []
        self.last_key_release_time = 0
        self.first_key_pressed_hold = False
        self.last_key_press_time = 0
        self.your_time = []
        self.cleaned_list = []
        self.name_key = []
        self.t = 0
        self.count = 1
        self._run_flag = True
        self.session_index = 1
        self.con_password = '.ego1buslix'
        self.ignored_key = {
            keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r, keyboard.Key.enter, keyboard.Key.backspace,
            keyboard.Key.space, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r, keyboard.Key.delete, keyboard.Key.caps_lock,
            keyboard.Key.tab, keyboard.Key.alt_l, keyboard.Key.alt_r, keyboard.Key.esc, keyboard.Key.f1,
            keyboard.Key.f2,
            keyboard.Key.f3, keyboard.Key.f4, keyboard.Key.f5, keyboard.Key.f6, keyboard.Key.f7, keyboard.Key.f8,
            keyboard.Key.f9,
            keyboard.Key.f10, keyboard.Key.f11, keyboard.Key.f12, keyboard.Key.f13, keyboard.Key.f14, keyboard.Key.f15,
            keyboard.Key.f16, keyboard.Key.f17, keyboard.Key.f18, keyboard.Key.f19, keyboard.Key.f20, keyboard.Key.f21,
            keyboard.Key.f22, keyboard.Key.f23, keyboard.Key.f24, keyboard.Key.print_screen, keyboard.Key.scroll_lock,
            keyboard.Key.pause, keyboard.Key.insert, keyboard.Key.home, keyboard.Key.end, keyboard.Key.page_up,
            keyboard.Key.page_down, keyboard.Key.num_lock, keyboard.Key.left, keyboard.Key.right, keyboard.Key.up,
            keyboard.Key.down, keyboard.Key.menu, keyboard.Key.media_play_pause,keyboard.Key.cmd, keyboard.Key.cmd_l,
            keyboard.Key.cmd_r

        }
        self.header = ['subject', 'session_index', 'rep', 'H.dot', 'UD.dot.e', 'DD.dot.e', 'H.e',
                       'UD.e.g', 'DD.e.g', 'H.g', 'UD.g.o', 'DD.g.o', 'H.o', 'UD.o.one', 'DD.o.one', 'H.one',
                       'UD.one.B',
                       'DD.one.B',
                       'H.B', 'UD.B.u', 'DD.B.u', 'H.u', 'UD.u.s', 'DD.u.s', 'H.s', 'UD.s.l', 'DD.s.l', 'H.l', 'UD.l.i',
                       'DD.l.i', 'H.i'
            , 'UD.i.x', 'DD.i.x', 'H.x']

    def on_key_release(self, key):
        if hasattr(key, 'char') or hasattr(key, 'name'):
            self.last_key_release_time = time.time()

        if not self.first_key_pressed_hold:
            return False

        time_taken = round(time.time() - self.t, 5)
        if key not in self.ignored_key:
            self.your_time.append(float(time_taken))
            self.take_key.append(str(key))
            self.keyPressed.emit(str(key))
        if key == keyboard.Key.backspace:
            print("bck")

        return False

    def on_key_press(self, key):
        self.first_key_pressed_hold = True
        if key not in self.ignored_key:
            if hasattr(key, 'char') or hasattr(key, 'name') and self.last_key_release_time != 0:
                time_difference_ud = round(time.time() - self.last_key_release_time, 5)
                if key.char != '.':
                    self.your_time.append(time_difference_ud)
                    self.keyPressed.emit(str(key))

            if hasattr(key, 'char') or hasattr(key, 'name') and key.char is not None:
                time_difference_dd = round(time.time() - self.last_key_press_time, 5)
                self.last_key_press_time = time.time()
                if key.char != '.':
                    self.your_time.append(time_difference_dd)
                    self.keyPressed.emit(str(key))
        return False

    def start_listening(self):
        while self._run_flag:
            self.t = time.time()
            with keyboard.Listener(on_press=self.on_key_press, on_release=self.on_key_release) as listener:
                listener.join()

            self.cleaned_list = [element.replace("'", '') for element in self.take_key]
            result = ''.join(self.cleaned_list)
            if len(self.con_password) == len(result):
                if self.con_password == result:
                    self.your_time.insert(0, self.session_index)
                    self.your_time.insert(1, self.count)
                    if len(self.your_time) + 1 != len(self.header):
                        self.password_info_signal.emit(f"Retry attempt {self.count}. Time not recorded.")
                        self.clear_password_label_signal.emit(True)
                    else:
                        self.count += 1
                        self.good_password_info_signal.emit(f"Good job! {self.count} out of 30 correct repetitions!")
                        self.user_time_list_signal.emit(self.your_time)

                    self.last_key_release_time = 0
                    self.last_key_press_time = 0
                    self.take_key = []
                    self.cleaned_list = []
                    self.your_time = []

                    if self.count == 31:
                        self.end_session_signal.emit(True)

            elif result != self.con_password[:len(result)]:
                self.clear_password_label_signal.emit(True)
                self.password_info_signal.emit("Sorry, try again! You've made a mistake!")
                self.last_key_release_time = 0
                self.last_key_press_time = 0
                self.take_key = []
                self.cleaned_list = []
                self.your_time = []

    def run(self):
        self.start_listening()

    def on_key_pressed(self, key):
        print("Przechwycono klawisz:", key)

    def stop_listening(self):
        self._run_flag = False

class KeyPressInterceptor2(QThread):
    keyPressed = pyqtSignal(str)
    password_info_signal = pyqtSignal(str)
    good_password_info_signal = pyqtSignal(str)
    clear_password_label_signal = pyqtSignal(bool)
    user_time_list_signal = pyqtSignal(list)
    verification_signal = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.take_key = []
        self.last_key_release_time = 0
        self.first_key_pressed_hold = False
        self.last_key_press_time = 0
        self.your_time = []
        self.cleaned_list = []
        self.name_key = []
        self.user_scores = []
        self.imposter_scores = []
        self.mean_vector = []
        self.odleglosci = []
        self.all_mean_vector = []
        self.user_index = []
        self.all_time = []
        self.t = 0
        self.count = 1
        self._run_flag = True
        self.session_index = 1
        self.con_password = '.ego1buslix'
        self.ignored_key = {
            keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r, keyboard.Key.enter, keyboard.Key.backspace,
            keyboard.Key.space, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r, keyboard.Key.delete, keyboard.Key.caps_lock,
            keyboard.Key.tab, keyboard.Key.alt_l, keyboard.Key.alt_r, keyboard.Key.esc, keyboard.Key.f1,
            keyboard.Key.f2,
            keyboard.Key.f3, keyboard.Key.f4, keyboard.Key.f5, keyboard.Key.f6, keyboard.Key.f7, keyboard.Key.f8,
            keyboard.Key.f9,
            keyboard.Key.f10, keyboard.Key.f11, keyboard.Key.f12, keyboard.Key.f13, keyboard.Key.f14, keyboard.Key.f15,
            keyboard.Key.f16, keyboard.Key.f17, keyboard.Key.f18, keyboard.Key.f19, keyboard.Key.f20, keyboard.Key.f21,
            keyboard.Key.f22, keyboard.Key.f23, keyboard.Key.f24, keyboard.Key.print_screen, keyboard.Key.scroll_lock,
            keyboard.Key.pause, keyboard.Key.insert, keyboard.Key.home, keyboard.Key.end, keyboard.Key.page_up,
            keyboard.Key.page_down, keyboard.Key.num_lock, keyboard.Key.left, keyboard.Key.right, keyboard.Key.up,
            keyboard.Key.down, keyboard.Key.menu, keyboard.Key.media_play_pause, keyboard.Key.cmd, keyboard.Key.cmd_l,
            keyboard.Key.cmd_r

        }

    def on_key_release(self, key):
        if hasattr(key, 'char') or hasattr(key, 'name'):
            self.last_key_release_time = time.time()

        if not self.first_key_pressed_hold:
            return False

        time_taken = round(time.time() - self.t, 5)
        if key not in self.ignored_key:
            self.your_time.append(float(time_taken))
            self.take_key.append(str(key))
            self.keyPressed.emit(str(key))

        return False

    def on_key_press(self, key):
        self.first_key_pressed_hold = True
        if key not in self.ignored_key:
            if hasattr(key, 'char') or hasattr(key, 'name') and self.last_key_release_time != 0:
                time_difference_ud = round(time.time() - self.last_key_release_time, 5)
                if key.char != '.':
                    self.your_time.append(time_difference_ud)
                    self.keyPressed.emit(str(key))

            if hasattr(key, 'char') or hasattr(key, 'name') and key.char is not None:
                time_difference_dd = round(time.time() - self.last_key_press_time, 5)
                self.last_key_press_time = time.time()
                if key.char != '.':
                    self.your_time.append(time_difference_dd)
                    self.keyPressed.emit(str(key))
        return False

    def start_listening(self):
        while self._run_flag:
            self.t = time.time()
            with keyboard.Listener(on_press=self.on_key_press, on_release=self.on_key_release) as listener:
                listener.join()

            self.cleaned_list = [element.replace("'", '') for element in self.take_key]
            result = ''.join(self.cleaned_list)
            if len(self.con_password) == len(result):
                if self.con_password == result:
                    if len(self.your_time) != 31:
                        self.password_info_signal.emit(f"Retry attempt {self.count}. Time not recorded.")
                        self.clear_password_label_signal.emit(True)
                        self.last_key_release_time = 0
                        self.last_key_press_time = 0
                        self.take_key = []
                        self.cleaned_list = []
                        self.your_time = []
                    else:
                        self.good_password_info_signal.emit("Password accepted! Verification in progress!")
                        self.verification_signal.emit(self.your_time)

            elif result != self.con_password[:len(result)]:
                self.clear_password_label_signal.emit(True)
                self.password_info_signal.emit("Sorry, try again! You've made a mistake!")
                self.last_key_release_time = 0
                self.last_key_press_time = 0
                self.take_key = []
                self.cleaned_list = []
                self.your_time = []


    def run(self):
        self.start_listening()

    def stop_listening(self):
        self._run_flag = False


class CreateAccountPage(QMainWindow):

    def __init__(self):
        super(CreateAccountPage, self).__init__()
        loadUi("ui/create_account_page.ui", self)
        self.background_label.setGeometry(50, 50, 1320, 700)
        self.background_label.setPixmap(QPixmap("images/las.jpg"))
        self.back_button.setIcon(QtGui.QIcon("images/back.png"))
        self.back_button.clicked.connect(self.go_to_first_page)
        self.password_lineEdit.hide()
        self.info_label.hide()
        self.conf_password_info_label.hide()
        QApplication.instance().installEventFilter(self)
        self.username = None
        self.con_password = '.ego1buslix'
        self.take_key = []
        self.name_key = []
        self.user_time = []
        self.cleaned_list = []
        self.session_index = 1
        self.counter = 0
        self.count = 1
        self.my_class_thread = KeyPressInterceptor()
        self.my_class_thread.password_info_signal.connect(self.password_info)
        self.my_class_thread.clear_password_label_signal.connect(self.password_label_clear)
        self.my_class_thread.good_password_info_signal.connect(self.good_password_info)
        self.my_class_thread.user_time_list_signal.connect(self.user_time_list)
        self.my_class_thread.end_session_signal.connect(self.end_session)
        self.my_class_thread.start()
        self.header = ['subject', 'session_index', 'rep', 'H.dot', 'UD.dot.e', 'DD.dot.e', 'H.e',
                       'UD.e.g', 'DD.e.g', 'H.g', 'UD.g.o', 'DD.g.o', 'H.o', 'UD.o.one', 'DD.o.one', 'H.one',
                       'UD.one.B',
                       'DD.one.B',
                       'H.B', 'UD.B.u', 'DD.B.u', 'H.u', 'UD.u.s', 'DD.u.s', 'H.s', 'UD.s.l', 'DD.s.l', 'H.l', 'UD.l.i',
                       'DD.l.i', 'H.i'
            , 'UD.i.x', 'DD.i.x', 'H.x']

    def eventFilter(self, obj, event):
        if obj == self.username_lineEdit and event.type() == QEvent.KeyPress:
            key_event = event
            if key_event.key() == Qt.Key_Return:
                self.username = self.username_lineEdit.text()
                self.login(self.username.lower())
                self.name_key.append(key_event.text())
                return False

        if obj == self.password_lineEdit and event.type() == QEvent.KeyPress:
            self.conf_password_info_label.show()
            self.conf_password_info_label.clear()
            return False
        return super().eventFilter(obj, event)

    def keyPressEvent(self, event):
        print(event.text())

    def go_to_first_page(self):
        self.my_class_thread.stop_listening()
        first_page = FirstPage()
        widget.addWidget(first_page)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def check_value_in_csv(self, target_value):
        if not os.path.exists('keystroke5.csv'):
            with open('keystroke5.csv', 'w', newline='') as new_file:
                pass

        with open('keystroke5.csv', 'r', newline='') as csvfile:
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
        else:
            self.username_info_label.setStyleSheet("color: rgb(153, 255, 153)")
            self.username_info_label.setText("The correct username. :)")
            self.password_lineEdit.show()
            self.info_label.show()
            self.conf_password_info_label.clear()
            self.username_lineEdit.setEnabled(False)
        return username

    def is_csv_empty(self, file_name):
        with open(file_name, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)

            first_row = next(csv_reader, None)
            if first_row is None:
                return True
            else:
                for row in csv_reader:
                    if any(row):
                        return False
        return True

    @pyqtSlot(str)
    def password_info(self, info):
        self.conf_password_info_label.setText(info)
        self.conf_password_info_label.setStyleSheet("color: rgb(255, 108, 108)")

    @pyqtSlot(str)
    def good_password_info(self, info):
        self.conf_password_info_label.setText(info)
        self.conf_password_info_label.setStyleSheet("color: rgb(153, 255, 153)")
        self.password_lineEdit.clear()

    @pyqtSlot(bool)
    def password_label_clear(self, info):
        if info:
            self.password_lineEdit.clear()

    @pyqtSlot(list)
    def user_time_list(self, list_info):
        list_info.insert(0, self.username)
        with open('keystroke5.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            if self.is_csv_empty('keystroke5.csv'):
                writer.writerow(self.header)
            writer.writerow(list_info)

    @pyqtSlot(bool)
    def end_session(self, info):
        if info:
            self.conf_password_info_label.setText("Thank you, session ended for today :)")
            self.conf_password_info_label.setStyleSheet("color: rgb(153, 255, 153)")
            self.password_lineEdit.clear()
            self.password_lineEdit.setEnabled(False)
            self.my_class_thread.stop_listening()


class SessionContinuationPage(QMainWindow):
    start_listener_signal = pyqtSignal(bool)

    def __init__(self):
        super(SessionContinuationPage, self).__init__()
        loadUi("ui/session_continuation.ui", self)
        self.background_label.setGeometry(50, 50, 1320, 700)
        self.background_label.setPixmap(QPixmap("images/las.jpg"))
        self.back_button.setIcon(QtGui.QIcon("images/back.png"))
        self.back_button.clicked.connect(self.go_to_first_page)
        self.password_lineEdit.hide()
        self.info_label.hide()
        self.conf_password_info_label.hide()
        QApplication.instance().installEventFilter(self)
        self.username = None
        self.con_password = '.ego1buslix'
        self.take_key = []
        self.name_key = []
        self.user_time = []
        self.cleaned_list = []
        self.session_index = 1
        self.counter = 0
        self.count = 1
        self.first_count_value = 0
        self.my_class_thread = KeyPressInterceptor()
        self.my_class_thread.password_info_signal.connect(self.password_info)
        self.my_class_thread.clear_password_label_signal.connect(self.password_label_clear)
        self.my_class_thread.good_password_info_signal.connect(self.good_password_info)
        self.my_class_thread.user_time_list_signal.connect(self.user_time_list)
        self.my_class_thread.end_session_signal.connect(self.end_session)
        self.my_class_thread.start()
        self.header = ['subject', 'session_index', 'rep', 'H.dot', 'UD.dot.e', 'DD.dot.e', 'H.e',
                       'UD.e.g', 'DD.e.g', 'H.g', 'UD.g.o', 'DD.g.o', 'H.o', 'UD.o.one', 'DD.o.one', 'H.one',
                       'UD.one.B',
                       'DD.one.B',
                       'H.B', 'UD.B.u', 'DD.B.u', 'H.u', 'UD.u.s', 'DD.u.s', 'H.s', 'UD.s.l', 'DD.s.l', 'H.l', 'UD.l.i',
                       'DD.l.i', 'H.i'
            , 'UD.i.x', 'DD.i.x', 'H.x']

    def eventFilter(self, obj, event):
        if obj == self.username_lineEdit and event.type() == QEvent.KeyPress:
            key_event = event
            if key_event.key() == Qt.Key_Return:
                self.username = self.username_lineEdit.text()
                self.login(self.username.lower())
                self.name_key.append(key_event.text())
                return False

        if obj == self.password_lineEdit and event.type() == QEvent.KeyPress:
            self.conf_password_info_label.show()
            self.conf_password_info_label.clear()
            return False
        return super().eventFilter(obj, event)

    def keyPressEvent(self, event):
        print(event.text())

    def check_value_in_csv(self, target_value):
        if not os.path.exists('keystroke5.csv'):
            with open('keystroke5.csv', 'w', newline='') as new_file:
                pass

        with open('keystroke5.csv', 'r', newline='') as csvfile:
            csv_reader = csv.reader(csvfile)
            headers = next(csv_reader, None)
            if headers is None:
                return False

            for row in csv_reader:
                if target_value in row:
                    return True
        return False

    def get_last_session_index_for_subject(self, target_subject):
        last_session_index = None

        with open('keystroke5.csv', 'r', newline='') as csvfile:
            csv_reader = csv.DictReader(csvfile)

            for row in csv_reader:
                if row['subject'] == target_subject:
                    last_session_index = row['session_index']

        return int(last_session_index)

    def get_last_rep_for_subject(self, target_subject):
        last_rep = None

        with open('keystroke5.csv', 'r', newline='') as csvfile:
            csv_reader = csv.DictReader(csvfile)

            for row in csv_reader:
                if row['subject'] == target_subject:
                    last_rep = row['rep']
        return int(last_rep)


    def login(self, username):
        if self.check_value_in_csv(username):
            self.username_info_label.setStyleSheet("color: rgb(153, 255, 153)")
            self.username_info_label.setText("The correct username. :)")
            self.password_lineEdit.show()
            self.info_label.show()
            self.conf_password_info_label.clear()
            self.username_lineEdit.setEnabled(False)
            self.session_index = self.get_last_session_index_for_subject(username) + 1
            self.session_number_label.setText(f"Session number {self.session_index}")
            self.count = self.get_last_rep_for_subject(username)
            self.first_count_value = self.get_last_rep_for_subject(username)
        else:
            self.username_info_label.setText("Username does not exist!")

        return username

    def is_csv_empty(self, file_name):
        with open(file_name, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)

            first_row = next(csv_reader, None)
            if first_row is None:
                return True
            else:
                for row in csv_reader:
                    if any(row):
                        return False
        return True

    @pyqtSlot(str)
    def password_info(self, info):
        self.conf_password_info_label.setText(info)
        self.conf_password_info_label.setStyleSheet("color: rgb(255, 108, 108)")

    @pyqtSlot(str)
    def good_password_info(self, info):
        self.conf_password_info_label.setText(info)
        self.conf_password_info_label.setStyleSheet("color: rgb(153, 255, 153)")
        self.password_lineEdit.clear()

    @pyqtSlot(bool)
    def password_label_clear(self, info):
        if info:
            self.password_lineEdit.clear()

    @pyqtSlot(list)
    def user_time_list(self, list_info):
        print(self.username)
        list_info.insert(0, self.username)
        list_count = int(list_info[2]) + self.count
        list_info[2] = list_count
        list_info[1] = self.session_index
        with open('keystroke5.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            if self.is_csv_empty('keystroke5.csv'):
                writer.writerow(self.header)
            writer.writerow(list_info)

    @pyqtSlot(bool)
    def end_session(self, info):
        if info:
            self.conf_password_info_label.setText("Thank you, session ended for today :)")
            self.conf_password_info_label.setStyleSheet("color: rgb(153, 255, 153)")
            self.password_lineEdit.clear()
            self.password_lineEdit.setEnabled(False)

    def go_to_first_page(self):
        self.my_class_thread.stop_listening()
        first_page = FirstPage()
        widget.addWidget(first_page)
        widget.setCurrentIndex(widget.currentIndex() + 1)

class FirstPage(QMainWindow):
    def __init__(self):
        super(FirstPage, self).__init__()
        loadUi("ui/first_page.ui", self)
        self.setGeometry(50, 50, 1370, 750)
        self.setFixedSize(1420, 800)
        self.login_button.clicked.connect(self.go_to_login_page)
        self.create_account_button.clicked.connect(self.go_to_create_account_page)
        self.register_button.clicked.connect(self.go_to_register_page)
        self.identify_button.clicked.connect(self.go_to_identify_page)
        self.complete_sessions_button.clicked.connect(self.go_to_session_page)
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

    def go_to_identify_page(self):
        identify_page = IdentifyPage()
        widget.addWidget(identify_page)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def go_to_register_page(self):
        register_page = RegisterPage()
        widget.addWidget(register_page)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def go_to_session_page(self):
        session_page = SessionContinuationPage()
        widget.addWidget(session_page)
        widget.setCurrentIndex(widget.currentIndex() + 1)


class LoginPage(QMainWindow):
    def __init__(self):
        super(LoginPage, self).__init__()
        loadUi("ui/login_page1.ui", self)
        self.background_label.setGeometry(50, 50, 1320, 700)
        self.background_label.setPixmap(QPixmap("images/las.jpg"))
        self.back_button.setIcon(QtGui.QIcon("images/back.png"))
        self.back_button.clicked.connect(self.go_to_first_page)
        self.path = "keystroke5.csv"
        self.data = pd.read_csv(self.path)
        self.subjects = self.data["subject"].unique()
        self.password_lineEdit.hide()
        self.info_label.hide()
        self.conf_password_info_label.hide()
        QApplication.instance().installEventFilter(self)
        self.username = None
        self.con_password = '.ego1buslix'
        self.take_key = []
        self.name_key = []
        self.user_time = []
        self.cleaned_list = []
        self.user_scores = []
        self.imposter_scores = []
        self.mean_vector = []
        self.odleglosci = []
        self.all_mean_vector = []
        self.user_index = []
        self.session_index = 1
        self.counter = 0
        self.count = 1
        self.my_class_thread = KeyPressInterceptor2()
        self.my_class_thread.password_info_signal.connect(self.password_info)
        self.my_class_thread.clear_password_label_signal.connect(self.password_label_clear)
        self.my_class_thread.good_password_info_signal.connect(self.good_password_info)
        self.my_class_thread.verification_signal.connect(self.verification)
        self.my_class_thread.start()
        self.header = ['subject', 'session_index', 'rep', 'H.dot', 'UD.dot.e', 'DD.dot.e', 'H.e',
                       'UD.e.g', 'DD.e.g', 'H.g', 'UD.g.o', 'DD.g.o', 'H.o', 'UD.o.one', 'DD.o.one', 'H.one',
                       'UD.one.B',
                       'DD.one.B',
                       'H.B', 'UD.B.u', 'DD.B.u', 'H.u', 'UD.u.s', 'DD.u.s', 'H.s', 'UD.s.l', 'DD.s.l', 'H.l', 'UD.l.i',
                       'DD.l.i', 'H.i'
            , 'UD.i.x', 'DD.i.x', 'H.x']

    def eventFilter(self, obj, event):
        if obj == self.username_lineEdit and event.type() == QEvent.KeyPress:
            key_event = event
            if key_event.key() == Qt.Key_Return:
                self.username = self.username_lineEdit.text()
                self.login(self.username.lower())
                self.name_key.append(key_event.text())
                return False

        if obj == self.password_lineEdit and event.type() == QEvent.KeyPress:
            key_event = event
            self.conf_password_info_label.show()
            self.conf_password_info_label.clear()
            return False
        return super().eventFilter(obj, event)

    def keyPressEvent(self, event):
        print(event.text())

    def go_to_first_page(self):
        first_page = FirstPage()
        widget.addWidget(first_page)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def go_to_user_page(self):
        user_page = UserPage(self.username)
        widget.addWidget(user_page)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def login(self, username):
        if username not in self.subjects:
            self.username_info_label.setText("Username does not exist!")
        else:
            if self.get_last_rep_for_subject(username) < 90:
                self.username_info_label.setText("Insufficient test data. Please return to the session and input new data. :)")
            else:
                self.username_info_label.setStyleSheet("color: rgb(153, 255, 153)")
                self.username_info_label.setText("The correct username. :)")
                self.password_lineEdit.show()
                self.info_label.show()
                self.conf_password_info_label.clear()
                self.username_lineEdit.setEnabled(False)
                take_user_index = np.where(self.subjects == username)[0].tolist()
                self.user_index = int(take_user_index[0])

    def get_last_rep_for_subject(self, target_subject):
        last_rep = None

        with open('keystroke5.csv', 'r', newline='') as csvfile:
            csv_reader = csv.DictReader(csvfile)

            for row in csv_reader:
                if row['subject'] == target_subject:
                    last_rep = row['rep']
        return int(last_rep)

    def training(self):
        self.mean_vector = self.train.mean().values
        self.std_vector = self.train.std().values
        dropping_indices = []
        for i in range(self.train.shape[0]):
            cur_score = euclidean(self.train.iloc[i].values,
                                  self.mean_vector)
            if (cur_score > 3 * self.std_vector).all() == True:
                dropping_indices.append(i)
        self.train = self.train.drop(self.train.index[dropping_indices])
        self.mean_vector = self.train.mean().values
        self.all_mean_vector.append(self.mean_vector)


    def testing(self, vector_2):

        if len(self.all_mean_vector) == len(self.subjects):
            vector_1 = self.all_mean_vector[self.user_index]
            self.manhattan_distance = cityblock(vector_2, vector_1)
            if self.manhattan_distance <= 2.1:
                self.go_to_user_page()
            else:
                self.conf_password_info_label.setText("Login attempt failed..")
                self.conf_password_info_label.setStyleSheet("color: rgb(255, 108, 108)")
                self.password_lineEdit.setEnabled(False)
                self.my_class_thread.stop_listening()

    def evaluate(self, vector):

        for subject in self.subjects:
            genuine_user_data = self.data.loc[self.data.subject == subject, \
                                "H.dot":"H.x"]
            imposter_data = self.data.loc[self.data.subject != subject, :]

            self.train = genuine_user_data[20:85]
            self.test_genuine = genuine_user_data[85:]
            self.test_imposter = imposter_data.groupby("subject"). \
                                     head(5).loc[:, "H.dot":"H.x"]

            self.training()
            self.testing(vector)


    @pyqtSlot(str)
    def password_info(self, info):
        self.conf_password_info_label.setText(info)
        self.conf_password_info_label.setStyleSheet("color: rgb(255, 108, 108)")

    @pyqtSlot(str)
    def good_password_info(self, info):
        self.conf_password_info_label.setText(info)
        self.conf_password_info_label.setStyleSheet("color: rgb(153, 255, 153)")
        self.password_lineEdit.setEnabled(False)
        self.password_lineEdit.clear()

    @pyqtSlot(bool)
    def password_label_clear(self, info):
        if info:
            self.password_lineEdit.clear()


    @pyqtSlot(list)
    def verification(self, time_list):
        self.evaluate(time_list)

class UserPage(QMainWindow):
    def __init__(self, name):
        super(UserPage, self).__init__()
        loadUi("ui/user_page.ui", self)
        self.background_label.setGeometry(50, 50, 1320, 700)
        self.background_label.setPixmap(QPixmap("images/las.jpg"))
        self.image_label.setPixmap(QPixmap("images/cute.jpg"))
        self.back_button.setIcon(QtGui.QIcon("images/back.png"))
        self.back_button.clicked.connect(self.go_to_first_page)
        self.name_label.setText(f"Hello, {name}! :)")

    def go_to_first_page(self):
        first_page = FirstPage()
        widget.addWidget(first_page)
        widget.setCurrentIndex(widget.currentIndex() + 1)


class IdentifyPage(QMainWindow):
    def __init__(self):
        super(IdentifyPage, self).__init__()
        self.user_input = None
        loadUi("ui/identify_page.ui", self)
        self.background_label.setGeometry(50, 50, 1320, 700)
        self.background_label.setPixmap(QPixmap("images/las.jpg"))
        self.back_button.setIcon(QtGui.QIcon("images/back.png"))
        self.back_button.clicked.connect(self.go_to_first_page)

        self.path = "mistakes_features_all.csv"
        self.data = pd.read_csv(self.path)
        self.users = self.data["User"].unique()

        self.typing_start_time = 0
        self.typing_end_time = 0

        self.bs_count = 0
        self.dlt_count = 0

        self.mean_vector = []
        self.all_mean_vector = []
        self.count = 1

        self.vector = []

        self.register = RegisterPage()

        QApplication.instance().installEventFilter(self)

    def go_to_first_page(self):
        first_page = FirstPage()
        widget.addWidget(first_page)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def eventFilter(self, obj, event):
        if obj == self.text_lineEdit and event.type() == QEvent.KeyPress:
            key_event = event
            if self.typing_start_time == 0:
                self.typing_start_time = time.time()
            if key_event.key() == Qt.Key_Return:
                self.typing_end_time - time.time()
                user_input = self.text_lineEdit.text()
                self.info_label.setText("Thank you! I think you are...")
                self.evaluate(self.get_vector(user_input))
                self.text_lineEdit.hide()
                self.text_label.hide()
                return True
            elif key_event.key() == Qt.Key_Backspace:
                self.bs_count += 1
            elif key_event.key() == Qt.Key_Delete:
                self.dlt_count += 1

        return super().eventFilter(obj, event)

    def get_vector(self, user_input):

        sentence = self.register.get_sentence()
        typing_duration = self.typing_end_time - self.typing_start_time
        words_typed = len(user_input.split())
        wpm = (words_typed / typing_duration) * 60
        similarity, mismatched_words = self.register.lavenshtein_distance(sentence, user_input)
        letter_diff, letter_extra, letter_miss = self.register.mismatched_letters(mismatched_words)
        letter_diff_numeric = self.register.assign_numbers_to_alphabet(letter_diff)
        letter_extra_numeric = self.register.assign_numbers_to_alphabet(letter_extra)
        letter_miss_numeric = self.register.assign_numbers_to_alphabet(letter_miss)

        sorted_extra_numeric = sorted(letter_extra_numeric)
        sorted_miss_numeric = sorted(letter_miss_numeric)
        sorted_diff_numeric = sorted(letter_diff_numeric)

        extra_numeric = self.register.pair_to_one(sorted_extra_numeric)
        miss_numeric = self.register.pair_to_one(sorted_miss_numeric)
        diff_numeric = self.register.pair_to_one_diff(sorted_diff_numeric)

        extra_numeric += [0] * (10 - len(extra_numeric))
        miss_numeric += [0] * (10 - len(miss_numeric))
        diff_numeric += [0] * (10 - len(diff_numeric))

        vector = [self.bs_count, self.dlt_count, wpm, similarity]
        vector.extend(diff_numeric)
        vector.extend(extra_numeric)
        vector.extend(miss_numeric)


        self.typing_start_time = 0
        self.typing_end_time = 0

        return vector

    def evaluate(self, vector):

        for user in self.users:
            genuine_user_data = self.data.loc[self.data.User == user, \
                                'BackspaceCount':'Miss_9']
            imposter_data = self.data.loc[self.data.User != user, :]

            self.train = genuine_user_data[:3]
            self.test_genuine = genuine_user_data[3:]
            self.test_imposter = imposter_data.groupby("User"). \
                                     head(5).loc[:, 'BackspaceCount':'Miss_9']

            self.training()

            self.testing(vector)

    def training(self):
        self.mean_vector = self.train.mean().values
        self.std_vector = self.train.std().values
        dropping_indices = []
        for i in range(self.train.shape[0]):
            cur_score = euclidean(self.train.iloc[i].values,
                                  self.mean_vector)
            if (cur_score > 2 * self.std_vector).all() == True:
                dropping_indices.append(i)
        self.train = self.train.drop(self.train.index[dropping_indices])
        self.mean_vector = self.train.mean().values
        self.all_mean_vector.append(self.mean_vector)

    def testing(self, user_vector):
        for idx, vector in enumerate(self.all_mean_vector):
            self.manhattan_distance = cityblock(vector, user_vector)
            print(self.users[idx], self.manhattan_distance)
            if self.manhattan_distance < 70:
                self.user_label.setText(self.users[idx])
                return
            else:
                self.user_label.setText("This time I don't know who you are :(")


class RegisterPage(QMainWindow):
    def __init__(self, pandas=None):
        super(RegisterPage, self).__init__()

        self.typing_start_time = 0
        self.typing_end_time = 0

        self.input_count = 0
        self.dlt_count = 0
        self.bs_count = 0

        self.text_input = None
        self.actual_user = None
        self.username = None
        self.all_features = []
        loadUi("ui/register_page.ui", self)
        self.background_label.setGeometry(50, 50, 1320, 700)
        self.background_label.setPixmap(QPixmap("images/las.jpg"))
        self.back_button.setIcon(QtGui.QIcon("images/back.png"))
        self.back_button.clicked.connect(self.go_to_first_page)
        self.info_label.hide()
        self.text_lineEdit.hide()
        self.text_info_label.hide()
        self.count_label.hide()

        QApplication.instance().installEventFilter(self)

    def go_to_first_page(self):
        first_page = FirstPage()
        widget.addWidget(first_page)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def eventFilter(self, obj, event):

        if obj == self.username_lineEdit and event.type() == QEvent.KeyPress:
            key_event = event
            if key_event.key() == Qt.Key_Return:
                self.username = self.username_lineEdit.text()
                self.actual_user = self.register(self.username.lower())
                return True

        if len(self.all_features) < 10:
            if obj == self.text_lineEdit and event.type() == QEvent.KeyPress:
                key_event = event
                if self.typing_start_time == 0:
                    self.typing_start_time = time.time()
                if key_event.key() == Qt.Key_Return:
                    self.typing_end_time = time.time()
                    self.main()
                    return True
                elif key_event.key() == Qt.Key_Backspace:
                    self.bs_count += 1
                elif key_event.key() == Qt.Key_Delete:
                    self.dlt_count += 1

        else:
            self.text_lineEdit.hide()
            self.text_info_label.hide()
            self.info_label.setText("Thank you! Now you can go back to the main window")

        return super().eventFilter(obj, event)

    def check_value_in_csv(self, target_value):
        if not os.path.exists('mistakes_features_all.csv'):
            with open('mistakes_features_all.csv', 'w', newline='') as new_file:
                pass

        with open('mistakes_features_all.csv', 'r', newline='') as csvfile:
            csv_reader = csv.reader(csvfile)
            headers = next(csv_reader, None)
            if headers is None:
                return False

            for row in csv_reader:
                if target_value in row:
                    return True
        return False

    def register(self, username):
        if self.check_value_in_csv(username):
            self.username_info_label.setText("Username for identify is taken!")
        else:
            self.username_info_label.setStyleSheet("color: rgb(153, 255, 153)")
            self.username_info_label.setText("Correct username")
            self.info_label.show()
            self.text_lineEdit.show()
            self.text_info_label.show()
            self.label_5.hide()
            self.username_lineEdit.hide()
            self.text_lineEdit.setFocus()
            self.count_label.show()

        return username

    def get_sentence(self):
        with open('text.txt') as f:
            sentences = f.read().split('\n')
            sentence = random.choice(sentences)
        return sentence

    def lavenshtein_distance(self, given_text, input_text, threshold=1):
        given_words = given_text.split()
        input_words = input_text.split()
        length = len(input_words)

        similarity_matrix = np.zeros(length)
        mismatched_words = []

        if len(given_words) == len(input_words):
            for i in range(length):
                distance = Levenshtein.distance(given_words[i], input_words[i])
                similarity = 1 - distance / max(len(given_words[i]), len(input_words[i]))
                similarity_matrix[i] = similarity

                if similarity < threshold:
                    mismatched_words.append((given_words[i], input_words[i]))

            if similarity_matrix.size == 0:
                total_similarity = 0
            else:
                total_similarity = np.nanmean(similarity_matrix)

        else:
            total_similarity = 0

        return total_similarity, mismatched_words

    def assign_numbers_to_alphabet(self, letter_to_number_mapping):
        alphabet = 'abcdefghijklmnopqrstuvwxyz '
        letter_to_number = {}

        for i, letter in enumerate(alphabet, 1):
            letter_to_number[letter] = i

        letter_numeric = [
            (
                letter_to_number.get(ref_letter, 0),
                letter_to_number.get(user_letter, 0)
            )
            for ref_letter, user_letter in letter_to_number_mapping
        ]

        return letter_numeric

    def mismatched_letters(self, mismatched_words):
        letter_diff = []
        letter_extra = []
        letter_miss = []

        for reference_word, user_word in mismatched_words:
            differ = difflib.Differ()
            diff_result = list(differ.compare(reference_word, user_word))

            if len(reference_word) > len(user_word):
                for item in diff_result:
                    if item.startswith('- '):
                        letter_miss.append((item[2:], ''))

            elif len(user_word) > len(reference_word):
                for item in diff_result:
                    if item.startswith('+ '):
                        letter_extra.append(('', item[2:]))

            else:
                for i in range(len(reference_word)):
                    if reference_word[i] != user_word[i]:
                        letter_diff.append((reference_word[i], user_word[i]))

        return letter_diff, letter_extra, letter_miss

    def pair_to_one(self, letter):
        new_letter = []
        for a, b in letter:
            new_letter.append(a - b)

        return (new_letter)

    def pair_to_one_diff(self, letter):
        new_letter = []
        for a, b in letter:
            new_a = a * 100
            new = new_a + b
            new_letter.append(new)

        return new_letter

    def main(self):
        self.username_info_label.hide()
        self.count_label.setText(f"Number of trial: {len(self.all_features) + 1}")
        self.text_input = self.text_lineEdit.text()

        sentence = self.get_sentence()
        typing_duration = self.typing_end_time - self.typing_start_time
        words_typed = len(self.text_input.split())
        wpm = (words_typed / typing_duration) * 60
        similarity, mismatched_words = self.lavenshtein_distance(sentence, self.text_input)
        letter_diff, letter_extra, letter_miss = self.mismatched_letters(mismatched_words)
        letter_diff_numeric = self.assign_numbers_to_alphabet(letter_diff)
        letter_extra_numeric = self.assign_numbers_to_alphabet(letter_extra)
        letter_miss_numeric = self.assign_numbers_to_alphabet(letter_miss)

        sorted_extra_numeric = sorted(letter_extra_numeric)
        sorted_miss_numeric = sorted(letter_miss_numeric)
        sorted_diff_numeric = sorted(letter_diff_numeric)

        extra_numeric = self.pair_to_one(sorted_extra_numeric)
        miss_numeric = self.pair_to_one(sorted_miss_numeric)
        diff_numeric = self.pair_to_one_diff(sorted_diff_numeric)

        extra_numeric += [0] * (10 - len(extra_numeric))
        miss_numeric += [0] * (10 - len(miss_numeric))
        diff_numeric += [0] * (10 - len(diff_numeric))

        if similarity != 0:

            features = [self.actual_user, self.bs_count, self.dlt_count, wpm, similarity]
            features.extend(diff_numeric)
            features.extend(extra_numeric)
            features.extend(miss_numeric)

            self.all_features.append(features)

            with open('mistakes_features_all.csv', 'a', newline='') as csv_file:
                writer = csv.writer(csv_file)

                file_is_empty = csv_file.tell() == 0

                if file_is_empty:
                    writer.writerow(['User', 'BackspaceCount', 'DeleteCount', 'WPM', 'Similarity'] +
                                    [f'Diff_{i}' for i in range(len(diff_numeric))] +
                                    [f'Extra_{i}' for i in range(len(extra_numeric))] +
                                    [f'Miss_{i}' for i in range(len(miss_numeric))])

                writer.writerow(features)

        self.bs_count = 0
        self.dlt_count = 0
        self.typing_start_time = 0
        self.typing_end_time = 0
        self.text_lineEdit.clear()


app = QApplication(sys.argv)
app.setApplicationName("Keystroke Biometric System")
widget = QtWidgets.QStackedWidget()
widget.setWindowIcon(QtGui.QIcon('images/icon.png'))

first_page = FirstPage()
widget.addWidget(first_page)
widget.show()

try:
    sys.exit(app.exec_())
except:
    print("Exiting")
