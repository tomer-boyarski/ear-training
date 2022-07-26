import numpy as np
import constants
# from low_level_classes_02 import *
# index = -1
error_state = 'No Recent Errors'
# chord = Chord(indices=[7])
# level = constants.levels.step_size.shape[0] * \
#         constants.levels.chord_size.shape[0] - 1


class Level:
    def __init__(self):
        self.step_size = constants.levels.step_size.shape[0] - 1
        self.number_of_notes = constants.levels.number_of_notes.shape[0] - 1
        self.intervals = constants.levels.intervals.shape[0]-1
        self.step_size = 0
        self.number_of_notes = 0
        self.intervals = 0
        self.total = self.number_of_notes * \
                     constants.levels.intervals.shape[0] * \
                     constants.levels.step_size.shape[0] + \
                     self.intervals * \
                     constants.levels.step_size.shape[0] + \
                     self.step_size

level = Level()


# error_state = False
indices = [7]
number_of_notes = len(indices)
# indices = np.array(indices)
