import rtmidi.midiconstants
import numpy as np
import time
from termcolor import colored

mo = rtmidi.MidiOut()
mo.open_port(0)
my_velocity = 127
note_names_C_to_B = np.array(['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'])
note_names_C_to_B = np.array(['C', 'CS', 'D', 'DS', 'E', 'F', 'FS', 'G', 'GS', 'A', 'AS', 'B'])


Termination_Flag = False
number_of_notes_to_play = 2
probability_not_to_hear_new_note = 0.1


def necessary_number_of_consecutive_successes_func(step_size):
    if step_size == 0:
        necessary_number_of_consecutive_successes = 1
    else:
        necessary_number_of_consecutive_successes = 10 * step_size
    return necessary_number_of_consecutive_successes


# necessary_number_of_consecutive_successes = \
#     lambda x, y: np.log(x) / np.log(1-1/y)
bass = 55
note_numbers_in_display_order = np.array([0, 7, 4, 12, 5, 2, 9, 3, 8, 6, 11, 1])

# all_note_name = ['G','G#','A','A#', 'B', 'C','C#','D', 'D#','E','F','F#']
# note_numbers_C_to_B = np.arange(60, 60+12)


note_numbers_in_display_order = bass + note_numbers_in_display_order

number_of_consecutive_successes = 0

step_size = 0
previous_note = 60

necessary_number_of_consecutive_successes = \
    necessary_number_of_consecutive_successes_func(step_size)


while not Termination_Flag:
    CorrectAnswer = False
    new_note_number = previous_note + np.random.randint(-step_size,step_size+1)
    while new_note_number < 55 or new_note_number > 68:
        new_note_number = previous_note + np.random.randint(-step_size, step_size + 1)
    new_note_name = note_names_C_to_B[new_note_number % 12]
    while not CorrectAnswer and not Termination_Flag:
        mo.send_message([rtmidi.midiconstants.NOTE_ON, new_note_number, my_velocity])
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
        mo.send_message([rtmidi.midiconstants.NOTE_OFF, new_note_number, my_velocity])
        identified_note = identified_note.upper()
        if identified_note == new_note_name: # or idendtified_note == str(note_number-notes_numbers_to_play_now[0]+1):
            CorrectAnswer = True
            print(colored("Good :-)", 'blue'))

            number_of_consecutive_successes += 1
            if number_of_consecutive_successes >= \
                    necessary_number_of_consecutive_successes:
                print("Let's try more notes")
                step_size += 1
                necessary_number_of_consecutive_successes = \
                        necessary_number_of_consecutive_successes_func(step_size)
                number_of_consecutive_successes = 0
        elif identified_note == 'REPEAT':
            continue
        elif identified_note == 'END':
            Termination_Flag = True
        elif identified_note == 'REVEAL':
            number_of_consecutive_successes = 0
            print('The correct answer is ' + new_note_name)
            CorrectAnswer = True
        else:
            for error_note in [80, 86, 92]:
                mo.send_message([rtmidi.midiconstants.NOTE_ON, error_note, my_velocity])
            time.sleep(0.1)
            for error_note in [80, 86, 92]:
                mo.send_message([rtmidi.midiconstants.NOTE_OFF, error_note, my_velocity])
            print(colored("Try Again",'red'))
            # print("your options are " + note_names_to_play_now)
            number_of_consecutive_successes = 0
    previous_note = new_note_number

mo.close_port()
