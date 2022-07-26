import numpy as np
import constants


class Note:
    def __init__(self, index=None, name=None, number=None,
                 interval=None, lower_note=None,
                 level=None):
        self.index = None
        self.name = None
        self.number = None

        self.raise_exceptions(index, name, number, interval, lower_note)
        if index is not None:
            self.initialize_with_index(index)
        elif name is not None:
            self.initialize_with_name(name)
        elif number is not None:
            self.initialize_with_number(number)

    @staticmethod
    def raise_exceptions(index, name, number, interval, lower_note):
        note_attributes = {'index': index,
                           'name': name,
                           'number': number}
        note_attributes = {k: v for k, v in note_attributes.items() if v is not None}
        if len(note_attributes) > 1:
            my_str = ''.join([k + '=' + str(v) + ', ' for k, v in note_attributes.items()])
            my_str = my_str[:-2]
            raise Exception('Can not define note with the following attribute: ' +
                            my_str)
        relative_attributes = {'interval': interval,
                               'lower_note': lower_note}
        relative_attributes = {k: v for k, v in relative_attributes.items() if v is not None}
        if len(note_attributes) == 1 and len(relative_attributes) > 0:
            merged_attributes = {**note_attributes, **relative_attributes}
            my_str = ''.join([k + '=' + str(v) + ', ' for k, v in merged_attributes.items()])
            my_str = my_str[:-2]
            raise Exception('Can not define note with the following attribute: ' +
                            my_str)

    def initialize_with_index(self, index):
        self.index = index
        self.number = constants.white_note.number[index]
        self.name = constants.note_names_chromatic_C_scale[int(self.number % 12)]

    def initialize_with_number(self, number):
        self.number = number
        self.index = np.in1d(
            constants.white_note.number,
            number).nonzero()[0]
        self.name = constants.white_note.name[self.number % 12]

    def initialize_with_name(self, name):
        self.name = name
        self.number = constants.name_to_number_dictionary[self.name]
        # self.number = np.array(self.number)
        self.index = np.in1d(
            constants.note_numbers_C_to_C,
            self.number).nonzero()[0]

    # def initialize_randomly(self, level):
