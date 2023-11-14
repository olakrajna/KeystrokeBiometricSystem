from pynput import keyboard
import time
import csv

take_key = []
cleaned_list = []
your_time = []
all_time = []
first_key_pressed = False
count = 0
up_time = 0
last_key_release_time = 0


ignored_key = {
    keyboard.Key.shift,keyboard.Key.shift_l,keyboard.Key.shift_r, keyboard.Key.enter, keyboard.Key.backspace,
    keyboard.Key.space, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r, keyboard.Key.delete, keyboard.Key.caps_lock,
    keyboard.Key.tab, keyboard.Key.alt_l, keyboard.Key.alt_r, keyboard.Key.esc, keyboard.Key.f1, keyboard.Key.f2,
    keyboard.Key.f3, keyboard.Key.f4,keyboard.Key.f5,keyboard.Key.f6, keyboard.Key.f7,keyboard.Key.f8,keyboard.Key.f9,
    keyboard.Key.f10,keyboard.Key.f11, keyboard.Key.f12, keyboard.Key.f13, keyboard.Key.f14, keyboard.Key.f15,
    keyboard.Key.f16, keyboard.Key.f17, keyboard.Key.f18, keyboard.Key.f19, keyboard.Key.f20, keyboard.Key.f21,
    keyboard.Key.f22, keyboard.Key.f23, keyboard.Key.f24, keyboard.Key.print_screen, keyboard.Key.scroll_lock,
    keyboard.Key.pause, keyboard.Key.insert, keyboard.Key.home, keyboard.Key.end, keyboard.Key.page_up,
    keyboard.Key.page_down, keyboard.Key.num_lock, keyboard.Key.left, keyboard.Key.right, keyboard.Key.up,
    keyboard.Key.down, keyboard.Key.menu, keyboard.Key.media_play_pause
}

deleted_key = {keyboard.Key.backspace}
con_password = '%ego1Buslix'

header = ['subject','rep','H.percent', 'UD.percent.e', 'H.e', 'UD.e.g', 'H.g', 'UD.g.o', 'H.o', 'UD.o.one',
          'H.one', 'UD.one.B', 'H.B', 'UD.B.u' , 'H.u' , 'UD.u.s', 'H.s', 'UD.s.l', 'H.l', 'UD.l.i',  'H.i', 'UD.i.x'
    ,'H.x', 'UD.x.Return']

def on_key_release(key):
    global first_key_pressed
    global up_time
    global last_key_release_time
    if hasattr(key, 'char'):
        last_key_release_time = time.time()

    if not first_key_pressed:
        return False

    up_time = time.time()
    time_taken = round(time.time() - t, 5)
    if key not in ignored_key:
        take_key.append(str(key))
        your_time.append(float(time_taken))

    print(your_time)

    if key == keyboard.Key.backspace:
        if len(take_key) > 0 and len(your_time) > 0:
            take_key.pop()
            your_time.pop()
            print('usunięto')

    print("The key", key, "is pressed for", time_taken, 'seconds')

    return False

def check_value_in_csv(target_value):
    with open('keystroke.csv', 'r', newline='') as csvfile:
        csv_reader = csv.reader(csvfile)

        headers = next(csv_reader, None)
        if headers is None:
            return False

        for row in csv_reader:
            if target_value in row:
                return True
    return False

def get_last_session_index_for_subject(target_subject):
    last_session_index = None

    with open('keystroke.csv', 'r', newline='') as csvfile:
        csv_reader = csv.DictReader(csvfile)

        for row in csv_reader:
            if row['subject'] == target_subject:
                last_session_index = row['session_index']

    return int(last_session_index)


def on_key_press(key):
    global last_key_release_time
    global first_key_pressed
    if hasattr(key, 'char') and last_key_release_time != 0:
        time_difference = round(time.time() - last_key_release_time, 5)
        your_time.append(time_difference)
        print(f"Time between key release and key press: {time_difference} seconds")
        print(f"Pressed key: {key.char}")

    first_key_pressed = True
    return False


print('------------------------------------------------------------------------')
print("System do zbieranie danych na temat charakterystyki używania klawiatury")
print('------------------------------------------------------------------------')

print("Jeśli pierwszy raz korzystasz z systemu wpisz nową nazwe użytkownika, jeśli nie wpisz starą.")
username = input("Nazwa użytkownika: ").lower()

if check_value_in_csv(username):
    print("Wprowadzono poprawną nazwę użytkownika!")
    session_index = get_last_session_index_for_subject(username) + 1
    print(f'Rozpoczynasz sesje numer {session_index}')
else:
    print(f'Witaj w naszym systemie, {username}!.')
    session_index = 1


con_password = '%ego1Buslix'

print('Teraz przejdziemy do fazy testowej, proszę o wpisanie 30 razy ciągu znaków "%ego1Buslix".')
print("Jeśli popełnisz błąd, będziesz poproszony o wpisanie tego ciągu od początku")
while True:
    t = time.time()
    down_time = time.time()

    with keyboard.Listener(on_press=on_key_press, on_release=on_key_release) as listener:
        listener.join()


    cleaned_list = [element.replace("'", '') for element in take_key]
    result = ''.join(cleaned_list)
    print(result)
    if result != con_password[:len(result)]:
        print("Masz błąd! Wpisz ciąg od początku: '%ego1Buslix' ")
        # take_key = []
        # cleaned_list = []
        # your_time = []

    if len(con_password) == len(result):
        if con_password == result:
            print("Hasło poprawne! Możesz przejść dalej.")
            count += 1

            print(f'Próba: {count}')

            your_time.insert(0, username)
            your_time.insert(1, session_index)
            your_time.insert(2, count)
            your_time.insert(-1, 0)
            print(your_time)
            with open('keystroke.csv', 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(header)

                writer.writerow(your_time)

            take_key = []
            cleaned_list = []
            your_time = []

            if count == 10:
                print("Dziękuje, koniec sesji na dziś :)")
                break
        else:
            print("Hasło niepoprawne. Spróbuj ponowne.")
            take_key = []
            cleaned_list = []
            your_time = []

