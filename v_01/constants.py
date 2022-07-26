import numpy as np
import rtmidi
from types import SimpleNamespace


mo = rtmidi.MidiOut()
mo.open_port(0)
mo = mo


class WhiteNotes():
    def __init__(self):
        numbers = np.array([60, 62, 64, 65, 67, 69, 71, 72])
        numbers = np.unique(np.concatenate((numbers - 12, numbers)))
        self.numbers = numbers
        self.names = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
        self.indices = np.arange(len(numbers))


white_note = WhiteNotes()
# note_numbers_C_to_C = np.array([60, 62, 64, 65, 67, 69, 71, 72])
# note_numbers_C_to_C = np.unique(np.concatenate((note_numbers_C_to_C - 12, note_numbers_C_to_C)))
note_names_chromatic_C_scale = ['C', 'CS', 'D', 'DS', 'E', 'F', 'FS', 'G', 'GS', 'A', 'AS', 'B']
# note_names_major_C_scale = ['C', 'D', 'E', 'F', 'G', 'A', 'B']

number_to_name_dictionary = {60: 'C', 62: 'D', 64: 'E',
                             65: 'F', 67: 'G', 69: 'A',
                             71: 'B'}
name_to_number_dictionary = {v: k for k, v in number_to_name_dictionary.items()}

note_names_chromatic_C_scale = note_names_chromatic_C_scale
my_velocity = 127
lower_bound_response_time = 1.5
upper_bound_response_time = 2.5

level_change_with_very_short_response_time = 10
level_change_with_very_long_response_time = 10

optimal_response_time = (lower_bound_response_time +
                         upper_bound_response_time) / 2
bpm = 60  # beats per minutes
quarter_note_time = 60 / bpm
minimal_response_time = 0.7
probability_of_same_step_direction = 0.75
probability_of_same_volume_change_direction = 0.75
max_volume = 96  # 127
min_volume = 64
max_step_size = 8
volume_change = (max_volume - min_volume) / 4
# volume_change = 1
number_of_step_size_sub_levels = 10
last_sample_weight = 0.25


def calculate_step_size_difficulty_levels(n_cols):
    n_sub_levels = number_of_step_size_sub_levels
    n_rows = (n_cols - 1) * n_sub_levels
    levels = np.zeros((n_rows, n_cols))
    for i in range(n_cols - 1):
        levels[i * n_sub_levels:i * n_sub_levels + n_sub_levels, 1:(1 + i)] = 1
        levels[i * n_sub_levels:i * n_sub_levels + n_sub_levels, 1 + i] = np.linspace(0, 0.9, n_sub_levels)
    final_level = np.ones(n_cols)
    levels[:, 0] = levels[:, 1] / 3
    levels = np.vstack([levels, final_level])
    levels = levels[10:, :]
    levels = levels / np.sum(levels, axis=1, keepdims=True)
    return levels


def calculate_chord_size_difficulty_levels_old():
    chord_size_levels = np.linspace(1, 0, 11)
    chord_size_levels = chord_size_levels.reshape(len(chord_size_levels), 1)
    chord_size_levels = np.hstack((chord_size_levels, chord_size_levels[::-1]))
    return chord_size_levels


def calculate_chord_size_difficulty_levels():
    chord_size_levels = np.eye(5)
    return chord_size_levels


def calculate_interval_levels():
    x = np.zeros((1, 7))
    x[0, 1] = 1
    for col_ind in [2, 3, 4, 6, 5, 0]:
        for i in range(10):
            y = np.copy(x[-1, :])
            y[col_ind] += 0.1
            x = np.vstack((x, y))
    x = x / np.sum(x, axis=1, keepdims=True)
    return x


class ClassOfLevels:
    class Max:
        def __init__(self, levels):
            self.step_size = levels.step_size.shape[0]-1
            self.number_of_notes = levels.number_of_notes.shape[0]-1
            self.intervals = levels.intervals.shape[0]-1


    def __init__(self):
        self.step_size = calculate_step_size_difficulty_levels(n_cols=8)
        self.number_of_notes = calculate_chord_size_difficulty_levels()
        self.intervals = calculate_interval_levels()
        self.max = self.Max(self)


levels = ClassOfLevels()
# myObject = myClass()
# max_level = levels.step_size.shape[0] * \
#             levels.number_of_notes.shape[0] - 1


def max_level(step_size=None,
              intervals=None,
              number_of_notes=None,
              step_size_level=None,
              number_of_notes_level=None,
              interval_level=None):
    max_level = 1
    if step_size is None and step_size_level is None:
        max_level = max_level * levels.max.step_size
    if intervals is None and interval_level is None and \
            (number_of_notes is None or number_of_notes > 1):
        max_level = max_level * levels.max.intervals
    if number_of_notes is None and number_of_notes_level is None:
        max_level = max_level * levels.max.number_of_notes
    max_level = max_level - 1
    if max_level == 0:
        max_level = None
    return max_level



max_chord_size = levels.number_of_notes.shape[1]

reveal = False
show_level = True


def set_abcd(number_of_notes):
    if number_of_notes == 1:
        very_short_response_time = 1.2
    elif number_of_notes == 2:
        very_short_response_time = 2.1
    very_long_response_time = very_short_response_time * 8
    a = very_short_response_time
    b = very_long_response_time
    c = level_change_with_very_short_response_time
    d = -level_change_with_very_long_response_time
    return a, b, c, d


number_of_step_size_levels = levels.step_size.shape[0]
level_decrease_upon_error = number_of_step_size_sub_levels
