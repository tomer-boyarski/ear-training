import rtmidi
import os.path
import pickle
import plot_functions
import config
import initial
import constants
import time
import numpy as np
from termcolor import colored
from datetime import datetime
import copy


class Iteration:
    class Question:
        class Level:
            @staticmethod
            def raise_exceptions_level_literals(level_att):
                for att_name, att_val in level_att.items():
                    if att_val is not None:
                        if att_val not in range(1 + getattr(constants.levels.max, att_name)):
                            raise Exception('invalid ' + att_name + ' level')

            def set_level_attributes_if_literal_otherwise_something_else(
                    self, iteration_list, attribute_names,
                    attributes, attribute_levels, user):
                attribute_level_is_dynamic = {}
                for attribute, attribute_level, attribute_name in \
                        zip(attributes, attribute_levels, attribute_names):
                    attribute_level_is_dynamic[attribute_name] = False
                    if attribute is not None:
                        if attribute_level is not None:
                            raise Exception(attribute_name + ' is not None and ' + attribute_name + ' level is also not None')
                        else:
                            setattr(self, attribute_name, None)
                    else:  # attribute is None
                        if attribute_level is not None:
                            setattr(self, attribute_name, attribute_level)
                        else:  # attribute_level is None
                            attribute_level_is_dynamic[attribute_name] = True
                            if len(iteration_list) == 0:
                                initial_attribute_level = getattr(initial.get_level(user=user), attribute_name)
                                setattr(self, attribute_name, initial_attribute_level)
                return attribute_level_is_dynamic

            def calculate_total_level_according_to_raw_answer_time(
                    self, iteration_list, phase, max_level, mistakes_counter, user):
                if len(iteration_list) == 0:
                    self.total = initial.get_level(user).total
                elif len(iteration_list) >= 1:
                    if iteration_list[-1].answer.type is True:
                        self.set_level_after_correct_answer(
                            phase=phase, mistakes_counter=mistakes_counter,
                            iteration_list=iteration_list,
                            max_level=max_level)
                    elif iteration_list[-1].answer.type is False:
                        if iteration_list[-1].phase == 'exponential':
                            if len(iteration_list) >= 2:
                                answers = [q.answer.type for q in iteration_list]
                                error_indices = [i for i, r in enumerate(answers) if r is False]
                                y = len(iteration_list) - 1
                                if len(error_indices) >= 2:
                                    x = error_indices[-2]
                                else:
                                    x = 0
                                index = round((x + y) / 2)
                                self.total = iteration_list[index].level.total
                            else:
                                self.total = 0
                        elif iteration_list[-1].phase == 'steady state':
                            self.total = iteration_list[-1].question.level.total + \
                                         constants.levels.change.additive.decrease_with_error
                        # self.total = int(iteration_list[-1].level.total /
                        #                  constants.multiplicative_level_decrease_upon_error)
                        if self.total < 0:
                            self.total = 0

            def set_level_after_correct_answer(
                    self, phase, mistakes_counter, iteration_list, max_level):
                previous_raw_answer_time = iteration_list[-1].answer.time.raw
                previous_level = iteration_list[-1].question.level.total
                previous_number_of_notes = iteration_list[-1].question.number_of_notes
                a, b, c, d = constants.set_abcd(number_of_notes=previous_number_of_notes)
                x = previous_raw_answer_time
                if type(x) is tuple:  # (which is shouldn't be)
                    x = x[0]
                if phase == 'exponential':
                    y = -2 * (x - a) / (b - a) + 1
                    factor = constants.levels.change.multiplicative.increase
                    factor = factor ** (1 / (1 + mistakes_counter) ** 2)
                    factor = factor ** y
                    print('factor = ' + str(factor))
                    self.total = (previous_level + 1) * factor
                    self.total = round(self.total)
                elif phase == 'steady state':
                    y = (x - a) * (d - c) / (b - a) + c
                    y = round(y)
                    # y = y / len(iteration_list)**0.8
                    # y = int(np.ceil(y))
                    self.total = previous_level + y
                if self.total > max_level:
                    self.total = max_level
                if self.total < 0:
                    self.total = 0


        class Note:
            def __init__(self, keys=None, index=None, names=None, numbers=None,
                         interval=None, lower_note=None, indices=None, 
                         level=None, number_of_notes=None):

                self.indices = copy.copy(indices)
                self.names = names
                self.numbers = numbers

                # self.raise_exceptions(index, name, number, interval, lower_note)

            # def new_note_method(self):
                # if self.indices is not None:
                #     self.initialize_with_index(index=self.indices, keys=keys)
                # elif self.name is not None:
                #     self.initialize_with_name(name=self.name, keys=keys)
                # elif self.number is not None:
                #     self.initialize_with_number(number=self.number, keys=keys)

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

            def initialize_with_index(self, keys):
                for note_index_in_chord, note_index_in_scale in enumerate(self.indices):
                    if keys == 'white':
                        self.numbers[note_index_in_chord] = constants.keys.white.numbers[note_index_in_scale]
                        same_note_bottom_octave = constants.keys.white.numbers[0] +\
                            self.numbers[note_index_in_chord] % 12
                        name_index = np.where(constants.keys.white.numbers == same_note_bottom_octave)
                        name_index = name_index[0][0]
                        self.names[note_index_in_chord] = constants.keys.white.names[name_index]
                    elif keys == 'all':
                        self.numbers[note_index_in_chord] = constants.keys.all.number[note_index_in_scale]
                        same_note_bottom_octave = constants.keys.all.number[0] + \
                            self.numbers[note_index_in_chord] % 12
                        name_index = np.where(constants.keys.all.number == same_note_bottom_octave)
                        name_index = name_index[0][0]
                        self.names[note_index_in_chord] = constants.keys.all.name[name_index]

            def initialize_with_number(self, number, keys):
                raise Exception('this need work: initialize_with_number in "note"')
                # self.number = number
                # self.index = np.in1d(
                #     constants.white_note.numbers,
                #     number).nonzero()[0]
                # self.name = constants.white_note.names[self.number % 12]

            def initialize_with_name(self, name, keys):
                raise Exception('this need work: initialize_with_name in "note"')

        @staticmethod
        def create_none_list_if_necessary(list_or_none, size):
            if list_or_none is None:
                output = [None] * size
            else:
                if type(list_or_none) is list or type(list_or_none) is np.ndarray:
                    if len(list_or_none) == size:
                        output = list_or_none
                    else: # elif len(list_or_none) != size:
                        raise Exception('The list received by "create_None_list_if_necessary" ' +
                                        str(list_or_none) + ' has a length of ' + str(len(list_or_none)) +
                                        ' but it should have a length of ' + str(size))
                else: # elif type(list_or_none) is not list and type(list_or_none) is not np.array:
                    raise Exception('note attributes inputs must be lists or numpy arrays')
            return output

    class Question_Steps_and_Intervals(Question):
        class Level:
            @staticmethod
            def raise_exceptions_level_literals(level_att):
                for att_name, att_val in level_att.items():
                    if att_val is not None:
                        max_att_level = getattr(constants.levels.max, att_name)
                        if att_name != 'number_of_notes':
                            max_att_level = getattr(max_att_level, config.keys)
                        if att_val not in range(1 + max_att_level):
                            raise Exception('invalid ' + att_name + ' level')

            def __init__(self, iteration_list, phase, mistakes_counter,
                         max_level):
                pass

            def set_level_attributes_if_literal_otherwise_something_else(
                    self, iteration_list, attribute_names,
                    attributes, attribute_levels, user):
                attribute_level_is_dynamic = {}
                for attribute, attribute_level, attribute_name in \
                        zip(attributes, attribute_levels, attribute_names):
                    attribute_level_is_dynamic[attribute_name] = False
                    if attribute is not None:
                        if attribute_level is not None:
                            raise Exception(attribute_name + ' is not None and ' + attribute_name + ' level is also not None')
                        else:
                            setattr(self, attribute_name, None)
                    else:  # attribute is None
                        if attribute_level is not None:
                            setattr(self, attribute_name, attribute_level)
                        else:  # attribute_level is None
                            attribute_level_is_dynamic[attribute_name] = True
                            if len(iteration_list) == 0:
                                initial_attribute_level = getattr(initial.get_level(user=user), attribute_name)
                                setattr(self, attribute_name, initial_attribute_level)
                return attribute_level_is_dynamic

            def calculate_total_level_according_to_raw_answer_time(
                    self, iteration_list, phase, max_level, mistakes_counter, user):
                if len(iteration_list) == 0:
                    self.total = initial.get_level(user).total
                elif len(iteration_list) >= 1:
                    if iteration_list[-1].answer.type is True:
                        self.set_level_after_correct_answer(
                            phase=phase, mistakes_counter=mistakes_counter,
                            iteration_list=iteration_list,
                            max_level=max_level)
                    elif iteration_list[-1].answer.type is False:
                        if iteration_list[-1].phase == 'exponential':
                            if len(iteration_list) >= 2:
                                answers = [q.answer.type for q in iteration_list]
                                error_indices = [i for i, r in enumerate(answers) if r is False]
                                y = len(iteration_list) - 1
                                if len(error_indices) >= 2:
                                    x = error_indices[-2]
                                else:
                                    x = 0
                                index = round((x + y) / 2)
                                self.total = iteration_list[index].level.total
                            else:
                                self.total = 0
                        elif iteration_list[-1].phase == 'steady state':
                            self.total = iteration_list[-1].question.level.total + \
                                         constants.levels.change.additive.decrease_with_error
                        # self.total = int(iteration_list[-1].level.total /
                        #                  constants.multiplicative_level_decrease_upon_error)
                        if self.total < 0:
                            self.total = 0

            def set_level_after_correct_answer(
                    self, phase, mistakes_counter, iteration_list, max_level):
                previous_raw_answer_time = iteration_list[-1].answer.time.raw
                previous_level = iteration_list[-1].question.level.total
                previous_number_of_notes = iteration_list[-1].question.number_of_notes
                a, b, c, d = constants.set_abcd(number_of_notes=previous_number_of_notes)
                x = previous_raw_answer_time
                if type(x) is tuple:  # (which is shouldn't be)
                    x = x[0]
                if phase == 'exponential':
                    y = -2 * (x - a) / (b - a) + 1
                    factor = constants.levels.change.multiplicative.increase
                    factor = factor ** (1 / (1 + mistakes_counter) ** 2)
                    factor = factor ** y
                    print('factor = ' + str(factor))
                    self.total = (previous_level + 1) * factor
                    self.total = round(self.total)
                elif phase == 'steady state':
                    y = (x - a) * (d - c) / (b - a) + c
                    y = round(y)
                    # y = y / len(iteration_list)**0.8
                    # y = int(np.ceil(y))
                    self.total = previous_level + y
                if self.total > max_level:
                    self.total = max_level
                if self.total < 0:
                    self.total = 0

        class Level_Step_and_Intervals(Level):
            def __init__(self, iteration_list, phase, mistakes_counter,
                         max_level):
                self.number_of_notes = None
                self.intervals = None
                self.step_size = None
                level_att = {'number_of_notes': config.number_of_notes_level,
                             'intervals': config.intervals_level,
                             'step_size': config.step_size_level}
                self.raise_exceptions_level_literals(level_att=level_att)
                attributes = [config.number_of_notes, config.intervals, config.step_size]
                attribute_names = ['number_of_notes', 'intervals', 'step_size']
                attribute_levels = [config.number_of_notes_level, config.intervals_level, config.step_size_level]

                is_attribute_dynamic = \
                    self.set_level_attributes_if_literal_otherwise_something_else(
                        iteration_list=iteration_list,
                        attributes=attributes,
                        attribute_levels=attribute_levels,
                        attribute_names=attribute_names,
                        user=config.user)
                self.dynamic_attributes = {k: v for k, v in is_attribute_dynamic.items() if v is True}
                if len(self.dynamic_attributes) == 0:
                    self.total = None
                else:
                    self.calculate_total_level_according_to_raw_answer_time(
                        iteration_list, phase, max_level=max_level, mistakes_counter=mistakes_counter,
                        user=config.user)
                    self.calculate_dynamic_attributes_from_total_level(
                        is_attribute_dynamic=is_attribute_dynamic,
                        attribute_names=attribute_names, keys=config.keys)

                    if constants.show_total_level:
                        print('level.total = ' + str(self.total))
                        # print('number_of_notes level= ' + str(self.number_of_notes))
                        # print('intervals level = ' + str(self.intervals))
                        # print('step_size level = ' + str(self.step_size))

            def calculate_dynamic_attributes_from_total_level(
                    self, keys, is_attribute_dynamic, attribute_names):
                dynamic_attribute_names = [x for x in attribute_names if
                                           is_attribute_dynamic[x]]
                max_step_size_level = getattr(constants.levels.max.step_size, keys)

                # if len(dynamic_attribute_names) != 3:
                #     raise Exception('I still did not write the code for how to '
                #                     'calculate the attribute level from the total level '
                #                     'when not all attributes are dynamic')
                if dynamic_attribute_names == ['intervals', 'step_size']:
                    if self.total <= max_step_size_level:
                        self.number_of_notes = None
                        self.intervals = 0
                        self.step_size = self.total
                    elif self.total > max_step_size_level:
                        current_level = self.total - max_step_size_level - 1
                        self.intervals, self.step_size = np.divmod(
                            current_level, max_step_size_level + 1)
                        self.intervals = self.intervals + 1
                elif len(dynamic_attribute_names) == 3:
                    if self.total <= max_step_size_level:
                        self.number_of_notes = 0
                        self.intervals = None
                        self.step_size = self.total
                    elif self.total > max_step_size_level:
                        current_level = self.total - max_step_size_level - 1
                        self.number_of_notes, remainder = \
                            np.divmod(current_level,
                                      (getattr(constants.levels.max.intervals, keys) + 1) *
                                      (getattr(constants.levels.max.step_size, keys) + 1))
                        self.number_of_notes = self.number_of_notes + 1
                        self.intervals, self.step_size = np.divmod(
                            remainder, getattr(constants.levels.max.step_size, keys) + 1)

        class Step:
            def __init__(self, keys, size=None, trend=None,
                         current_index=None, previous_index=None,
                         difficulty_level=None):
                if (size is not None or trend is not None) and current_index is not None:
                    raise Exception('step object is over-defined')

                if size is not None:
                    self.size = size
                elif current_index is not None and previous_index is not None:
                    self.size = abs(current_index - previous_index) + 1
                elif difficulty_level is not None:
                    p = getattr(constants.levels.step_size, keys)
                    p = p[difficulty_level, :]
                    self.size = np.random.choice(
                        np.arange(1, constants.max_step_size(keys=keys) + 1), 1, p=p)
                    self.size = self.size[0]
                else:
                    raise Exception('Can not determine step size. Not enough inputs.')

                if trend is not None:
                    self.trend = np.array(trend)
                elif current_index is not None and previous_index is not None:
                    self.trend = np.sign(self.size)
                else:
                    self.trend = (-1) ** np.random.binomial(1, 0.5)

        @staticmethod
        def raise_exceptions_for_notes_and_intervals():
            # Check that all note attributes are valid
            note_attributes = {'names': config.note_names,
                               'numbers': config.note_numbers,
                               'indices': config.note_indices}
            note_attributes = {k: v for k, v in note_attributes.items() if v is not None}

            # check that all note attributes are valid
            for key_1, list_1 in note_attributes.items():
                if config.key == 'WHITE':
                    att_list = getattr(constants.white_note, key_1)
                    for item in list_1:
                        if item is not None and item not in att_list:
                            raise Exception('invalid note ' + key_1)
                elif config.key != 'WHITE':
                    raise Exception('missing exception rule for non-white keys')

            # Check that all note attributes have the same length
            for key_1, list_1 in note_attributes.items():
                for key_2, list_2 in note_attributes.items():
                    if len(list_1) != len(list_2):
                        raise Exception('Length of ' + key_1 + ' is ' + str(len(list_1)) +
                                        ' but ' +
                                        ' length of ' + key_2 + ' is ' + str(len(list_2)) +
                                        '. They should be the same.')

            # Check that the length of all note attributes is the same as the number of notes
            if config.number_of_notes is not None:
                for config.key, a_list in note_attributes.items():
                    if len(a_list) != config.number_of_notes:
                        raise Exception('length of ' + config.key + ' is ' + str(len(a_list)) +
                                        ' but number of notes is ' + str(config.number_of_notes) +
                                        '. They should be the same.')

            # Check that the length of all note attributes is the same as number of intervals plus one
            if config.intervals is not None:
                for config.key, a_list in note_attributes.items():
                    if len(a_list) != len(config.intervals) + 1:
                        raise Exception('Length of ' + config.key + ' is ' + str(len(a_list)) +
                                        ' but length of "interval" is ' + str(len(config.intervals)) +
                                        '. Length of "intervals" should be equal to length of ' +
                                        config.key + ' - 1.')

            if config.step_size is not None or config.step_trend is not None:
                for key_1, list_1 in note_attributes.items():
                    if list_1[0] is not None:
                        raise Exception('bottom note is over-defined')

        @staticmethod
        def get_number_of_notes_intervals_and_step_size_from_literals(
                iteration_list, note_indices=None):
            number_of_notes = None
            if note_indices is None:
                number_of_notes = config.number_of_notes
            intervals = config.intervals
            step_size = config.step_size
            step_trend = config.step_trend
            if len(config.note_attributes) != 0:
                for key, a_list in config.note_attributes.items():
                    number_of_notes = len(a_list)
            elif config.intervals is not None:
                number_of_notes = len(config.intervals) + 1

            if note_indices is None:
                note_indices = config.note_indices
            if note_indices is not None:
                number_of_notes = len(note_indices)
                if None not in note_indices:
                    if config.intervals is None:
                        note_indices = np.array(note_indices)
                        intervals = note_indices[1:] - note_indices[:-1] + 1
                        intervals = intervals.tolist()
                if note_indices[0] is not None:
                    if config.step_size is None:
                        if len(iteration_list) >= 1:
                            previous_bottom_note_index = iteration_list[-1].question.note.indices[0]
                        else:
                            previous_bottom_note_index = initial.indices[0]
                        step = note_indices[0] - previous_bottom_note_index + 1
                        # step = step[0]
                        step_size = abs(step)
                        step_trend = np.sign(step_size)
            return number_of_notes, intervals, step_size, step_trend

        def __init__(self, iteration_list, phase, previous_note_indices,
                     mistakes_counter, note_indices=None):
            self.raise_exceptions_for_notes_and_intervals()

            self.max_level = self.set_max_level()

            self.level = self.Level_Step_and_Intervals(iteration_list=iteration_list,
                                    max_level=self.max_level,
                                    phase=phase, mistakes_counter=mistakes_counter)

            number_of_notes, _, _, _ = \
                self.get_number_of_notes_intervals_and_step_size_from_literals(
                    iteration_list=iteration_list, note_indices=note_indices)
            self.number_of_notes = number_of_notes

            if constants.show_phase:
                print('phase = ' + phase)
            self.step = None

            if number_of_notes is None:
                self.number_of_notes = np.random.choice(
                    np.arange(1, 1 + constants.max_chord_size), 1,
                    p=constants.levels.number_of_notes[self.level.number_of_notes, :])
                self.number_of_notes = self.number_of_notes[0]

            intervals = self.create_none_list_if_necessary(list_or_none=config.intervals, size=self.number_of_notes - 1)
            note_names = self.create_none_list_if_necessary(list_or_none=config.note_names, size=self.number_of_notes)
            note_numbers = self.create_none_list_if_necessary(list_or_none=config.note_numbers, size=self.number_of_notes)
            if note_indices is None:
                note_indices = config.note_indices
            note_indices = self.create_none_list_if_necessary(list_or_none=note_indices, size=self.number_of_notes)
            # Simplity the code.
            # Either all notes are deterministic or none of them are.
            self.note = self.Note(names=note_names, numbers=note_numbers, indices=note_indices)
            note_indices_1 = copy.copy(note_indices)
            if type(note_indices_1) is not list:
                note_indices_1 = note_indices_1.tolist()
            if note_indices_1 != [None]*self.number_of_notes:
                self.note.initialize_with_index(keys=config.keys)
            else:
                if config.step_top_or_bottom == 'top':
                    previous_note_indices = np.array(previous_note_indices)
                    previous_note_indices = np.flip(previous_note_indices)
                if constants.show_step_options:
                    p = getattr(constants.levels.step_size, config.keys)
                    p = p[self.level.step_size, :]
                    x = np.arange(len(p))
                    print('step option: ' + str(x[p>0]+1))
                while True:
                    for index_in_chord in np.arange(self.number_of_notes):
                        if index_in_chord == 0:
                            self.set_chord_step_and_top_or_bottom_note(
                                previous_note_indices=previous_note_indices, 
                                index_in_chord=index_in_chord,
                                note_names=note_names, note_numbers=note_numbers,
                                note_indices=note_indices,
                                level=self.level)
                            if constants.show_step:
                                print('step size = ' + str(self.step.size) + ' step trend = ' + str(self.step.trend))
                        else:
                            self.set_interval_and_note(
                                index_in_chord=index_in_chord,
                                note_names=note_names, note_numbers=note_numbers, 
                                note_indices=note_indices,
                                intervals=intervals,
                                level=self.level)
                    keys_obj = getattr(constants.keys, config.keys)
                    possible_note_indices = keys_obj.indices
                    indices = self.note.indices
                    # why is this if statement here?
                    # if None not in note_indices:
                    if config.step_top_or_bottom == 'top':
                        indices = np.array(indices)
                        indices = indices - self.note.indices[0]
                        indices = -1 * indices
                        indices = indices + self.note.indices[0]
                        indices = np.flip(indices)
                        self.note.indices = indices
                    elif config.step_top_or_bottom == 'bottom':
                        pass
                    if all(index in possible_note_indices for index in indices):
                        self.note.initialize_with_index(keys=config.keys)
                        break
                    else:
                        self.note.indices = copy.copy(note_indices)
        
        @staticmethod
        def set_max_level():
            max_level = 0
            if config.step_size is None and config.step_size_level is None:
                max_level = max_level + getattr(constants.levels.max.step_size, config.keys)
            if config.intervals is None and config.intervals_level is None:
                if config.number_of_notes is None:
                    max_level = max(1, max_level) + getattr(constants.levels.max.intervals, config.keys) * max(1, max_level) * 4
                elif config.number_of_notes > 1:
                    max_level = max_level + getattr(constants.levels.max.intervals, config.keys) * max(1, max_level)
                elif config.number_of_notes == 1:
                    pass
            if config.number_of_notes is None and config.number_of_notes_level is None:
                if config.intervals is not None:
                    max_level = max_level + (constants.levels.max.number_of_notes-1) * max(1, max_level)
            return max_level

        def set_chord_step_and_top_or_bottom_note(
                self, previous_note_indices, index_in_chord,
                note_names=None, note_numbers=None, note_indices=None,
                level=None):
            keys = config.keys
            step_size = config.step_size
            step_trend = config.step_trend
            note_is_literally_defined = \
                note_indices[index_in_chord] is not None or \
                note_names[index_in_chord] is not None or \
                note_numbers[index_in_chord] is not None
            step_is_literally_defined = step_size is not None or step_trend is not None
            if note_is_literally_defined:
                self.step = self.Step(keys=keys,
                                 current_index=note_indices[index_in_chord],
                                 previous_index=previous_note_indices[index_in_chord])
            else:
                while True:
                    if step_is_literally_defined:
                        self.step = self.Step(keys=keys, size=step_size,
                                         trend=step_trend)
                    else:
                        self.step = self.Step(keys=keys, difficulty_level=level.step_size)
                    new_note_index = previous_note_indices[index_in_chord] + \
                                       (self.step.size - 1) * self.step.trend
                    keys_obj = getattr(constants.keys, keys)
                    num_notes_per_octave = keys_obj.per_octave
                    top_note_index_allowed = 2 * num_notes_per_octave
                    if config.step_top_or_bottom == 'top':
                        top_note_index_allowed = top_note_index_allowed + num_notes_per_octave
                    if 0 <= new_note_index < top_note_index_allowed:
                        self.note.indices[index_in_chord] = new_note_index
                        break

        def set_interval_and_note(
                self, index_in_chord,
                note_names=None, note_numbers=None, note_indices=None,
                intervals=None,
                level=None):
            keys = config.keys
            note_is_literally_defined = \
                note_indices[index_in_chord] is not None or \
                note_names[index_in_chord] is not None or \
                note_numbers[index_in_chord] is not None
            if note_is_literally_defined:
                intervals[index_in_chord - 1] = \
                    self.note.indices[index_in_chord] - \
                    self.note.indices[index_in_chord-1] + 1
            else:
                if intervals[index_in_chord - 1] is None:
                    p = getattr(constants.levels.intervals, keys)
                    p = p[level.intervals, :]
                    x = getattr(constants.keys, keys)
                    x = len(x.names) + 2
                    intervals[index_in_chord - 1] = np.random.choice(
                        np.arange(2, x), 1, p=p)
                lower_note = self.note.indices[index_in_chord - 1]
                note_index = lower_note + intervals[index_in_chord - 1] - 1
                note_index = note_index[0]
                self.note.indices[index_in_chord] = note_index

    class Question_notes_from_a_box(Question):
        def __init__(self):
            self.max_level = 2 
        def set_max_level(self):

            pass

    class Answer:
        # class Flag:
        #     def __init__(self):
        #         self.repeat = True
        #         # self.termination = False
        #         self.correct = None
        #         self.reveal = None

        class Time:
            def __init__(self, number_of_notes):
                # a, b, c, d = constants.set_abcd(number_of_notes=number_of_notes)
                # x = a - c * (b-a) / (d-c)
                self.raw = None
                self.autoregressive = None  # constants.optimal_answer_time

        def __init__(self, number_of_notes):
            self.text = 'C'
            self.type = 'repeat'
            # self.flag = self.Flag()
            self.time = self.Time(number_of_notes=number_of_notes)

    class Attributes:
        def __init__(self, request_answer,
                     error_state=initial.error_state
                     ):
            # self.error_state = error_state
            self.request_answer = request_answer

    class Volume:
        def __init__(self):
            self.value = round((constants.max_volume + constants.min_volume) / 2)
            self.trend = (-1) ** np.random.binomial(1, 0.5)


    def request_answer(self):
        note_numbers = self.question.note.numbers
        volume = self.volume.value
        question_start_time = time.time()
        self.answer.text = input("Identify Note:")
        self.answer.text = self.answer.text.strip()
        self.answer.time.raw = time.time() - question_start_time
        self.answer.time.datetime = datetime.now()
        answer_time_now_fraction = self.answer.time.raw - np.round(self.answer.time.raw)
        time.sleep(constants.quarter_note_time - answer_time_now_fraction)
        # note_numbers = [note.number for note in iteration.chord.notes]
        for number in note_numbers:
            constants.mo.send_message([constants.note_off,
                                       number, volume])
        self.answer.text = self.answer.text.upper()
        self.set_answer_time_to_nan_if_incorrect()
        termination_flag = self.check_user_answer_at_question_end()
        return termination_flag

    def set_answer_time_to_nan_if_incorrect(self):
        is_incorrect = True
        note_names = self.question.note.names
        if config.accept_without_spaces:
            if self.answer.text == ''.join(note_names):
                is_incorrect = False
        if config.accept_with_spaces:
            if self.answer.text == ' '.join(note_names):
                is_incorrect = False
        if is_incorrect:
            self.answer.time.raw = np.nan

    def check_user_answer_at_question_end(self):
        termination_flag = False
        note_names = self.question.note.names
        is_correct = False
        if config.accept_without_spaces:
            if self.answer.text == ''.join(note_names):
                is_correct = True
        if config.accept_with_spaces:
            if self.answer.text == ' '.join(note_names):
                is_correct = True
        if is_correct:
            self.answer.type = True
            print(colored("Good :-)", 'blue'))
        elif self.answer.text == 'END':
            self.answer.type = 'end'
            termination_flag = True
        elif self.answer.text == 'RESTART':
            self.answer.type = 'restart'
            print(colored("OK, RESTART: :-)", 'green'))
            raise Exception('need to implement RESTART with "intro"')
            # intro()
        elif self.answer.text == 'REPEAT':
            self.answer.type = 'repeat'
        else:  # user error
            self.answer.type = False
            self.mistakes_counter = self.mistakes_counter + 1
            print(colored("Bad :-)", 'red'))
        return termination_flag

    @staticmethod
    def intro(x=2):
        note_on = 144
        note_off = 128
        my_volume = 64
        for i in range(4, 0, -1):
            note_to_play_now = constants.keys.white.numbers[i] + 12
            constants.mo.send_message([note_on, note_to_play_now, my_volume])
            time.sleep(constants.quarter_note_time / 4 / x)
            constants.mo.send_message([note_off, note_to_play_now, my_volume])

        constants.mo.send_message([note_on, 60, my_volume])
        time.sleep(constants.quarter_note_time / 2 / x)
        constants.mo.send_message([note_off, 60, my_volume])
        previous_note_index = np.array([7])

        return previous_note_index

    def set_mistakes_counter_and_phase(self, iteration_list):
        if len(iteration_list) == 0:
            self.phase = config.phase
            self.mistakes_counter = 0
        else:
            self.mistakes_counter = iteration_list[-1].mistakes_counter
            if iteration_list[-1].phase == 'steady state':
                self.phase = 'steady state'
            else:
                if iteration_list[-1].answer.type is False:
                    self.phase = 'steady state'
                else:
                    self.phase = 'exponential'
    @staticmethod
    def raise_exceptions_chord_vs_level_literals():
        if len(config.note_attributes) != 0 or config.intervals is not None or config.number_of_notes is not None:
            print('"get_number_of_notes" says: Number of notes is not random.')
            if config.number_of_notes_level is not None:
                raise Exception('Please do not explicitly define the "number of notes level" '
                                'if the number of notes is explicitly defined.')
        if config.intervals_level is not None and config.intervals is not None and None not in config.intervals:
            raise Exception('Please do not explicitly define the "intervals level" '
                            'if all intervals are explicitly defined.')
        if config.step_size is not None and config.step_size_level is not None:
            raise Exception('Please do not explicitly define the "step size level" '
                            'if the step size is explicitly defined.')

    def __init__(self, iteration_list):
        self.raise_exceptions_chord_vs_level_literals
        note_attributes = {'names': config.note_names,
                           'numbers': config.note_numbers,
                           'indices': config.note_indices}
        note_attributes = {k: v for k, v in note_attributes.items() if v is not None}


        self.phase = None
        self.mistakes_counter = None
        self.set_mistakes_counter_and_phase(iteration_list=iteration_list)

        if len(iteration_list) == 0:
            if config.play_intro:
                self.intro(x=2)
            self.question = self.Question_Steps_and_Intervals(mistakes_counter=self.mistakes_counter,
                                          phase=self.phase, iteration_list=iteration_list,
                                          previous_note_indices=initial.indices(keys=config.keys))
        elif len(iteration_list) == 1:
            previous_note_indices = iteration_list[-1].question.note.indices
            if iteration_list[-1].answer.type is True:
                self.question = self.Question_Steps_and_Intervals(mistakes_counter=self.mistakes_counter,
                                              phase=self.phase, iteration_list=iteration_list,
                                              previous_note_indices=previous_note_indices)
            elif iteration_list[-1].answer.type is False:
                self.question = self.Question_Steps_and_Intervals(mistakes_counter=self.mistakes_counter,
                                              phase=self.phase, iteration_list=iteration_list,
                                              previous_note_indices=previous_note_indices,
                                              note_indices=initial.indices(keys=config.keys))
        elif len(iteration_list) >= 2:
            previous_note_indices = iteration_list[-1].question.note.indices
            if iteration_list[-1].answer.type is True:
                self.question = self.Question_Steps_and_Intervals(mistakes_counter=self.mistakes_counter,
                                              phase=self.phase, iteration_list=iteration_list,
                                              previous_note_indices=previous_note_indices)
            elif iteration_list[-1].answer.type is False:
                if iteration_list[-2].answer.type is True:
                    note_indices = iteration_list[-2].question.note.indices
                    self.question = self.Question_Steps_and_Intervals(mistakes_counter=self.mistakes_counter,
                                                  phase=self.phase, iteration_list=iteration_list,
                                                  note_indices=note_indices,
                                                  previous_note_indices=previous_note_indices)
                elif iteration_list[-2].answer.type is False:
                    if config.play_intro:
                        self.intro(x=2)
                    self.question = self.Question_Steps_and_Intervals(mistakes_counter=self.mistakes_counter,
                                                  phase=self.phase, iteration_list=iteration_list,
                                                  previous_note_indices=initial.indices(keys=config.keys))

        self.answer = self.Answer(number_of_notes=self.question.number_of_notes)
        self.volume = self.Volume()
        self.attributes = self.Attributes(config.request_answer)

    def play_chord(self, iteration_list):
        # if self.chord is None:
        #     self = set_chord(self, iteration_list)
        #     self = set_volume(self, iteration_list)
        if constants.show_notes:
            print(self.question.note.numbers)
            print(self.question.note.names)
        try:
            for number in self.question.note.numbers:
                constants.mo.send_message([constants.note_on,
                                           number, self.volume.value])

        except:
            raise Exception('"high_level_classes" says: '
                            'I can not play these notes.')
        if not self.attributes.request_answer:
            time.sleep(constants.quarter_note_time)
            for number in self.question.note.numbers:
                constants.mo.send_message([rtmidi.midiconstants.NOTE_OFF,
                                           number, self.volume.value])


def main():
    iteration_list = []
    termination_flag = False
    while not termination_flag:
        iteration = Iteration(iteration_list=iteration_list)
        while iteration.answer.type == 'repeat':
            iteration.play_chord(iteration_list)
            termination_flag = iteration.request_answer()
        iteration_list.append(iteration)

    constants.mo.close_port()


    if None not in [config.number_of_notes, config.step_size, config.intervals]:
        file_name = 'answer_times//answer_times_number_of_notes_' + str(config.number_of_notes) + '.p'
        if os.path.exists(file_name):
            answer_times_old = pickle.load(open(file_name, "rb"))
        else:
            answer_times_old = []
        answer_times = [iteration.answer.time.raw for iteration in iteration_list]
        answer_times = answer_times_old + answer_times
        pickle.dump(answer_times, open(file_name, "wb"))
    else:
        iteration_list = iteration_list[:-1]
        file_name = 'users\\' + config.user + '\\list_of_iteration_lists.pkl'
        # if os.path.isfile(file_name): 
        try:
            with open(file_name, 'rb') as input:
                list_of_iteration_lists = pickle.load(input)
        except:
            list_of_iteration_lists = []
        if len(iteration_list) > 0:
            list_of_iteration_lists.append(iteration_list)
        with open(file_name, 'wb') as output:
            pickle.dump(list_of_iteration_lists, output, pickle.HIGHEST_PROTOCOL)
        if len(iteration_list) > 0:
            with open('users\\' + config.user + '\\level.pkl', 'wb') as output:
                pickle.dump(iteration_list[-1].question.level.total, output, pickle.HIGHEST_PROTOCOL)
        if len(list_of_iteration_lists) > 0:
            if config.plot:
                plot_functions.my_plot(list_of_iteration_lists=list_of_iteration_lists, keys=config.keys)

    print('this is the end of MAIN')


if __name__ == '__main__':
    main()