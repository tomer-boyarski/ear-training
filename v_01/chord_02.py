import numpy as np
import constants
from get_number_of_notes_from_literals import get_number_of_notes_intervals_and_step_size_from_literals
from create_None_list_if_necessary import create_none_list_if_necessary
from note_02 import Note
from step import Step
import initial


class Chord:
    def __init__(self,
                 note_names=None, note_numbers=None, note_indices=None,
                 previous_note_indices=None,
                 step_trend=None, step_size=None,
                 intervals=None,
                 number_of_notes=None,
                 level=None):
        self.size = None
        self.step = None
        self.notes = []
        self.number_of_notes = number_of_notes

        if number_of_notes is None:
            if level.number_of_notes == 1:
                print('level.number_of_notes == 1')
            self.number_of_notes = np.random.choice(
                np.arange(1, 1 + constants.max_chord_size), 1,
                p=constants.levels.number_of_notes[level.number_of_notes, :])
            self.number_of_notes = self.number_of_notes[0]

        note_names = create_none_list_if_necessary(list_or_none=note_names, size=self.number_of_notes)
        note_numbers = create_none_list_if_necessary(list_or_none=note_numbers, size=self.number_of_notes)
        note_indices = create_none_list_if_necessary(list_or_none=note_indices, size=self.number_of_notes)
        intervals = create_none_list_if_necessary(list_or_none=intervals, size=self.number_of_notes-1)

        while True:
            for i in range(self.number_of_notes):
                if i == 0:
                    self.set_chord_step_and_bottom_note(
                        previous_note_indices=previous_note_indices, i=i,
                        note_names=note_names, note_numbers=note_numbers, note_indices=note_indices,
                        step_trend=step_trend, step_size=step_size,
                        level=level)
                elif i >= 1:
                    self.set_interval_and_non_bottom_note(
                        index_in_chord=i,
                        note_names=note_names, note_numbers=note_numbers, note_indices=note_indices,
                        intervals=intervals,
                        level=level)
            if self.notes[-1].index < len(constants.white_note.number) and \
                    self.notes[0].index >= 0:
                break

    def set_chord_step_and_bottom_note(
            self, previous_note_indices, i,
            note_names=None, note_numbers=None, note_indices=None,
            step_trend=None, step_size=None,
            level=None):
        note_is_literally_defined = \
            note_indices[i] is not None or \
            note_names[i] is not None or \
            note_numbers[i] is not None
        step_is_literally_defined = step_size is not None or step_trend is not None
        if note_is_literally_defined:
            if step_is_literally_defined:
                raise Exception('bottom note is over-defined')
            else:
                self.notes.append(Note(index=note_indices[i],
                                  number=note_numbers[i],
                                  name=note_names[i]))
                self.step = Step(current_index=note_indices[i],
                                 previous_index=previous_note_indices[i])
        else:
            while True:
                if step_is_literally_defined:
                    self.step = Step(size=step_size,
                                     trend=step_trend)
                else:
                    self.step = Step(difficulty_level=level.step_size)
                new_bottom_index = previous_note_indices[0] + \
                                   (self.step.size - 1) * self.step.trend
                if 0 <= new_bottom_index < len(constants.white_note.number):
                    self.notes.append(Note(index=new_bottom_index))
                    break

    def set_interval_and_non_bottom_note(
            self, index_in_chord,
            note_names=None, note_numbers=None, note_indices=None,
            intervals=None,
            level=None):
        note_is_literally_defined = \
            note_indices[index_in_chord] is not None or \
            note_names[index_in_chord] is not None or \
            note_numbers[index_in_chord] is not None
        if note_is_literally_defined:
            if intervals[index_in_chord - 1] is not None:
                raise Exception('non-bottom note is over-defined')
            else:
                self.notes.append(Note(index=note_indices[index_in_chord],
                                       number=note_numbers[index_in_chord],
                                       name=note_names[index_in_chord]))
                intervals[index_in_chord - 1] = self.notes[-1].index - self.notes[-2].index + 1
        else:
            if intervals[index_in_chord - 1] is  None:
                intervals[index_in_chord - 1] = np.random.choice(
                    np.arange(2, 9), 1, p=constants.levels.intervals[level.intervals, :]
                )
            lower_note = self.notes[index_in_chord - 1].index
            note_index = lower_note + intervals[index_in_chord - 1] - 1
            self.notes.append(Note(index=note_index))
