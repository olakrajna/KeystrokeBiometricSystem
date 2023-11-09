from pynput.keyboard import Key, Listener
import random

bs_count = 0  # Licznik naciśnięć Backspace
dlt_count = 0  # Licznik naciśnięć Delete`

def on_press(key):
    global bs_count, dlt_count

    if key == Key.esc:
        return False

    if key == Key.backspace:
        bs_count += 1
    elif key == Key.delete:
        dlt_count += 1

    sentence = get_sentence()
    print('Backspace count: {0}, Delete count: {1}'.format(bs_count, dlt_count))
    print('Random Sentence: {0}'.format(sentence))

def get_sentence():
    with open('tests.txt') as f:
        sentences = f.read().split('\n')
        sentence = random.choice(sentences)
    return sentence

with Listener(on_press=on_press) as listener:
    listener.join()
