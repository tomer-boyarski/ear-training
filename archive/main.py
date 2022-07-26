import rtmidi.midiconstants
import numpy as np
import time


mo = rtmidi.MidiOut()
mo.open_port(0)
my_velocity = 60
note_names_G_to_F_sharp = np.array(['G', 'G#', 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#'])
note_names_C_to_B = np.array(['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'])

# with mo:

# start = 54

# # rtmidi.midiconstants.CHANNEL_VOLUME.as_integer_ratio()
# for note in range(start, start+14):
#     print(note_names[note % 12])
#     mo.send_message([rtmidi.midiconstants.NOTE_ON, note, my_velocity])
#     time.sleep(1.5)
#     mo.send_message([rtmidi.midiconstants.NOTE_OFF, note, my_velocity])

# my_notes = [60,64,67,72]

# for note in my_notes:
#     mo.send_message([rtmidi.midiconstants.NOTE_ON, note, my_velocity])
#
# time.sleep(5)
#
# for note in my_notes:
#     mo.send_message([rtmidi.midiconstants.NOTE_OFF, note, my_velocity])
#
# time.sleep(0.1)

Flag = False
number_of_notes_to_play = 2
probability_not_to_hear_new_note = 0.05


def necessary_number_of_consecutive_successes_func(
        probability_not_to_hear_new_note,
        number_of_notes_to_play, note_numbers_in_display_order):
    necessary_number_of_consecutive_successes = \
        np.log(probability_not_to_hear_new_note) / \
        np.log(1 - 1 / number_of_notes_to_play)
    necessary_number_of_consecutive_successes = \
        int(np.ceil(necessary_number_of_consecutive_successes))
    print('try to get ' +
          str(necessary_number_of_consecutive_successes) +
          ' consecutive correct answers')
    notes_numbers_to_play_now = note_numbers_in_display_order[:number_of_notes_to_play]
    note_indices = note_numbers_in_display_order[:number_of_notes_to_play] % 12
    print('your notes are ' + ', '.join(note_names_C_to_B[note_indices]))
    return necessary_number_of_consecutive_successes, notes_numbers_to_play_now


# necessary_number_of_consecutive_successes = \
#     lambda x, y: np.log(x) / np.log(1-1/y)
bass = 55
note_numbers_in_display_order = np.array([0, 7, 4, 12, 5, 2, 9, 3, 8, 6, 11, 1])

# all_note_name = ['G','G#','A','A#', 'B', 'C','C#','D', 'D#','E','F','F#']
# note_numbers_C_to_B = np.arange(60, 60+12)


note_numbers_in_display_order = bass + note_numbers_in_display_order

number_of_consecutive_successes = 0


necessary_number_of_consecutive_successes, \
    notes_numbers_to_play_now = \
    necessary_number_of_consecutive_successes_func(
        probability_not_to_hear_new_note,
        number_of_notes_to_play,
        note_numbers_in_display_order)


while not Flag:
    CorrectAnswer = False
    note_number = np.random.choice(notes_numbers_to_play_now, 1)
    while not CorrectAnswer and not Flag:
        mo.send_message([rtmidi.midiconstants.NOTE_ON, note_number, my_velocity])
        time.sleep(1.5)
        mo.send_message([rtmidi.midiconstants.NOTE_OFF, note_number, my_velocity])
        identified_note = input("Identify Note:")
        if identified_note == note_names_C_to_B[note_number[0] % 12]:
            CorrectAnswer = True
            print("Good :-)")

            number_of_consecutive_successes += 1
            if number_of_consecutive_successes >=            \
                    np.log(probability_not_to_hear_new_note) \
                    / np.log(1-1/number_of_notes_to_play):
                print("Let's try more notes")
                number_of_notes_to_play += 1
                necessary_number_of_consecutive_successes = \
                    necessary_number_of_consecutive_successes_func(
                        probability_not_to_hear_new_note,
                        number_of_notes_to_play)
        elif identified_note == 'end':
            Flag = True
        else:
            print("Try Again")
            number_of_consecutive_successes = 0


mo.close_port()
