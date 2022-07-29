import os.path
import pickle
import plot_functions
from archive.high_level_classes_02 import *
import config
import raise_exceptions


iteration_list = []

termination_flag = False
step_size = None
keys = 'white'
# keys = 'all'
number_of_notes = None
intervals = None
# phase = 'exponential'
step_trend = None
phase = 'steady state'
play_intro = True
accept_with_spaces = True
accept_without_spaces = True
mistakes_counter = 0
user = 'tomer'
request_response=True



class Iteration:
    class Question:
        class Level:
            def __init__(self, iteration_list, phase, keys, mistakes_counter,
                         step_size, intervals, number_of_notes, step_size_level,
                         number_of_notes_level, interval_level, max_level, user):

                attributes = [number_of_notes, intervals, step_size]
                attribute_names = ['number_of_notes', 'intervals', 'step_size']
                attribute_levels = [number_of_notes_level, interval_level, step_size_level]

                is_attribute_dynamic = \
                    self.set_level_attributes_if_literal_otherwise_something_else(
                        iteration_list=iteration_list,
                        attributes=attributes,
                        attribute_levels=attribute_levels,
                        attribute_names=attribute_names,
                        user=user)
                self.dynamic_attributes = {k: v for k, v in is_attribute_dynamic.items() if v is True}
                if len(self.dynamic_attributes) == 0:
                    self.total = None
                else:
                    self.calculate_total_level_according_to_raw_response_time(
                        iteration_list, phase, max_level=max_level, mistakes_counter=mistakes_counter,
                        user=user)
                    self.number_of_notes = None
                    self.intervals = None
                    self.step_size = None
                    self.calculate_dynamic_attributes_from_total_level(
                        is_attribute_dynamic=is_attribute_dynamic,
                        attribute_names=attribute_names, keys=keys)

                    if constants.show_total_level:
                        print('level.total = ' + str(self.total))
                        print('number_of_notes level= ' + str(self.number_of_notes))
                        print('intervals level = ' + str(self.intervals))
                        print('step_size level = ' + str(self.step_size))

            def raise_exception(self):
                my_str = 'To manually set the difficulty level, ' + \
                         'either input the "total" level or ' + \
                         'both the "step_size" and "chord_size" levels. '
                if self.step_size is not None and self.number_of_notes is None and self.total is None:
                    raise Exception(my_str +
                                    'You only put the "step_size" level.')
                if self.step_size is None and self.number_of_notes is not None and self.total is None:
                    raise Exception(my_str +
                                    'You only put the "chord_size" level.')
                if self.step_size is None and self.number_of_notes is not None and self.total is not None:
                    raise Exception(my_str +
                                    'You put both the "total" level and the "chord_size" level.')
                if self.step_size is not None and self.number_of_notes is None and self.total is not None:
                    raise Exception(my_str +
                                    'You put both the "total" level and the "step_size" level.')
                if self.step_size is not None and self.number_of_notes is not None and self.total is not None:
                    raise Exception(my_str +
                                    'You put all three levels together.')

            def set_level_attributes_if_literal_otherwise_something_else(
                    self, iteration_list, attribute_names,
                    attributes, attribute_levels, user):
                update_level_according_to_user_response = {}
                for attribute, attribute_level, attribute_name in \
                        zip(attributes, attribute_levels, attribute_names):
                    update_level_according_to_user_response[attribute_name] = False
                    if attribute is not None:
                        if attribute_level is not None:
                            raise Exception('step size is not None and step size level is also not None')
                        else:
                            setattr(self, attribute_name, None)
                    else:  # attribute is None
                        if attribute_level is not None:
                            setattr(self, attribute_name, attribute_level)
                        else:  # attribute_level is None
                            update_level_according_to_user_response[attribute_name] = True
                            if len(iteration_list) == 0:
                                initial_attribute_level = getattr(initial.get_level(user=user), attribute_name)
                                setattr(self, attribute_name, initial_attribute_level)
                return update_level_according_to_user_response

            def calculate_total_level_according_to_raw_response_time(
                    self, iteration_list, phase, max_level, mistakes_counter, user):
                if len(iteration_list) == 0:
                    self.total = initial.get_level(user).total
                elif len(iteration_list) >= 1:
                    if iteration_list[-1].response.type is True:
                        self.set_level_after_correct_answer(
                            phase=phase, mistakes_counter=mistakes_counter,
                            iteration_list=iteration_list,
                            max_level=max_level)
                    elif iteration_list[-1].response.type is False:
                        if iteration_list[-1].phase == 'exponential':
                            if len(iteration_list) >= 2:
                                responses = [q.response.type for q in iteration_list]
                                error_indices = [i for i, r in enumerate(responses) if r is False]
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

            def calculate_total_level_from_dynamic_attributes(self):
                self.total = self.number_of_notes * \
                             constants.levels.intervals.shape[0] * \
                             constants.levels.step_size.shape[0] + \
                             self.intervals * \
                             constants.levels.step_size.shape[0] + \
                             self.step_size

            def set_level_after_correct_answer(
                    self, phase, mistakes_counter, iteration_list, max_level):
                previous_raw_response_time = iteration_list[-1].response.time.raw
                previous_level = iteration_list[-1].question.level.total
                previous_number_of_notes = iteration_list[-1].question.number_of_notes
                a, b, c, d = constants.set_abcd(number_of_notes=previous_number_of_notes)
                x = previous_raw_response_time
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

        class Note:
            def __init__(self, keys, index=None, name=None, number=None,
                         interval=None, lower_note=None,
                         level=None):

                self.index = index
                self.name = name
                self.number = number

                self.raise_exceptions(index, name, number, interval, lower_note)

            # def new_note_method(self):
                if self.index is not None:
                    self.initialize_with_index(index=self.index, keys=keys)
                elif self.name is not None:
                    self.initialize_with_name(name=self.name, keys=keys)
                elif self.number is not None:
                    self.initialize_with_number(number=self.number, keys=keys)

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
                if keys == 'white':
                    self.number = constants.keys.white.numbers[index]
                    same_note_bottom_octave = constants.keys.white.numbers[0] + self.number % 12
                    name_index = np.where(constants.keys.white.numbers == same_note_bottom_octave)
                    name_index = name_index[0][0]
                    self.name = constants.keys.white.names[name_index]
                elif keys == 'all':
                    self.number = constants.keys.all.number[index]
                    same_note_bottom_octave = constants.keys.all.number[0] + self.number % 12
                    name_index = np.where(constants.keys.all.number == same_note_bottom_octave)
                    name_index = name_index[0][0]
                    self.name = constants.keys.all.name[name_index]

            def initialize_with_number(self, number, keys):
                raise Exception('this need work: initialize_with_number in "note"')
                # self.number = number
                # self.index = np.in1d(
                #     constants.white_note.numbers,
                #     number).nonzero()[0]
                # self.name = constants.white_note.names[self.number % 12]

            def initialize_with_name(self, name, keys):
                raise Exception('this need work: initialize_with_name in "note"')
                # self.name = name
                # self.number = constants.name_to_number_dictionary[self.name]
                # # self.number = np.array(self.number)
                # self.index = np.in1d(
                #     constants.note_numbers_C_to_C,
                #     self.number).nonzero()[0]

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

        def __init__(self, keys=None, iteration_list=None,
                     note_names=None, note_numbers=None, note_indices=None,
                     previous_note_indices=None,
                     step_trend=None, step_size=None,
                     intervals=None, mistakes_counter=None,
                     number_of_notes=None,
                     step_size_level=None, phase=None,
                     intervals_level=None, number_of_notes_level=None, user=None):

            self.max_level = constants.max_level_func(
                keys=keys, step_size=None, intervals=None,
                number_of_notes=None, step_size_level=None,
                number_of_notes_level=None, interval_level=None)

            self.level = self.Level(iteration_list=iteration_list,
                                    mistakes_counter=mistakes_counter,
                                    keys=keys,
                                    phase=phase,
                                    max_level=self.max_level,
                                    step_size=step_size,
                                    intervals=intervals,                                     number_of_notes=number_of_notes,
                                    step_size_level=step_size_level,
                                    number_of_notes_level=number_of_notes_level,
                                    interval_level=intervals_level,
                                    user=user)

            if constants.show_phase:
                print('phase = ' + phase)
            # self.size = None
            self.step = None
            # self.notes = self.Note(names=note_names, numbers=note_numbers, indices=note_indices)
            self.notes = []
            self.number_of_notes = number_of_notes

            if number_of_notes is None:
                self.number_of_notes = np.random.choice(
                    np.arange(1, 1 + constants.max_chord_size), 1,
                    p=constants.levels.number_of_notes[self.level.number_of_notes, :])
                self.number_of_notes = self.number_of_notes[0]

            intervals = self.create_none_list_if_necessary(list_or_none=intervals, size=self.number_of_notes - 1)
            note_names = self.create_none_list_if_necessary(list_or_none=note_names, size=self.number_of_notes)
            note_numbers = self.create_none_list_if_necessary(list_or_none=note_numbers, size=self.number_of_notes)
            note_indices = self.create_none_list_if_necessary(list_or_none=note_indices, size=self.number_of_notes)

            while True:
                for i in range(self.number_of_notes):
                    if i == 0:
                        self.set_chord_step_and_bottom_note(keys=keys,
                                                            previous_note_indices=previous_note_indices, i=i,
                                                            note_names=note_names, note_numbers=note_numbers,
                                                            note_indices=note_indices,
                                                            step_trend=step_trend, step_size=step_size,
                                                            level=self.level)
                    elif i >= 1:
                        self.set_interval_and_non_bottom_note(
                            index_in_chord=i, keys=keys,
                            note_names=note_names, note_numbers=note_numbers, note_indices=note_indices,
                            intervals=intervals,
                            level=self.level)
                indices = [note.index for note in self.notes]
                if all(index in constants.keys.white.indices for index in indices):
                    break
                else:
                    self.notes = []
                    pass

        def set_chord_step_and_bottom_note(
                self, previous_note_indices, i, keys,
                note_names=None, note_numbers=None, note_indices=None,
                step_trend=None, step_size=None,
                level=None):
            note_is_literally_defined = \
                note_indices[i] is not None or \
                note_names[i] is not None or \
                note_numbers[i] is not None
            step_is_literally_defined = step_size is not None or step_trend is not None
            if note_is_literally_defined:
                # if not step_is_literally_defined:
                self.notes.append(self.Note(keys=keys, index=note_indices[i],
                                            number=note_numbers[i],
                                            name=note_names[i]))
                self.step = self.Step(keys=keys,
                                 current_index=note_indices[i],
                                 previous_index=previous_note_indices[i])
            else:
                while True:
                    if step_is_literally_defined:
                        self.step = self.Step(keys=keys, size=step_size,
                                         trend=step_trend)
                    else:
                        self.step = self.Step(keys=keys, difficulty_level=level.step_size)
                    new_bottom_index = previous_note_indices[0] + \
                                       (self.step.size - 1) * self.step.trend
                    if 0 <= new_bottom_index < len(constants.keys.white.numbers) / 2:
                        self.notes.append(self.Note(keys=keys, index=new_bottom_index))
                        break

        def set_interval_and_non_bottom_note(
                self, index_in_chord, keys,
                note_names=None, note_numbers=None, note_indices=None,
                intervals=None,
                level=None):
            note_is_literally_defined = \
                note_indices[index_in_chord] is not None or \
                note_names[index_in_chord] is not None or \
                note_numbers[index_in_chord] is not None
            if note_is_literally_defined:
                # if intervals[index_in_chord - 1] is None:
                self.notes.append(self.Note(keys=keys, index=note_indices[index_in_chord],
                                            number=note_numbers[index_in_chord],
                                            name=note_names[index_in_chord]))
                intervals[index_in_chord - 1] = self.notes[-1].index - self.notes[-2].index + 1
            else:
                if intervals[index_in_chord - 1] is None:
                    p = getattr(constants.levels.intervals, keys)
                    p = p[level.intervals, :]
                    x = getattr(constants.keys, keys)
                    x = len(x.names) + 2
                    intervals[index_in_chord - 1] = np.random.choice(
                        np.arange(2, x), 1, p=p)
                lower_note = self.notes[index_in_chord - 1].index
                note_index = lower_note + intervals[index_in_chord - 1] - 1
                self.notes.append(self.Note(keys=keys, index=note_index))

    class Response:
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
                self.autoregressive = None  # constants.optimal_response_time

        def __init__(self, number_of_notes):
            self.text = 'C'
            self.type = 'repeat'
            # self.flag = self.Flag()
            self.time = self.Time(number_of_notes=number_of_notes)

    class Attributes:
        def __init__(self, request_response,
                     error_state=initial.error_state
                     ):
            # self.error_state = error_state
            self.request_response = request_response

    class Volume:
        def __init__(self):
            self.value = round((constants.max_volume + constants.min_volume) / 2)
            self.trend = (-1) ** np.random.binomial(1, 0.5)

    @staticmethod
    def get_number_of_notes_intervals_and_step_size_from_literals(intervals, step_size, step_trend,
                                                                  iteration_list,
                                                                  note_names, note_numbers, note_indices,
                                                                  number_of_notes, number_of_notes_level):
        # The following "list of lists" made sense when the code was written
        # in a polyphonic way. We had several co-existing melodic lines,
        # each with its own "step trend" and "step size".
        # However, since then I have decided that it would make more sense to
        # write this code with a harmony state of mind.
        # The "chord" class will have the "step" class and a list of "note" objects
        # as attributes. The "step" will be an attribute of the chord and will refer
        # to the step of the bottom note.
        # I use the term "bottom note" rather than 'bass' since it may be quite high.
        # list_of_lists = {'step_trends': step_trends,
        #                  'step_sizes': step_sizes,
        #                  'note_names': note_names,
        #                  'note_numbers': note_numbers,
        #                  'note_indices': note_indices}
        note_attributes = {'note_names': note_names,
                           'note_numbers': note_numbers,
                           'note_indices': note_indices}
        note_attributes = {k: v for k, v in note_attributes.items() if v is not None}

        if len(note_attributes) is not 0:
            for key, a_list in note_attributes.items():
                number_of_notes = len(a_list)
        elif intervals is not None:
            number_of_notes = len(intervals) + 1

        if note_indices is not None:
            if None not in note_indices:
                if intervals is None:
                    note_indices = np.array(note_indices)
                    intervals = note_indices[1:] - note_indices[:-1] + 1
                    intervals = intervals.tolist()
            if note_indices[0] is not None:
                if step_size is None:
                    if len(iteration_list) >= 1:
                        previous_bottom_note_index = iteration_list[-1].question.notes[0].index
                    else:
                        previous_bottom_note_index = initial.indices[0]
                    step = note_indices[0] - previous_bottom_note_index + 1
                    # step = step[0]
                    step_size = abs(step)
                    step_trend = np.sign(step_size)

        return number_of_notes, intervals, step_size, step_trend

    def request_response(self, accept_with_spaces, accept_without_spaces):
        note_numbers = [note.number for note in self.question.notes]
        volume = self.volume.value
        question_start_time = time.time()
        self.response.text = input("Identify Note:")
        self.response.text = self.response.text.strip()
        self.response.time.raw = time.time() - question_start_time
        response_time_now_fraction = self.response.time.raw - np.round(self.response.time.raw)
        time.sleep(constants.quarter_note_time - response_time_now_fraction)
        # note_numbers = [note.number for note in iteration.chord.notes]
        for number in note_numbers:
            constants.mo.send_message([constants.note_off,
                                       number, volume])
        self.response.text = self.response.text.upper()
        self.set_response_time_to_nan_if_incorrect(
            accept_with_spaces, accept_without_spaces)
        termination_flag = self.check_user_response_at_question_end(
            accept_with_spaces=accept_with_spaces,
            accept_without_spaces= accept_without_spaces)
        return termination_flag

    def set_response_time_to_nan_if_incorrect(self, accept_with_spaces, accept_without_spaces):
        is_incorrect = True
        note_names = [note.name for note in self.question.notes]
        if accept_without_spaces:
            if self.response.text == ''.join(note_names):
                is_incorrect = False
        if accept_with_spaces:
            if self.response.text == ' '.join(note_names):
                is_incorrect = False
        if is_incorrect:
            self.response.time.raw = np.nan

    def check_user_response_at_question_end(self, accept_with_spaces, accept_without_spaces):
        termination_flag = False
        note_names = [note.name for note in self.question.notes]
        is_correct = False
        if accept_without_spaces:
            if self.response.text == ''.join(note_names):
                is_correct = True
        if accept_with_spaces:
            if self.response.text == ' '.join(note_names):
                is_correct = True
        if is_correct:
            self.response.type = True
            print(colored("Good :-)", 'blue'))
        elif self.response.text == 'END':
            self.response.type = 'end'
            termination_flag = True
        elif self.response.text == 'RESTART':
            self.response.type = 'restart'
            print(colored("OK, RESTART: :-)", 'green'))
            raise Exception('need to implement RESTART with "intro"')
            # intro()
        elif self.response.text == 'REPEAT':
            self.response.type = 'repeat'
        else:  # user error
            self.response.type = False
            print(colored("Bad :-)", 'red'))
        return termination_flag

    @staticmethod
    def intro(x=1):
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

    def __init__(self, iteration_list, phase,
                 mistakes_counter, user,
                 request_response=True,
                 play_intro=True,
                 keys='white',
                 note_names=None, note_numbers=None, note_indices=None,
                 step_trend=None, step_size=None,
                 intervals=None,
                 number_of_notes=None,
                 number_of_notes_level=None,
                 intervals_level=None,
                 step_size_level=None):
        # keys = keys.upper()
        self.phase = phase
        note_attributes = {'names': note_names,
                           'numbers': note_numbers,
                           'indices': note_indices}
        note_attributes = {k: v for k, v in note_attributes.items() if v is not None}

        raise_exceptions.chord_literals(note_attributes=note_attributes,
                                                                  number_of_notes=number_of_notes,
                                                                  intervalsssss=intervals,
                                                                  step_sizeeeeeeeee=step_size,
                                                                  step_trendddddddddd=step_trend,
                                                                  config_key=keys)

        raise_exceptions.level_literals(number_of_notes_level=number_of_notes_level,
                                        intervals_levellllllll=intervals_level,
                                        step_size_levellllllllll=step_size_level)

        raise_exceptions.chord_vs_level_literals(note_attributesssssss=note_attributes,
                                                 step_sizesssssssss=step_size,
                                                 intervalsssssssss=intervals,
                                                 number_of_notes=number_of_notes,
                                                 number_of_notes_level=number_of_notes_level,
                                                 intervals_levellllllllll=intervals_level,
                                                 step_size_levelllllllll=step_size_level)

        number_of_notes, _, _, _ = \
            self.get_number_of_notes_intervals_and_step_size_from_literals(
                iteration_list=iteration_list,
                step_size=step_size, step_trend=step_trend,
                intervals=intervals, note_numbers=note_numbers,
                note_indices=note_indices, note_names=note_names,
                number_of_notes=number_of_notes,
                number_of_notes_level=number_of_notes_level)

        if len(iteration_list) == 0:
            if play_intro:
                self.intro(x=2)
            self.question = self.Question(phase=phase, iteration_list=iteration_list,
                                          mistakes_counter=mistakes_counter, keys=keys,
                                          previous_note_indices=initial.indices(keys=keys),
                                          intervals=intervals,
                                          note_numbers=note_numbers,
                                          note_indices=note_indices,
                                          note_names=note_names,
                                          step_size=step_size,
                                          step_trend=step_trend,
                                          number_of_notes=number_of_notes,
                                          step_size_level=step_size_level,
                                          intervals_level=intervals_level,
                                          number_of_notes_level=number_of_notes_level,
                                          user=user)
        elif len(iteration_list) == 1:
            previous_note_indices = [note.index for note in iteration_list[-1].question.notes]
            if iteration_list[-1].response.type is True:
                self.question = self.Question(phase=phase, iteration_list=iteration_list,
                                              mistakes_counter=mistakes_counter, keys=keys,
                                              previous_note_indices=previous_note_indices,
                                              intervals=intervals,
                                              note_numbers=note_numbers,
                                              note_indices=note_indices,
                                              note_names=note_names,
                                              step_size=step_size,
                                              step_trend=step_trend,
                                              number_of_notes=number_of_notes,
                                              step_size_level=step_size_level,
                                              intervals_level=intervals_level,
                                              number_of_notes_level=number_of_notes_level,
                                              user=user)
            elif iteration_list[-1].response.type is False:
                self.question = self.Question(phase=phase, iteration_list=iteration_list,
                                              mistakes_counter=mistakes_counter, keys=keys,
                                              previous_note_indices=previous_note_indices,
                                              note_indices=initial.indices(keys=keys),
                                              number_of_notes=len(initial.indices(keys=keys)))
        elif len(iteration_list) >= 2:
            previous_note_indices = [note.index for note in iteration_list[-1].question.notes]
            if iteration_list[-1].response.type is True:
                self.question = self.Question(phase=phase, iteration_list=iteration_list,
                                              mistakes_counter=mistakes_counter,
                                              keys=keys, previous_note_indices=previous_note_indices,
                                              intervals=intervals,
                                              note_numbers=note_numbers,
                                              note_indices=note_indices,
                                              note_names=note_names,
                                              step_size=step_size,
                                              step_trend=step_trend,
                                              number_of_notes=number_of_notes,
                                              step_size_level=step_size_level,
                                              intervals_level=intervals_level,
                                              number_of_notes_level=number_of_notes_level,
                                              user=user)
            elif iteration_list[-1].response.type is False:
                if iteration_list[-2].response.type is True:
                    note_indices = [note.index for note in iteration_list[-2].question.notes]
                    self.question = self.Question(phase=phase, iteration_list=iteration_list,
                                                  mistakes_counter=mistakes_counter,
                                                  keys=keys, note_indices=note_indices,
                                                  previous_note_indices=previous_note_indices,
                                                  number_of_notes=len(note_indices))
                elif iteration_list[-2].response.type is False:
                    if play_intro:
                        self.intro(x=2)
                    self.question = self.Question(phase=phase, iteration_list=iteration_list,
                                                  mistakes_counter=mistakes_counter,
                                                  keys=keys, previous_note_indices=initial.indices(keys=keys),
                                                  intervals=intervals,
                                                  note_numbers=note_numbers,
                                                  note_indices=note_indices,
                                                  note_names=note_names,
                                                  step_size=step_size,
                                                  step_trend=step_trend,
                                                  number_of_notes=number_of_notes,
                                                  step_size_level=step_size_level,
                                                  intervals_level=intervals_level,
                                                  number_of_notes_level=number_of_notes_level,
                                                  user=user)

        self.response = self.Response(number_of_notes=self.question.number_of_notes)
        self.volume = self.Volume()
        self.attributes = self.Attributes(request_response)

    def play_chord(self, iteration_list):
        # if self.chord is None:
        #     self = set_chord(self, iteration_list)
        #     self = set_volume(self, iteration_list)
        if constants.reveal:
            note_numbers = [note.number for note in self.question.notes]
            print(note_numbers)
            note_names = [note.name for note in self.question.notes]
            print(note_names)
        try:
            numbers = [note.number for note in self.question.notes]
            for number in numbers:
                constants.mo.send_message([constants.note_on,
                                           number, self.volume.value])

        except:
            raise Exception('"high_level_classes" says: '
                            'I can not play these notes.')
        if not self.attributes.request_response:
            time.sleep(constants.quarter_note_time)
            for number in self.question.numbers:
                constants.mo.send_message([rtmidi.midiconstants.NOTE_OFF,
                                           number, self.volume.value])

while not termination_flag:
    iteration = Iteration(request_response=request_response,
                          keys=keys,
                          play_intro=play_intro,
                          iteration_list=iteration_list,
                          number_of_notes=number_of_notes,
                          step_size=step_size, step_trend=step_trend,
                          phase=phase, intervals=intervals,
                          mistakes_counter=mistakes_counter,
                          user=user)
    while iteration.response.type == 'repeat':
        iteration.play_chord(iteration_list)
        termination_flag = iteration.request_response(
            accept_with_spaces=accept_with_spaces,
            accept_without_spaces=accept_without_spaces)
    if iteration.response.type is False:
        # phase = 'steady state'
        mistakes_counter = mistakes_counter + 1
    iteration_list.append(iteration)

constants.mo.close_port()


if None not in [number_of_notes, step_size, intervals]:
    file_name = 'response_times//response_times_number_of_notes_' + str(number_of_notes) + '.p'
    if os.path.exists(file_name):
        response_times_old = pickle.load(open(file_name, "rb"))
    else:
        response_times_old = []
    response_times = [iteration.response.time.raw for iteration in iteration_list]
    response_times = response_times_old + response_times
    pickle.dump(response_times, open(file_name, "wb"))
else:
    iteration_list = iteration_list[:-1]
    with open('question lists\\iteration_list.pkl', 'wb') as output:
        pickle.dump(iteration_list, output, pickle.HIGHEST_PROTOCOL)
    with open('users levels\\' + user + '.pkl', 'wb') as output:
        pickle.dump(iteration_list[-1].question.level.total, output, pickle.HIGHEST_PROTOCOL)
    plot_functions.my_plot(iteration_list=iteration_list, keys=keys)


print('this is the end of MAIN')
