import random
import numpy as np
import Levenshtein
from pynput.keyboard import Key
from pynput.keyboard import Listener
import time
import csv

# Inicjalizacja pliku CSV
typing_results_csv_file = 'typing_results.csv'
mismatched_words_csv_file = 'mismatched_words.csv'
typing_fieldnames = ['Number of sample', 'Backspace Count', 'Delete Count', 'Typing Duration (seconds)', 'WPM',
                     'Sentence Similarity']
mismatched_fieldnames = ['Number of sample', 'Mismatched reference letter', 'Mismatched user letter']

bs_count = 0  # Licznik naciśnięć Backspace
dlt_count = 0  # Licznik naciśnięć Delete
typing_count = 0  # Licznik ilości prób


def get_sentence():
    with open('tests.txt') as f:
        sentences = f.read().split('\n')
        sentence = random.choice(sentences)
    return sentence


def lavenshtein_distance(given_text, input_text, threshold=1):
    given_words = given_text.split()
    input_words = input_text.split()

    # Upewnij się, że liczba słów jest taka sama
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


def mismatched_letters(mismatched_words):
    for reference_word, user_word in mismatched_words:
        letter_diff = []

        # Porównaj litera po literze i identyfikuj różnice
        for i in range(min(len(reference_word), len(user_word))):
            if reference_word[i] != user_word[i]:
                letter_diff.append((reference_word[i], user_word[i]))

        # Jeśli jedno słowo jest dłuższe, zidentyfikuj dodatkowe litery
        if len(reference_word) > len(user_word):
            additional_letters = reference_word[len(user_word):]
            letter_diff.extend([(letter, '') for letter in additional_letters])

        elif len(user_word) > len(reference_word):
            missing_letters = user_word[len(reference_word):]
            letter_diff.extend([('', letter) for letter in missing_letters])

        return letter_diff


listener = Listener(on_press=on_press)
listener.start()

with open(typing_results_csv_file, mode='w', newline='') as typing_file:
    typing_writer = csv.DictWriter(typing_file, fieldnames=typing_fieldnames)

    # Write headers to the typing results file
    typing_writer.writeheader()

    # Open the mismatched words CSV file in write mode
    with open(mismatched_words_csv_file, mode='w', newline='') as mismatched_file:
        mismatched_writer = csv.DictWriter(mismatched_file, fieldnames=mismatched_fieldnames)

        # Write headers to the mismatched words file
        mismatched_writer.writeheader()

        while typing_count < 10:
            try:
                print(sentence)
                text = input("Rewrite text above: ")
                typing_end_time = time.time()
                typing_duration = typing_end_time - typing_start_time
                words_typed = len(text.split())
                wpm = (words_typed / typing_duration) * 60  # Calculate WPM

                similarity, mismatched_words = lavenshtein_distance(sentence, text)
                letter_diff = mismatched_letters(mismatched_words)

                # Write typing results to the main CSV file
                typing_writer.writerow({
                    'Number of sample': typing_count + 1,
                    'Backspace Count': bs_count,
                    'Delete Count': dlt_count,
                    'Typing Duration (seconds)': typing_duration,
                    'WPM': wpm,
                    'Sentence Similarity': similarity
                })

                # Write mismatched words to the mismatched words CSV file
                for ref_letter, user_letter in letter_diff:
                    mismatched_writer.writerow({
                        'Number of sample': typing_count + 1,
                        'Mismatched reference letter': ref_letter,
                        'Mismatched user letter': user_letter
                    })

                typing_count += 1
            except KeyboardInterrupt:
                listener.stop()
                listener.join()
