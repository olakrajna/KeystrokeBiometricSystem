from pynput import keyboard
import time
import sqlite3
import re
engine = sqlite3.connect("database.db")

cursor = engine.cursor()
cursor.execute("SELECT username FROM users")
usernames = cursor.fetchall()
existing_usernames = [user[0] for user in usernames]
take_key = []
cleaned_list = []
your_time = []
all_time = []
first_key_pressed = False  # Dodana flaga
count = 0
ignored_key = {keyboard.Key.shift, keyboard.Key.caps_lock, keyboard.Key.enter, keyboard.Key.backspace}
deleted_key = {keyboard.Key.backspace}
def sprawdz_haslo(haslo):
    if len(haslo) < 12:
        return False

    if not re.search(r'[A-Z]', haslo) or not re.search(r'\d', haslo) or not re.search(r'[#%$!?]', haslo):
        return False

    return True


def on_key_release(key):
    global first_key_pressed
    if not first_key_pressed:
        return False  # Ignoruj pierwszy release, aby rozpocząć pomiar od wciśnięcia pierwszego przycisku

    time_taken = round(time.time() - t, 5)
    if key not in ignored_key:
        take_key.append(str(key))
        your_time.append(float(time_taken))

    if key == keyboard.Key.backspace:
        if len(take_key) > 0 and len(your_time) > 0:
            take_key.pop()
            your_time.pop()
            print('usunieto')

    print("The key", key, "is pressed for", time_taken, 'seconds')

    return False

def on_key_press(key):
    global first_key_pressed
    first_key_pressed = True
    return False

username = input("Hej, podaj nazwę użytkownika: ")
choose_another_name = True

while username in existing_usernames:
    username = input("Zajęta nazwa użytkownika, wprowadź nową: ")

print("Wprowadzono poprawną nazwę użytkownika!")
password = input("Podaj hasło (min. 12 znaków, duża litera, znak specjalny, liczba: ")
while sprawdz_haslo(password) == False:
    print("Hasło nie spełnia wymagań")
    password = input("Podaj hasło (min. 12 znaków, duża litera, znak specjalny, liczba: ")
else:
    print("Okej")

con_password = input("Wprowadź hasło jeszcze raz: ")

while con_password != password:
    con_password = input("Hasło wpisane niepoprawnie! Wprowadź hasło jeszcze raz: ")

print('Teraz przejdziemy do fazy testowej, proszę o wpisanie hasła 30 razy w celu wygenerowania wzorca biometrycznego')

while True:
    t = time.time()

    with keyboard.Listener(on_press=on_key_press, on_release=on_key_release) as listener:
        listener.join()

    cleaned_list = [element.replace("'", '') for element in take_key]
    result = ''.join(cleaned_list)
    print(result)


    if result != con_password[:len(result)]:
        print("Masz błąd!")


    if len(con_password) == len(result):
        if con_password == result:
            print("Hasło poprawne! Możesz przejść dalej.")
            count += 1
            print(f'Próba: {count}')
            total_time = round(sum(your_time), 5)
            print("Suma czasów:", total_time)
            all_time.append(total_time)
            take_key = []
            cleaned_list = []
            your_time = []
            average_time = sum(all_time)/len(all_time)
        else:
            print("Hasło niepoprawne. Spróbuj ponownie.")
            take_key = []
            cleaned_list = []
            your_time = []

