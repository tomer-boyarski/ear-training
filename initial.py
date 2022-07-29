import numpy as np
import constants
import os.path
# from low_level_classes_02 import *
# index = -1
import pickle
error_state = 'No Recent Errors'
# chord = Chord(indices=[7])
# level = constants.levels.step_size.shape[0] * \
#         constants.levels.chord_size.shape[0] - 1


class Level:
    def __init__(self, user):
        if user is None:
            self.step_size = 0
            self.number_of_notes = 0
            self.intervals = 0
            self.total = 0
        elif user == 'tomer':
            self.step_size = None
            self.number_of_notes = None
            self.intervals = None
            self.total = 97
            file_name = 'users\\' + user + '\\level.pkl'
            if os.path.isfile(file_name):
                with open(file_name, 'rb') as inp:
                    self.total = pickle.load(inp)
        # self.total = self.number_of_notes * \
        #              constants.levels.intervals.shape[0] * \
        #              constants.levels.step_size.shape[0] + \
        #              self.intervals * \
        #              constants.levels.step_size.shape[0] + \
        #              self.step_size


def get_level(user):
    return Level(user=user)

# error_state = False


def indices(keys):
    if keys == 'white':
        indices = [7]
    elif keys == 'all':
        indices = [12]
    return indices


# number_of_notes = len(indices)
# indices = np.array(indices)
