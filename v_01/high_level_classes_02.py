from low_level_classes_02 import *
from chord_02 import Chord
from level import Level
from note_01 import Note
import initial
from set_chord import set_chord
from set_volume import set_volume
from get_number_of_notes_from_literals import get_number_of_notes_intervals_and_step_size_from_literals
import raise_exceptions
import rtmidi
import time
from intro import intro
from create_None_list_if_necessary import create_none_list_if_necessary


class Iteration:
    def __init__(self, question_list, request_response=True,
                 key='MAJOR',
                 note_names=None, note_numbers=None, note_indices=None,
                 step_trend=None, step_size=None,
                 chord_range=None, intervals=None,
                 number_of_notes=None,
                 number_of_notes_level=None,
                 intervals_level=None,
                 step_size_level=None):
        key = key.upper()
        note_attributes = {'names': note_names,
                           'numbers': note_numbers,
                           'indices': note_indices}
        note_attributes = {k: v for k, v in note_attributes.items() if v is not None}

        raise_exceptions.chord_literals(note_attributes=note_attributes,
                                        number_of_notes=number_of_notes,
                                        intervals=intervals,
                                        key=key)

        raise_exceptions.level_literals(number_of_notes_level=number_of_notes_level,
                                        intervals_level=intervals_level,
                                        step_size_level=step_size_level)

        raise_exceptions.chord_vs_level_literals(note_attributes=note_attributes,
                                                 step_size=step_size,
                                                 intervals=intervals,
                                                 number_of_notes=number_of_notes,
                                                 number_of_notes_level=number_of_notes_level,
                                                 intervals_level=intervals_level,
                                                 step_size_level=step_size_level)

        number_of_notes, intervals, _ = \
            get_number_of_notes_intervals_and_step_size_from_literals(question_list=question_list,
                                                                      step_size=step_size,
                                                                      intervals=intervals,
                                                                      note_numbers=note_numbers,
                                                                      note_indices=note_indices,
                                                                      note_names=note_names,
                                                                      number_of_notes=number_of_notes,
                                                                      number_of_notes_level=number_of_notes_level)
        self.max_level = constants.max_level(step_size=None,
                                        intervals=None,
                                        number_of_notes=None,
                                        step_size_level=None,
                                        number_of_notes_level=None,
                                        interval_level=None)

        self.level = Level(question_list,
                           max_level=self.max_level,
                           step_size=step_size,
                           intervals=intervals,
                           number_of_notes=number_of_notes,
                           step_size_level=step_size_level,
                           number_of_notes_level=number_of_notes_level,
                           interval_level=intervals_level)

        if len(question_list) == 0:
            intro(x=2)
            self.chord = Chord(previous_note_indices=initial.indices,
                               intervals=intervals,
                               note_numbers=note_numbers,
                               note_indices=note_indices,
                               note_names=note_names,
                               step_size=step_size,
                               step_trend=step_trend,
                               number_of_notes=number_of_notes,
                               level=self.level)
        elif len(question_list) == 1:
            previous_note_indices = [note.index for note in question_list[-1].question.notes]
            if question_list[-1].response.type:
                self.chord = Chord(previous_note_indices=previous_note_indices,
                                   intervals=intervals,
                                   note_numbers=note_numbers,
                                   note_indices=note_indices,
                                   note_names=note_names,
                                   step_size=step_size,
                                   step_trend=step_trend,
                                   number_of_notes=number_of_notes,
                                   level=self.level)
            elif not question_list[-1].response.type:
                self.chord = Chord(previous_note_indices=previous_note_indices,
                                   note_indices=initial.indices,
                                   number_of_notes=len(initial.indices))
        elif len(question_list) >= 2:
            previous_note_indices = [note.index for note in question_list[-1].question.notes]
            if question_list[-1].response.type:
                self.chord = Chord(previous_note_indices=previous_note_indices,
                                   intervals=intervals,
                                   note_numbers=note_numbers,
                                   note_indices=note_indices,
                                   note_names=note_names,
                                   step_size=step_size,
                                   step_trend=step_trend,
                                   number_of_notes=number_of_notes,
                                   level=self.level)
            elif not question_list[-1].response.type:
                if question_list[-2].response.type:
                    note_indices = [note.index for note in question_list[-2].question.notes]
                    self.chord = Chord(note_indices=note_indices,
                                       previous_note_indices=previous_note_indices,
                                       number_of_notes=len(note_indices))
                elif not question_list[-2].response.type:
                    intro(x=2)
                    self.chord = Chord(previous_note_indices=initial.indices,
                                       intervals=intervals,
                                       note_numbers=note_numbers,
                                       note_indices=note_indices,
                                       note_names=note_names,
                                       step_size=step_size,
                                       step_trend=step_trend,
                                       number_of_notes=number_of_notes,
                                       level=self.level)

        self.response = Response(number_of_notes=self.chord.number_of_notes)
        self.volume = Volume()
        self.attributes = Attributes(request_response)

    def play_chord(self, question_list):
        if self.chord is None:
            self = set_chord(self, question_list)
            self = set_volume(self, question_list)
        if constants.reveal:
            note_numbers = [note.number for note in self.chord.notes]
            print(note_numbers)
            note_names = [note.name for note in self.chord.notes]
            print(note_names)
        try:
            numbers = [note.number for note in self.chord.notes]
            for number in numbers:
                constants.mo.send_message([rtmidi.midiconstants.NOTE_ON,
                                           number, self.volume.value])
        except:
            raise Exception('"high_level_classes" says: '
                            'I can not play these notes.')
        if not self.attributes.request_response:
            time.sleep(constants.quarter_note_time)
            for number in self.chord.numbers:
                constants.mo.send_message([rtmidi.midiconstants.NOTE_OFF,
                                           number, self.volume.value])