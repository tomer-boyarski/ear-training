import rtmidi.midiconstants
import numpy as np
import time


mo = rtmidi.MidiOut()
mo.open_port(0)
my_velocity = 127
chord_duration = 0.7
allowed_soprano_jump = 7
allowed_bass_jump = allowed_soprano_jump
key_root_number = 60
progression_length = 8
all_chord_root_numbers = np.array([60, 65, 67])
all_chord_root_numbers = np.array([60, 65, 67])
note_names_C_to_B = np.array(['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'])

def number_to_name(note_number):
    note_name = note_names_C_to_B[note_number % 12]
    return note_name


root_note_name = number_to_name(key_root_number)
print('key of ' + root_note_name)


def invert_chord(root_of_chord, inversion):
    if inversion == 0:
        inverted_chord = np.array([root_of_chord,
                                   root_of_chord + 4,
                                   root_of_chord + 7])
    elif inversion == 1:
        inverted_chord = np.array([root_of_chord + 4,
                                   root_of_chord + 7,
                                   root_of_chord + 12])
    elif inversion == 2:
        inverted_chord = np.array([root_of_chord + 7,
                                   root_of_chord + 12,
                                   root_of_chord + 16])
    return inverted_chord


def move_chord_up_and_down_octaves(inverted_chord):
    inverted_chord = np.tile(inverted_chord, (5, 1))
    change_octaves = 12 * np.transpose(np.tile(np.array([-2, -1, 0, 1, 2]), (3, 1)))
    same_chord_diff_octaves = inverted_chord + change_octaves
    return same_chord_diff_octaves

def choose_octave(previous_chord, same_chord_diff_octaves, allowed_soprano_jump, allowed_bass_jump):
    mask = np.ones(np.size(same_chord_diff_octaves, 0), dtype=bool)
    for i in range(np.size(same_chord_diff_octaves, 0)):
        if same_chord_diff_octaves[i, -1] > previous_chord[-1] + allowed_soprano_jump or \
                same_chord_diff_octaves[i, 0] < previous_chord[0] - allowed_bass_jump:
            mask[i] = False
    same_chord_diff_octaves = same_chord_diff_octaves[mask,]
    row_ind = np.random.randint(0, np.size(same_chord_diff_octaves, 0))
    chord = same_chord_diff_octaves[row_ind,]
    return chord

    #     inverted_chord = same_chord_diff_octaves[i,]

    # return inverted_chord

# inversion = np.random.randint(0, 3, 1)
# play_chord(60, 0)
# play_chord(60, 1)
# play_chord(60, 2)


def play_chord(chord):
    for note in chord:
        mo.send_message([rtmidi.midiconstants.NOTE_ON, note, my_velocity])
    time.sleep(chord_duration)
    for note in chord:
        mo.send_message([rtmidi.midiconstants.NOTE_OFF, note, my_velocity])

def play_progression():
    for i in range(progression_length):
        play_chord(progression_numbers[i, :])



def tmp_func_name(root, previous_chord):
    inverted_chord = invert_chord(root, 0)
    same_chord_diff_octaves = move_chord_up_and_down_octaves(inverted_chord)
    chord = choose_octave(previous_chord, same_chord_diff_octaves, allowed_soprano_jump, allowed_bass_jump)
    # play_chord(chord)
    return chord

def get_progression(key_root_number):
    chord = tmp_func_name(key_root_number, [60, 69])
    progression_numbers = chord
    progression_names = []
    progression_names.append(number_to_name(key_root_number))
    for _ in range(progression_length - 2):
        chord_root = np.random.choice(all_chord_root_numbers)
        # add chord name to list
        progression_names.append(number_to_name(chord_root))
        chord = tmp_func_name(chord_root, chord)
        # add chord numbers to array
        progression_numbers = np.vstack((progression_numbers, chord))
    chord = tmp_func_name(key_root_number, [key_root_number, 69])
    # add chord name to list
    progression_names.append(number_to_name(key_root_number))
    # add chord numbers to array
    progression_numbers = np.vstack((progression_numbers, chord))
    # print(progression_numbers)
    return progression_numbers, progression_names


Termination_Flag = False
while not Termination_Flag:
    CorrectAnswer = False
    progression_numbers, progression_names = get_progression(key_root_number)
    progression_names_str = ""
    progression_names_str = progression_names_str.join(progression_names)
    print(progression_names_str)
    while not CorrectAnswer and not Termination_Flag:
        play_progression()
        progression_identification = input("Identify progression:")

        if progression_identification == progression_names_str:
            CorrectAnswer = True
        elif progression_identification == 'end':
            Termination_Flag = True
        elif progression_identification == 'reveal':
            number_of_consecutive_successes = 0
            print('The correct answer is ' + progression_names_str)
            CorrectAnswer = True
        else:
            print("Try Again")
    Termination_Flag = True


# note_names_G_to_F_sharp = np.array(['G', 'G#', 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#'])
#
#
# Termination_Flag = False
# number_of_notes_to_play = 2
# probability_not_to_hear_new_note = 0.1
#
#
# def necessary_number_of_consecutive_successes_func():
#     necessary_number_of_consecutive_successes = \
#         np.log(probability_not_to_hear_new_note) / \
#         np.log(1 - 1 / number_of_notes_to_play)
#     necessary_number_of_consecutive_successes = \
#         int(np.ceil(necessary_number_of_consecutive_successes))
#     print('try to get ' +
#           str(necessary_number_of_consecutive_successes) +
#           ' consecutive correct answers')
#     notes_numbers_to_play_now = note_numbers_in_display_order[:number_of_notes_to_play]
#     note_indices = note_numbers_in_display_order[:number_of_notes_to_play] % 12
#     print('your notes are ' + ', '.join(note_names_C_to_B[note_indices]))
#     return necessary_number_of_consecutive_successes, notes_numbers_to_play_now
#
#
# # necessary_number_of_consecutive_successes = \
# #     lambda x, y: np.log(x) / np.log(1-1/y)
# bass = 55
# note_numbers_in_display_order = np.array([0, 7, 4, 12, 5, 2, 9, 3, 8, 6, 11, 1])
#
# # all_note_name = ['G','G#','A','A#', 'B', 'C','C#','D', 'D#','E','F','F#']
# # note_numbers_C_to_B = np.arange(60, 60+12)
#
#
# note_numbers_in_display_order = bass + note_numbers_in_display_order
#
# number_of_consecutive_successes = 0
#
#
# necessary_number_of_consecutive_successes, \
#     notes_numbers_to_play_now = \
#     necessary_number_of_consecutive_successes_func()
#
#
# while not Termination_Flag:
#     CorrectAnswer = False
#     note_number = np.random.choice(notes_numbers_to_play_now, 1)
#     note_name = note_names_C_to_B[note_number[0] % 12]
#     while not CorrectAnswer and not Termination_Flag:
#         mo.send_message([rtmidi.midiconstants.NOTE_ON, note_number, my_velocity])
#         time.sleep(1.5)
#         mo.send_message([rtmidi.midiconstants.NOTE_OFF, note_number, my_velocity])
#         identified_note = input("Identify Note:")
#         if identified_note == note_name:
#             CorrectAnswer = True
#             print("Good :-)")
#
#             number_of_consecutive_successes += 1
#             if number_of_consecutive_successes >=            \
#                     np.log(probability_not_to_hear_new_note) \
#                     / np.log(1-1/number_of_notes_to_play):
#                 print("Let's try more notes")
#                 number_of_notes_to_play += 1
#                 necessary_number_of_consecutive_successes, \
#                     notes_numbers_to_play_now = \
#                     necessary_number_of_consecutive_successes_func()
#         elif identified_note == 'end':
#             Termination_Flag = True
#         elif identified_note == 'reveal':
#             number_of_consecutive_successes = 0
#             print('The correct answer is ' + note_name)
#             CorrectAnswer = True
#         else:
#             print("Try Again")
#             number_of_consecutive_successes = 0
#
#
mo.close_port()
