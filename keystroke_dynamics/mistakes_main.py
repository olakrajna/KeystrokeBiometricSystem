import difflib
import random
import numpy as np
import Levenshtein
from pynput.keyboard import Key, Listener
import time
import csv

bs_count = 0  # Licznik naciśnięć Backspace
dlt_count = 0  # Licznik naciśnięć Delete
typing_count = 0  # Licznik ilości prób
all_features = []

def get_sentence():
    with open('text.txt') as f:
        sentences = f.read().split('\n')
        sentence = random.choice(sentences)
    return sentence

def lavenshtein_distance(given_text, input_text, threshold=1):
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

    total_similarity = np.mean(similarity_matrix)

    return total_similarity, mismatched_words


sentence = get_sentence()

typing_start_time = 0
typing_end_time = 0


def on_press(key):
    global bs_count, dlt_count, typing_start_time
    if key == Key.esc:
        return False
    if key == Key.backspace:
        bs_count += 1
    elif key == Key.delete:
        dlt_count += 1
    elif typing_start_time == 0:
        typing_start_time = time.time()


def assign_numbers_to_alphabet(letter_to_number_mapping):
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

def mismatched_letters(mismatched_words):
    letter_diff = []
    letter_extra =[]
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

def pair_to_one(letter):
    new_letter = []
    for a, b in letter:
        new_letter.append(a-b)

    return(new_letter)

def pair_to_one_diff(letter):
    new_letter = []
    for a, b in letter:
        new_a = a * 100
        new = str(new_a + b).zfill(4)
        new_letter.append(new)

    return new_letter

listener = Listener(on_press=on_press)
listener.start()

while typing_count < 3:
    try:
        sentence = get_sentence()
        print(sentence)
        text = input("Rewrite text above: ")
        typing_end_time = time.time()
        typing_duration = typing_end_time - typing_start_time
        words_typed = len(text.split())
        wpm = (words_typed / typing_duration) * 60
        similarity, mismatched_words = lavenshtein_distance(sentence, text)
        letter_diff, letter_extra, letter_miss = mismatched_letters(mismatched_words)
        letter_diff_numeric = assign_numbers_to_alphabet(letter_diff)
        letter_extra_numeric = assign_numbers_to_alphabet(letter_extra)
        letter_miss_numeric = assign_numbers_to_alphabet(letter_miss)

        extra_numeric = pair_to_one(letter_extra_numeric)
        miss_numeric = pair_to_one(letter_miss_numeric)
        diff_numeric = pair_to_one_diff(letter_diff_numeric)

        max_len_extra = len(extra_numeric)
        max_len_miss = len(miss_numeric)
        max_len_diff = len(diff_numeric)

        extra_numeric += [0] * (10 - len(extra_numeric))
        miss_numeric += [0] * (10 - len(miss_numeric))
        diff_numeric += [0] * (10 - len(diff_numeric))

        features = [bs_count, dlt_count, wpm, similarity]
        features.extend(diff_numeric)
        features.extend(extra_numeric)
        features.extend(miss_numeric)

        all_features.append(features)

        typing_count += 1
        bs_count = 0
        dlt_count = 0
        typing_start_time = 0

    except KeyboardInterrupt:
        listener.stop()
        listener.join()

print(all_features)