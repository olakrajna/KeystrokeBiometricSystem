#keystroke_ManhattanFiltered.py

from scipy.spatial.distance import euclidean, cityblock
import numpy as np
np.set_printoptions(suppress = True)
import pandas
from EER import evaluateEER
from pynput import keyboard
import time
import csv
import os

class ManhattanFilteredDetector:
#just the training() function changes, rest all remains same.

    def __init__(self, subjects):
        self.user_scores = []
        self.imposter_scores = []
        self.mean_vector = []
        self.all_mean_vector = []
        self.subjects = subjects
        self.odleglosci = []
        self.take_key = []
        self.cleaned_list = []
        self.your_time = []
        self.all_time = []
        self.user_index = []
        self.count = 0
        self.first_key_pressed_hold = False
        self.last_key_release_time = 0
        self.last_key_press_time = 0
        self.counter = 0
        self.t = 0
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
            keyboard.Key.down, keyboard.Key.menu, keyboard.Key.media_play_pause
        }
        self.deleted_key = {keyboard.Key.backspace}
        self.username = None


    def on_key_release(self, key):

        if hasattr(key, 'char') or hasattr(key, 'name'):
            self.last_key_release_time = time.time()

        if not self.first_key_pressed_hold:
            return False

        time_taken = round(time.time() - self.t, 5)
        if key not in self.ignored_key:
            self.take_key.append(str(key))
            self.your_time.append(float(time_taken))
        return False

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

    def on_key_press(self, key):
        self.first_key_pressed_hold = True
        if key not in self.ignored_key:
            if hasattr(key, 'char') or hasattr(key, 'name') and self.last_key_release_time != 0:
                time_difference_ud = round(time.time() - self.last_key_release_time, 5)
                if key.char != '.':
                    self.your_time.append(time_difference_ud)

            if hasattr(key, 'char') or hasattr(key, 'name') and key.char is not None:
                time_difference_dd = round(time.time() - self.last_key_press_time, 5)
                self.last_key_press_time = time.time()
                self.counter += 1
                if key.char != '.':
                    self.your_time.append(time_difference_dd)
        return False

    def main(self):
        print('------------------------------------------------------------------------')
        print("System do zbieranie danych na temat charakterystyki używania klawiatury")
        print('------------------------------------------------------------------------')
        print("-------------------------------Logowanie--------------------------------")

        self.username = input("Nazwa użytkownika: ").lower()

        while self.username not in subjects:
            self.username = input("Niepoprawna nazwa użytkownia. Wpisz ponownie: ").lower()

        take_user_index = np.where(subjects == self.username)[0].tolist()
        self.user_index = int(take_user_index[0])

        con_password = '.ego1buslix'

        print('Hasło: ')
        while True:
            self.t = time.time()

            with keyboard.Listener(on_press=self.on_key_press, on_release=self.on_key_release) as listener:
                listener.join()

            self.cleaned_list = [element.replace("'", '') for element in self.take_key]
            result = ''.join(self.cleaned_list)
            print(result)
            if len(con_password) == len(result):
                if con_password == result:
                    if len(self.your_time) != 31:
                        print(f"Niestety musisz powtórzyć próbę wpisania hasła.")
                        print(len(self.your_time))
                        self.last_key_release_time = 0
                        self.last_key_press_time = 0
                        self.take_key = []
                        self.cleaned_list = []
                        self.your_time = []
                        self.counter = 0
                    else:
                        print("Hasło poprawne! Trwa weryfikacja.")
                        self.evaluate(self.your_time)

                        print("Dziękuje, koniec sesji na dziś :)")

            elif result != con_password[:len(result)]:
                print(f"Niestety musisz powtórzyć próbę wpisania hasła. Popełniłeś błąd!")
                self.last_key_release_time = 0
                self.last_key_press_time = 0
                self.counter = 0
                self.take_key = []
                self.cleaned_list = []
                self.your_time = []
    def training(self):
        self.mean_vector = self.train.mean().values
        self.std_vector = self.train.std().values
        dropping_indices = []
        for i in range(self.train.shape[0]):
            cur_score = euclidean(self.train.iloc[i].values, 
                                   self.mean_vector)
            if (cur_score > 3*self.std_vector).all() == True:
                dropping_indices.append(i)
        self.train = self.train.drop(self.train.index[dropping_indices])
        self.mean_vector = self.train.mean().values
        self.all_mean_vector.append(self.mean_vector)
        print(self.all_mean_vector)
        #
        # print(self.all_mean_vector)
        # print(len(self.all_mean_vector))

    def testing(self, wektor_2):
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

        if len(self.all_mean_vector) == len(subjects):
            vector_1 = self.all_mean_vector[self.user_index]
            print(wektor_2)
        # for i in (self.all_mean_vector):
            self.odleglosc = cityblock(wektor_2, vector_1)

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

    def evaluate(self, wektor):
        eers = []
 
        for subject in subjects:
            genuine_user_data = data.loc[data.subject == subject, \
                                         "H.percent":"H.x"]
            imposter_data = data.loc[data.subject != subject, :]
            # print(subjects)

            self.train = genuine_user_data[:25]
            self.test_genuine = genuine_user_data[25:]
            self.test_imposter = imposter_data.groupby("subject"). \
                                 head(5).loc[:, "H.percent":"H.x"]

            self.training()
            self.testing(wektor)
            eers.append(evaluateEER(self.user_scores, \
                                     self.imposter_scores))

        return np.mean(eers)


path = "keystroke4.csv"
data = pandas.read_csv(path)
subjects = data["subject"].unique()
print ("average EER for Manhattan Filtered detector:")
print(ManhattanFilteredDetector(subjects).main())
