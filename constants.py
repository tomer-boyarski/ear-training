import numpy as np
import rtmidi
from types import SimpleNamespace


mo = rtmidi.MidiOut()
mo.open_port(0)


class Keys:
    class White:
        def __init__(self):
            numbers = np.array([60, 62, 64, 65, 67, 69, 71, 72])
            numbers = np.unique(np.concatenate((numbers - 12, numbers)))
            numbers = np.unique(np. concatenate((numbers, numbers + 24)))
            self.numbers = numbers
            self.names = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
            self.indices = np.arange(len(numbers))

    class All:
        def __init__(self):
            self.numbers = np.arange(60-12, 73)
            self.numbers = np.unique(np.concatenate((self.numbers, self.numbers + 24)))
            self.indices = np.arange(len(self.numbers))
            self.names = ['C', 'CS', 'D', 'DS', 'E', 'F', 'FS', 'G', 'GS', 'A', 'AS', 'B']

    def __init__(self):
        self.white = self.White()
        self.all = self.All()
# note_numbers_C_to_C = np.array([60, 62, 64, 65, 67, 69, 71, 72])
# note_numbers_C_to_C = np.unique(np.concatenate((note_numbers_C_to_C - 12, note_numbers_C_to_C)))


keys = Keys()
number_to_name_dictionary = {60: 'C', 62: 'D', 64: 'E',
                             65: 'F', 67: 'G', 69: 'A',
                             71: 'B'}
name_to_number_dictionary = {v: k for k, v in number_to_name_dictionary.items()}

note_on = 144
note_off = 128

# note_names_chromatic_C_scale = note_names_chromatic_C_scale
my_velocity = 127
lower_bound_response_time = 1.5
upper_bound_response_time = 2.5

level_change_with_very_short_response_time = 10
level_change_with_very_long_response_time = \
    -level_change_with_very_short_response_time
linear_level_decrease_upon_error = level_change_with_very_long_response_time


optimal_response_time = (lower_bound_response_time +
                         upper_bound_response_time) / 2
bpm = 60  # beats per minutes
quarter_note_time = 60 / bpm
minimal_response_time = 0.7
probability_of_same_step_direction = 0.75
probability_of_same_volume_change_direction = 0.75
max_volume = 96  # 127
min_volume = 64


def max_step_size(keys):
    if keys == 'white':
        max_step_size = 8
    elif keys == 'all':
        max_step_size = 12
    return max_step_size


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
    chord_size_levels = np.eye(10)
    return chord_size_levels


def calculate_interval_levels(keys):
    if keys == 'white':
        x = np.zeros((1, 7))
        x[0, 1] = 1
        for col_ind in [2, 3, 4, 6, 5, 0]:
            for i in range(10):
                y = np.copy(x[-1, :])
                y[col_ind] += 0.1
                x = np.vstack((x, y))
    elif keys == 'all':
        # 0: small 2nd, 1: large 2nd, 2: small 3rd, 3: large 3rd
        # 4: perfect 4th, 5: tritone, 6: perfect 5th,
        # 7: small 6th, 8: large 6th, 9: small 7th, 10: large 7th, 11: octave
        x = np.zeros((1, 12))
        x[0, 3] = 1
        for col_ind in [2, 4, 6, 8, 11, 7, 5, 9, 10, 1, 0]:
            for i in range(10):
                y = np.copy(x[-1, :])
                y[col_ind] += 0.1
                x = np.vstack((x, y))
    x = x / np.sum(x, axis=1, keepdims=True)
    return x


class ClassOfLevels:
    class Change:
        class Multiplicative:
            def __init__(self):
                self.decrease = 4
                self.increase = self.decrease

        class Additive:
            def __init__(self):
                self.increase = 1
                self.decrease = -self.increase
                self.decrease_with_error = self.decrease * 4

        def __init__(self):
            self.multiplicative = self.Multiplicative()
            self.additive = self.Additive()

    class Max:
        class StepSize:
            def __init__(self, levels):
                self.white = levels.step_size.white.shape[0]-1
                self.all = levels.step_size.all.shape[0]-1

        class Intervals:
            def __init__(self, levels):
                self.white = levels.intervals.white.shape[0] - 1
                self.all = levels.intervals.all.shape[0] - 1

        def __init__(self, levels):
            self.step_size = self.StepSize(levels)
            self.number_of_notes = levels.number_of_notes.shape[0]-1
            self.intervals = self.Intervals(levels)

    class StepSize:
        def __init__(self):
            self.white = calculate_step_size_difficulty_levels(n_cols=8)
            self.all = calculate_step_size_difficulty_levels(n_cols=12)

    class Intervals:
        def __init__(self):
            self.white = calculate_interval_levels(keys='white')
            self.all = calculate_interval_levels(keys='all')

    def __init__(self):
        self.number_of_notes = calculate_chord_size_difficulty_levels()
        self.step_size = self.StepSize()
        self.intervals = self.Intervals()
        self.max = self.Max(self)
        self.change = self.Change()


levels = ClassOfLevels()

max_chord_size = levels.number_of_notes.shape[1]

reveal = False
show_total_level = True
show_phase = False
show_step_options = True

def set_abcd(number_of_notes):
    if number_of_notes == 1:
        very_short_response_time = 1.2
    elif number_of_notes == 2:
        very_short_response_time = 2
    elif number_of_notes == 3:
        very_short_response_time = 2.5
    very_long_response_time = very_short_response_time * 6
    a = very_short_response_time
    b = very_long_response_time
    c = levels.change.additive.increase
    d = levels.change.additive.decrease
    return a, b, c, d


# number_of_step_size_levels = levels.step_size.shape[0]

