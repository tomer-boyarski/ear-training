import rtmidi.midiconstants
import numpy as np
import time
from termcolor import colored

mo = rtmidi.MidiOut()
mo.open_port(0)
my_velocity = 127
note_names_G_to_F_sharp = np.array(['G', 'G#', 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#'])
note_names_C_to_B = np.array(['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'])

Termination_Flag = False
number_of_notes_to_play = 2
probability_not_to_hear_new_note = 0.1


def necessary_number_of_consecutive_successes_func():
    necessary_number_of_consecutive_successes = \
        np.log(probability_not_to_hear_new_note) / \
        np.log(1 - 1 / number_of_notes_to_play)
    necessary_number_of_consecutive_successes = \
        int(np.ceil(necessary_number_of_consecutive_successes))
    notes_numbers_to_play_now = note_numbers_in_display_order[:number_of_notes_to_play]
    for note in [55+24,55+4+24,55+7+24,55+12+24]:
        mo.send_message([rtmidi.midiconstants.NOTE_ON, note, my_velocity])
    time.sleep(0.5)
    for note in [55 + 24, 55 + 4 + 24, 55 + 7 + 24, 55 + 12 + 24]:
        mo.send_message([rtmidi.midiconstants.NOTE_OFF, note, my_velocity])
    for note in np.sort(notes_numbers_to_play_now):
        mo.send_message([rtmidi.midiconstants.NOTE_ON, note, my_velocity])
        time.sleep(1)
        mo.send_message([rtmidi.midiconstants.NOTE_OFF, note, my_velocity])
    time.sleep(2)
    note_indices = note_numbers_in_display_order[:number_of_notes_to_play] % 12
    note_names_to_play_now = note_names_C_to_B[note_indices]
    note_names_to_play_now = ', '.join(note_names_to_play_now)
    return necessary_number_of_consecutive_successes, \
           notes_numbers_to_play_now, \
           note_names_to_play_now


# necessary_number_of_consecutive_successes = \
#     lambda x, y: np.log(x) / np.log(1-1/y)
bass = 55
note_numbers_in_display_order = np.array([0, 7, 4, 12, 5, 2, 9, 3, 8, 6, 11, 1])

# all_note_name = ['G','G#','A','A#', 'B', 'C','C#','D', 'D#','E','F','F#']
# note_numbers_C_to_B = np.arange(60, 60+12)


note_numbers_in_display_order = bass + note_numbers_in_display_order

number_of_consecutive_successes = 0

necessary_number_of_consecutive_successes, \
           notes_numbers_to_play_now, \
           note_names_to_play_now = \
    necessary_number_of_consecutive_successes_func()

while not Termination_Flag:
    CorrectAnswer = False
    note_number = np.random.choice(notes_numbers_to_play_now, 1)
    note_name = note_names_C_to_B[note_number[0] % 12]
    while not CorrectAnswer and not Termination_Flag:
        mo.send_message([rtmidi.midiconstants.NOTE_ON, note_number, my_velocity])
        print('your options are ' + note_names_to_play_now)
        print('You need ' +
              str(necessary_number_of_consecutive_successes) +
              ' consecutive correct answers to reach the next level')
        print('You have ' + str(number_of_consecutive_successes) +
              ' consecutive correct answers so far in this level')
        print('Try to get ' + str(necessary_number_of_consecutive_successes -
                                  number_of_consecutive_successes) +
              ' more consecutive correct answers')
        identified_note = input("Identify Note:")
        # time.sleep(1.5)
        mo.send_message([rtmidi.midiconstants.NOTE_OFF, note_number, my_velocity])
        identified_note = identified_note.upper()
        if identified_note == note_name: # or idendtified_note == str(note_number-notes_numbers_to_play_now[0]+1):
            CorrectAnswer = True
            print(colored("Good :-)", 'blue'))

            number_of_consecutive_successes += 1
            if number_of_consecutive_successes >= \
                    necessary_number_of_consecutive_successes:
                print("Let's try more notes")
                number_of_notes_to_play += 1
                necessary_number_of_consecutive_successes, \
                    notes_numbers_to_play_now, \
                    note_names_to_play_now = \
                        necessary_number_of_consecutive_successes_func()
                number_of_consecutive_successes = 0
        elif identified_note == 'REPEAT':
            continue
        elif identified_note == 'END':
            Termination_Flag = True
        elif identified_note == 'REVEAL':
            number_of_consecutive_successes = 0
            print('The correct answer is ' + note_name)
            CorrectAnswer = True
        else:
            for error_note in [80, 86, 92]:
                mo.send_message([rtmidi.midiconstants.NOTE_ON, error_note, my_velocity])
            time.sleep(0.1)
            for error_note in [80, 86, 92]:
                mo.send_message([rtmidi.midiconstants.NOTE_OFF, error_note, my_velocity])
            print(colored("Try Again",'red'))
            print("your options are " + note_names_to_play_now)
            number_of_consecutive_successes = 0

mo.close_port()
