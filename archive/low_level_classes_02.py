import constants
import numpy as np
import initial
import raise_exceptions


# class Volume:
#     def __init__(self):
#         self.value = round((constants.max_volume + constants.min_volume) / 2)
#         self.trend = (-1)**np.random.binomial(1, 0.5)


# class Step:
#     def __init__(self, sizes=None, trends=None,
#                  current_indices=None, previous_indices=None,
#                  difficulty_level=None):
#         self.difficulty_level = difficulty_level
#
#         if sizes is not None:
#             self.sizes = sizes # [None] * constants.max_chord_size
#         elif current_indices is not None and previous_indices is not None:
#             self.sizes = current_indices - previous_indices
#         else:
#             self.set_step_size(difficulty_level)
#
#         if trends is not None:
#             self.trends = np.array(trends)
#         elif current_indices is not None and previous_indices is not None:
#             self.trends = np.sign(self.sizes)
#         # if sizes is not None:
#         #     self.initialize_with_sizes(sizes)
#         # self.trends =  [(-1) ** np.random.binomial(1, 0.5)] * chord_size
#         # self.trend = self.trend + \
#         #     [np.nan] * (constants.max_chord_size - chord_size)
#
#     def set_step_size(self, difficulty_level):
#         # self.sizes = np.random.choice(
#         #     np.arange(constants.max_step_size+1), question.chord.sizes,
#         #     p=constants.levels.step_size[difficulty_level, :])
#         pass
#         # if 0 > np.min(question.step.size) or question.step.size > 7:
#         #     print('step size too big or too small')


# class Chord:
#     def __init__(self, indices=None, names=None, numbers=None):
#         self.size = None
#         self.indices = None
#         self.names = None
#         self.numbers = None
#         if indices is not None:
#             self.initialize_with_indices(indices)
#         elif names is not None:
#             self.initialize_with_names(names)
#         elif numbers is not None:
#             self.initialize_with_numbers(numbers)
#         self.range = np.max(self.indices) - np.min(self.indices) +1
#
#     def initialize_with_indices(self, indices):
#         self.indices = np.array(indices)
#         self.size = len(indices)
#         self.numbers = constants.note_numbers_C_to_C[indices]
#         self.names = [constants.note_names_major_C_scale[number % 12] for number in self.numbers]
#
#     def initialize_with_numbers(self, numbers):
#         self.numbers = np.array(numbers)
#         self.size = len(numbers)
#         self.indices = np.in1d(
#             constants.note_numbers_C_to_C,
#             numbers).nonzero()[0]
#         self.names = [constants.note_names_major_C_scale[number % 12] for number in self.numbers]
#
#     def initialize_with_names(self, names):
#         self.names = names
#         self.size = len(names)
#         self.numbers = [constants.name_to_number_dictionary[name] for name in names]
#         self.numbers = np.array(self.numbers)
#         self.indices = np.in1d(
#             constants.note_numbers_C_to_C,
#             self.numbers).nonzero()[0]


# class Response:
#     # class Flag:
#     #     def __init__(self):
#     #         self.repeat = True
#     #         # self.termination = False
#     #         self.correct = None
#     #         self.reveal = None
#
#     class Time:
#         def __init__(self, number_of_notes):
#             # a, b, c, d = constants.set_abcd(number_of_notes=number_of_notes)
#             # x = a - c * (b-a) / (d-c)
#             self.raw = None
#             self.autoregressive = None # constants.optimal_response_time
#
#     def __init__(self, number_of_notes):
#         self.text = 'C'
#         self.type = 'repeat'
#         # self.flag = self.Flag()
#         self.time = self.Time(number_of_notes=number_of_notes)
#
#
# class Attributes:
#     def __init__(self, request_response,
#                  error_state=initial.error_state,
#                  level=initial.level.total
#                  ):
#         self.error_state = error_state
#         self.request_response = request_response
#

