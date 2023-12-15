import difflib
import random
import typing

import Levenshtein
import numpy as np
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
from EER import evaluateEER
from scipy.spatial.distance import euclidean, cityblock
import pandas as pd


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
        self.register_button.clicked.connect(self.go_to_register_page)
        self.identify_button.clicked.connect(self.go_to_identify_page)
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


class IdentifyPage(QMainWindow):
    def __init__(self):
        super(IdentifyPage, self).__init__()
        self.user_input = None
        loadUi("ui/identify_page.ui", self)
        self.background_label.setGeometry(50, 50, 1320, 700)
        self.background_label.setPixmap(QPixmap("images/las.jpg"))
        self.back_button.setIcon(QtGui.QIcon("images/back.png"))
        self.back_button.clicked.connect(self.go_to_first_page)

        QApplication.instance().installEventFilter(self)

    def go_to_first_page(self):
        first_page = FirstPage()
        widget.addWidget(first_page)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def eventFilter(self, obj, event):
        if obj == self.text_lineEdit and event.type() == QEvent.KeyPress:
            key_event = event
            if key_event.key() == Qt.Key_Return:
                self.user_input = self.text_lineEdit.text()
                self.info_label.setText("Thank you! I think you are...")
                self.check(self.user_input)
                self.text_lineEdit.hide()
                self.text_label.hide()
                return True


        return super().eventFilter(obj, event)

    def check(self, input):
        print(input)


class RegisterPage(QMainWindow):
    def __init__(self, pandas=None):
        super(RegisterPage, self).__init__()
        self.typing_start_time = None
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
                if key_event.key() == Qt.Key_Return:
                    self.main()
                    return True
        else:
            self.info_label.hide()
            self.text_lineEdit.hide()
            self.text_info_label.hide()
            self.username_info_label.setText("Thank you! Now you can go back to the main window")

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
            self.info_label.setText("Please enter text below 10 times. After each trail click 'Enter'")
            self.info_label.show()
            self.text_lineEdit.show()
            self.text_info_label.show()
            self.label_5.hide()
            self.username_lineEdit.hide()
            self.text_lineEdit.setFocus()


        return username

    def get_sentence(self):
        with open('text.txt') as f:
            sentences = f.read().split('\n')
            sentence = random.choice(sentences)
        return sentence

    def lavenshtein_distance(self, given_text, input_text, threshold=1):
        given_words = given_text.split()
        input_words = input_text.split()

        min_length = min(len(given_words), len(input_words))
        given_words = given_words[:min_length]
        input_words = input_words[:min_length]

        similarity_matrix = np.zeros(min_length)
        mismatched_words = []

        for i in range(min_length):
            distance = Levenshtein.distance(given_words[i], input_words[i])
            similarity = 1 - distance / max(len(given_words[i]), len(input_words[i]))
            similarity_matrix[i] = similarity

            if similarity < threshold:
                mismatched_words.append((given_words[i], input_words[i]))

        if similarity_matrix.size == 0:
            total_similarity = 0
        else:
            total_similarity = np.nanmean(similarity_matrix)

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
            new = str(new_a + b).zfill(4)
            new_letter.append(new)

        return new_letter

    def main(self):
        self.text_input = self.text_lineEdit.text()
        # self.typing_start_time = 0
        # self.typing_end_time = 0

        sentence = self.get_sentence()
        # typing_end_time = time.time()
        # typing_duration = self.typing_end_time - self.typing_start_time
        # words_typed = len(self.text_input.split())
        # wpm = (words_typed / typing_duration) * 60
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

        # features = [self.actual_user, self.input_count, self.bs_count, self.dlt_count, wpm, similarity]
        features = [self.actual_user, self.input_count, self.bs_count, self.dlt_count, similarity]
        features.extend(diff_numeric)
        features.extend(extra_numeric)
        features.extend(miss_numeric)

        self.all_features.append(features)

        self.input_count += 1
        self.bs_count = 0
        self.dlt_count = 0
        self.typing_start_time = 0

        with open('mistakes_features_all.csv', 'a', newline='') as csv_file:
            writer = csv.writer(csv_file)

            file_is_empty = csv_file.tell() == 0

            if file_is_empty:
                writer.writerow(['User', 'Number of trial', 'BackspaceCount', 'DeleteCount', 'Similarity'] +
                                [f'Diff_{i}' for i in range(len(diff_numeric))] +
                                [f'Extra_{i}' for i in range(len(extra_numeric))] +
                                [f'Miss_{i}' for i in range(len(miss_numeric))])

            writer.writerow(features)
        self.text_lineEdit.clear()

    def get_users(self):
        file_path = "mistakes_features_all.csv"

        # Check if the file exists
        if not os.path.isfile(file_path):
            print(f"Error: File '{file_path}' not found.")
            return None

        try:
            # Read the CSV file
            data = pd.read_csv(file_path)
            users = data["User"].unique()

            return users
        except Exception as e:
            print(f"Error: An error occurred while reading the file - {e}")
            return None

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
        print(self.all_mean_vector)
        #
        # print(self.all_mean_vector)
        # print(len(self.all_mean_vector))

    def testing(self, vector_2):
        users = self.get_users()
        for i in range(self.test_genuine.shape[0]):
            cur_score = cityblock(self.test_genuine.iloc[i].values, \
                                  self.mean_vector)
            self.user_scores.append(cur_score)

        for i in range(self.test_imposter.shape[0]):
            cur_score = cityblock(self.test_imposter.iloc[i].values, \
                                  self.mean_vector)
            self.imposter_scores.append(cur_score)
            # print(self.test_imposter.iloc[i].values)
            # print('----------------------------------------------------')

        # print("To jest wektor tej osoby", self.all_mean_vector[self.user_index])

        if len(self.all_mean_vector) == len(users):
            vector_1 = self.all_mean_vector[self.user_index]
            print(vector_2)
            # for i in (self.all_mean_vector):
            self.odleglosc = cityblock(vector_2, vector_1)

            if self.odleglosc <= 2.1:
                print("Jest to ta sama osoba. Próba logowania się powiodła")
            else:
                print("Próba logowania nie powiodła się")

            #         print('index manh', self.min_value_index_manhattan)
            #         print(min(self.odleglosci))
            print(self.odleglosc)

        # for i in (self.all_mean_vector):
        #     odleglosc_eukl = np.linalg.norm(i - wektor_2)
        #     if len(self.all_mean_vector) == len(subjects):
        #         self.odleglosci_euklidesowe.append(odleglosc_eukl)
        #         self.min_value_index_euklides = self.odleglosci_euklidesowe.index(min(self.odleglosci_euklidesowe))
        #         # print('index euk', self.min_value_index_euklides)
        #         # print(min(self.odleglosci_euklidesowe))
        # print('EUK', self.odleglosci_euklidesowe)

    def evaluate(self, vector):
        users = self.get_users()
        eers = []

        for user in self.users:
            genuine_user_data = self.data.loc[self.data.user == user, \
                                "H.percent":"H.x"]
            imposter_data = self.data.loc[self.data.user != user, :]
            # print(subjects)

            self.train = genuine_user_data[:25]
            self.test_genuine = genuine_user_data[25:]
            self.test_imposter = imposter_data.groupby("user"). \
                                     head(5).loc[:, "H.percent":"H.x"]

            self.training()
            self.testing(vector)
            eers.append(evaluateEER(self.user_scores, \
                                    self.imposter_scores))

        return np.mean(eers)




app = QApplication(sys.argv)
widget = QtWidgets.QStackedWidget()
first_page = FirstPage()
widget.addWidget(first_page)
widget.show()

try:
    sys.exit(app.exec_())
except:
    print("Exiting")
