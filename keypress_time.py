from pynput import keyboard
import time
import csv
import os

class KeyPressTime:
    def __init__(self):
        self.take_key = []
        self.cleaned_list = []
        self.your_time = []
        self.all_time = []
        self.count = 1
        self.first_key_pressed_hold = False
        self.last_key_release_time = 0
        self.last_key_press_time = 0
        self.counter = 0
        self.t = 0
        self.first_count_value = 0
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
        self.header = ['subject', 'session_index', 'rep', 'H.dot', 'UD.dot.e', 'DD.dot.e', 'H.e',
                  'UD.e.g', 'DD.e.g', 'H.g', 'UD.g.o', 'DD.g.o', 'H.o', 'UD.o.one', 'DD.o.one', 'H.one', 'UD.one.B',
                  'DD.one.B',
                  'H.B', 'UD.B.u', 'DD.B.u', 'H.u', 'UD.u.s', 'DD.u.s', 'H.s', 'UD.s.l', 'DD.s.l', 'H.l', 'UD.l.i',
                  'DD.l.i', 'H.i'
            , 'UD.i.x', 'DD.i.x', 'H.x']

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
            # print("H.", key, "is pressed for", time_taken, 'seconds')
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

    def get_last_session_index_for_subject(self, target_subject):
        last_session_index = None

        with open('keystroke4.csv', 'r', newline='') as csvfile:
            csv_reader = csv.DictReader(csvfile)

            for row in csv_reader:
                if row['subject'] == target_subject:
                    last_session_index = row['session_index']

        return int(last_session_index)

    def get_last_rep_for_subject(self, target_subject):
        last_rep = None

        with open('keystroke4.csv', 'r', newline='') as csvfile:
            csv_reader = csv.DictReader(csvfile)

            for row in csv_reader:
                if row['subject'] == target_subject:
                    last_rep = row['rep']
        return int(last_rep)

    def on_key_press(self, key):
        self.first_key_pressed_hold = True
        if key not in self.ignored_key:
            if hasattr(key, 'char') or hasattr(key, 'name') and self.last_key_release_time != 0:
                time_difference_ud = round(time.time() - self.last_key_release_time, 5)
                if key.char != '.':
                    self.your_time.append(time_difference_ud)
                    # print(f"UD.{key.char}: {time_difference_ud} seconds")
                # print(f"Pressed key: {key.char}")

            if hasattr(key, 'char') or hasattr(key, 'name') and key.char is not None:
                time_difference_dd = round(time.time() - self.last_key_press_time, 5)
                # print(f"DD.{key.char}: {time_difference_dd} seconds")
                # print(f"Pressed key: {key.char}")
                self.last_key_press_time = time.time()
                self.counter += 1
                # print(counter)
                if key.char != '.':
                    self.your_time.append(time_difference_dd)

        return False

    def login(self):
        username = input("Nazwa użytkownika: ").lower()

        if self.check_value_in_csv(username):
            print("Wprowadzono poprawną nazwę użytkownika!")
            self.session_index = self.get_last_session_index_for_subject(username) + 1
            print(f'Rozpoczynasz sesje numer {self.session_index}')
            self.count = self.get_last_rep_for_subject(username) + 1
            self.first_count_value = self.get_last_rep_for_subject(username) + 1
            print("Ostatnia twoja próba", self.get_last_rep_for_subject(username))
        else:
            print(f'Witaj w naszym systemie, {username}!.')
            self.session_index = 1
        return username


    def main(self):
        print('------------------------------------------------------------------------')
        print("System do zbieranie danych na temat charakterystyki używania klawiatury")
        print('------------------------------------------------------------------------')
        print("Wybirz, czy chcesz się zalogować do systemu czy utworzyć nowe konto:")
        # print("1. Utworzyć nowe konto")
        # print("2. Zaloguj się")
        # wybor = input("Wybór ")

        print("Jeśli pierwszy raz korzystasz z systemu wpisz nową nazwe użytkownika, jeśli nie wpisz starą.")

        self.username = self.login()

        con_password = '.ego1buslix'

        print('Teraz przejdziemy do fazy testowej, proszę o wpisanie 30 razy ciągu znaków ".ego1buslix".')
        print("Jeśli popełnisz błąd, będziesz poproszony o wpisanie tego ciągu od początku")
        print(f"Próba nr {self.count}!")
        while True:
            self.t = time.time()

            with keyboard.Listener(on_press=self.on_key_press, on_release=self.on_key_release) as listener:
                listener.join()

            self.cleaned_list = [element.replace("'", '') for element in self.take_key]
            result = ''.join(self.cleaned_list)
            print(result)

            if len(con_password) == len(result):
                if con_password == result:
                    self.your_time.insert(0, self.username)
                    self.your_time.insert(1, self.session_index)
                    self.your_time.insert(2, self.count)
                    if len(self.your_time) != len(self.header):
                        print(f"Niestety musisz powtórzyć próbę nr {self.count + 1}. System nie zarejestrował czasu.")
                    else:
                        self.count += 1
                        print("Hasło poprawne! Możesz przejść dalej.")
                        print(f'Rozpoczynasz próbe nr {self.count}!')
                        print(f"W tej sesji zostało Ci jeszcze {self.first_count_value + 30 - self.count} prób!go1 buslix.ego1buslix.ego1vysl.ego1buslix")
                        print(self.your_time)
                        with open('keystroke4.csv', 'a', newline='') as f:
                            writer = csv.writer(f)
                            if self.is_csv_empty('keystroke4.csv'):
                                writer.writerow(self.header)
                            writer.writerow(self.your_time)
                    self.last_key_release_time = 0
                    self.last_key_press_time = 0
                    self.take_key = []
                    self.cleaned_list = []
                    self.your_time = []
                    self.counter = 0

                    if self.count == self.first_count_value + 30:
                        print("Dziękuje, koniec sesji na dziś :)")
                        break
            elif result != con_password[:len(result)]:
                print(result)
                print(f"Niestety musisz powtórzyć próbę nr {self.count}. Popełniłeś błąd!")
                self.last_key_release_time = 0
                self.last_key_press_time = 0
                self.counter = 0
                self.take_key = []
                self.cleaned_list = []
                self.your_time = []

keypress = KeyPressTime()
keypress.main()