import numpy as np
import constants


class Note:
    def __init__(self, keys, index=None, name=None, number=None,
                 interval=None, lower_note=None,
                 level=None):
        self.index = None
        self.name = None
        self.number = None

        self.raise_exceptions(index, name, number, interval, lower_note)
        if index is not None:
            self.initialize_with_index(index=index, keys=keys)
        elif name is not None:
            self.initialize_with_name(name=name, keys=keys)
        elif number is not None:
            self.initialize_with_number(number=number, keys=keys)

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

    def initialize_with_index(self, index, keys):
        self.index = index
        try:
            if keys == 'white':
                self.number = constants.keys.white.number[index]
                same_note_bottom_octave = constants.keys.white.number[0] + self.number % 12
                name_index = np.where(constants.keys.white.number == same_note_bottom_octave)
                name_index = name_index[0][0]
                self.name = constants.keys.white.name[name_index]
            elif keys == 'all':
                self.number = constants.keys.all.number[index]
                same_note_bottom_octave = constants.keys.all.number[0] + self.number % 12
                name_index = np.where(constants.keys.all.number == same_note_bottom_octave)
                name_index = name_index[0][0]
                self.name = constants.keys.all.name[name_index]
        except:
            self.number = None
            self.name = None

    def initialize_with_number(self, number, keys):
        raise Exception('this need work: initialize_with_number in "note"')
        self.number = number
        self.index = np.in1d(
            constants.white_note.number,
            number).nonzero()[0]
        self.name = constants.white_note.name[self.number % 12]

    def initialize_with_name(self, name, keys):
        raise Exception('this need work: initialize_with_name in "note"')
        self.name = name
        self.number = constants.name_to_number_dictionary[self.name]
        # self.number = np.array(self.number)
        self.index = np.in1d(
            constants.note_numbers_C_to_C,
            self.number).nonzero()[0]

