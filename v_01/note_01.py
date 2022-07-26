import numpy as np
import constants


class Note:
    def __init__(self, question_list, index=None, name=None, number=None,
                 # step_size=None, step_trend=None
                 ):
        self.indices = None
        self.names = None
        self.numbers = None
        # self.step_size = None
        # self.step_trend = None
        self.raise_exceptions(index, name, number, step_size, step_trend)
        if index is not None:
            self.initialize_with_indices(index)
        elif name is not None:
            self.initialize_with_names(name)
        elif number is not None:
            self.initialize_with_numbers(number)

    @staticmethod
    def raise_exceptions(index, name, number, step_size, step_trend):
        note_attributes = {'index': index,
                           'name': name,
                           'number': number}
        note_attributes = {k: v for k, v in note_attributes.items() if v is not None}
        if len(note_attributes) > 1:
            my_str = ''.join([k + '=' + str(v) + ', ' for k, v in note_attributes.items()])
            my_str = my_str[:-2]
            raise Exception('Can not define note with the following attribute: ' +
                            my_str)
        step_attributes = {'step_size': step_size,
                           'step_trend': step_trend}
        step_attributes = {k: v for k, v in step_attributes.items() if v is not None}
        if len(note_attributes) >= 1 and len(step_attributes) >= 1:
            my_str_note_attributes = ''.join([k + '=' + str(v) + ', ' for k, v in note_attributes.items()])
            my_str_step_attributes = ''.join([k + '=' + str(v) + ', ' for k, v in step_attributes.items()])
            my_str = my_str_note_attributes + my_str_step_attributes
            my_str = my_str[:-2]
            raise Exception('Can not define note with the following attribute: ' +
                            my_str)


    def initialize_with_indices(self, indices):
        self.indices = np.array(indices)
        self.numbers = constants.note_numbers_C_to_C[indices]
        self.names = [constants.note_names_major_C_scale[number % 12] for number in self.numbers]

    def initialize_with_numbers(self, numbers):
        self.numbers = np.array(numbers)
        self.indices = np.in1d(
            constants.note_numbers_C_to_C,
            numbers).nonzero()[0]
        self.names = [constants.note_names_major_C_scale[number % 12] for number in self.numbers]

    def initialize_with_names(self, names):
        self.names = names
        self.numbers = [constants.name_to_number_dictionary[name] for name in names]
        self.numbers = np.array(self.numbers)
        self.indices = np.in1d(
            constants.note_numbers_C_to_C,
            self.numbers).nonzero()[0]
