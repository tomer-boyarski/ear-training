import numpy as np
import constants
from archive.get_number_of_notes_intervals_and_step_size_from_literals import get_number_of_notes_intervals_and_step_size_from_literals
from create_None_list_if_necessary import create_none_list_if_necessary
from note_02 import Note
from step import Step
import initial


class Chord:
    def __init__(self, question_list, request_response=True,
                 note_names=None, note_numbers=None, note_indices=None,
                 step_trend=None, step_size=None,
                 chord_range=None, intervals=None,
                 number_of_notes=None,
                 level=None):
        self.number_of_notes = get_number_of_notes_intervals_and_step_size_from_literals(intervals=intervals,
                                                                                         note_numbers=note_numbers,
                                                                                         note_indices=note_indices,
                                                                                         note_names=note_names,
                                                                                         step_sizes=step_size,
                                                                                         step_trends=step_trend,
                                                                                         number_of_notes=number_of_notes,
                                                                                         level=level)
        # step_trend = create_none_list_if_necessary(list_or_none=step_trend, size=self.number_of_notes)
        # step_size = create_none_list_if_necessary(list_or_none=step_size, size=self.number_of_notes)
        note_names = create_none_list_if_necessary(list_or_none=note_names, size=self.number_of_notes)
        note_numbers = create_none_list_if_necessary(list_or_none=note_numbers, size=self.number_of_notes)
        note_indices = create_none_list_if_necessary(list_or_none=note_indices, size=self.number_of_notes)
        notes = []
        for i in range(self.number_of_notes):
            note_is_literally_defined = \
                note_indices[i] is not None or \
                note_names[i] is not None or \
                note_numbers[i] is not None
            if i == 0:
                step_is_literally_defined = step_size is not None or step_trend is not None
                if note_is_literally_defined:
                    if step_is_literally_defined:
                        raise Exception('bottom note is over-defined')
                    elif not step_is_literally_defined:
                        notes.append(Note(index=note_indices[i],
                                          number=note_numbers[i],
                                          name=note_names[i]))
                        if len(question_list) >= 1:
                            self.step = Step(current_index=note_indices[i],
                                             previous_index=question_list[-1].question.notes.index[i])
                        else:
                            self.step = Step(current_index=note_indices[i],
                                             previous_index=initial.indices)
                elif not note_is_literally_defined:
                    if step_is_literally_defined:
                        self.step = Step(size=step_size,
                                         trend=step_trend)
                        if len(question_list) >= 1:
                            previous_bottom_index = question_list[-1].question.notes.index[i]
                        elif len(question_list) == 0:
                            previous_bottom_index = initial.indices
                        new_bottom_index = previous_bottom_index + \
                            self.step.size * self.step.trend - 1
                        notes.append(Note(index=new_bottom_index))
                    elif not step_is_literally_defined:
                        # randomize
                        pass
            elif i >= 1:
                if note_is_literally_defined:
                    if intervals[i-1] is not None:
                        raise Exception('non-bottom note is over-defined')
                    elif intervals[i-1] is None:
                        notes.append(Note(index=note_indices[i],
                                          number=note_numbers[i],
                                          name=note_names[i]))
                        intervals[i-1] = notes[-1].index - notes[-2].index + 1
                elif not note_is_literally_defined:
                    if intervals[i-1] is not None:
                        notes.append(Note(note_indices[i-1] + intervals[i-1] - 1))
                    elif intervals[i-1] is None:
                        # randomize
                        pass



        # bottom_note = True
        for note_index, note_name, note_number, \
            step_size, step_trend \
                in zip(note_indices, note_names, note_numbers,
                       step_size, step_trend):
            self.notes.append(Note(question_list,
                                   index=note_index,
                                   name=note_name,
                                   number=note_number,
                                   step_size=step_size,
                                   step_trend=step_trend,
                                   bottom_note=bottom_note))

        self.size = None
        self.indices = None
        self.names = None
        self.numbers = None
        if indices is not None:
            self.initialize_with_indices(indices)
        elif names is not None:
            self.initialize_with_names(names)
        elif numbers is not None:
            self.initialize_with_numbers(numbers)
        self.range = np.max(self.indices) - np.min(self.indices) +1

    def initialize_with_indices(self, indices):
        self.indices = np.array(indices)
        self.size = len(indices)
        self.numbers = constants.note_numbers_C_to_C[indices]
        self.names = [constants.note_names_major_C_scale[number % 12] for number in self.numbers]

    def initialize_with_numbers(self, numbers):
        self.numbers = np.array(numbers)
        self.size = len(numbers)
        self.indices = np.in1d(
            constants.note_numbers_C_to_C,
            numbers).nonzero()[0]
        self.names = [constants.note_names_major_C_scale[number % 12] for number in self.numbers]

    def initialize_with_names(self, names):
        self.names = names
        self.size = len(names)
        self.numbers = [constants.name_to_number_dictionary[name] for name in names]
        self.numbers = np.array(self.numbers)
        self.indices = np.in1d(
            constants.note_numbers_C_to_C,
            self.numbers).nonzero()[0]
