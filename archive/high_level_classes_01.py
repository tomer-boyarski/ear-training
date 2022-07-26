# from low_level_classes_02 import *
from archive.chord_02 import Chord
from archive.level import Level
import initial
# from set_difficulty_distribution import set_difficulty_distribution
from archive.set_chord import set_chord
from set_volume import set_volume
from archive.get_number_of_notes_intervals_and_step_size_from_literals import get_number_of_notes_intervals_and_step_size_from_literals
import rtmidi
import time


class Iteration:
    def __init__(self, question_list, request_response=True,
                 note_names=None, note_numbers=None, note_indices=None,
                 step_trend=None, step_size=None,
                 chord_range=None, intervals=None,
                 number_of_notes=None,
                 level=None):

        # raise_exceptions.iteration(
        #     chord=chord, step_sizes=step_sizes,
        #     step_trends=step_trends,
        #     intervals=intervals, chord_range=chord_range)
        self.number_of_notes = get_number_of_notes_intervals_and_step_size_from_literals(intervals=intervals,
                                                                                         note_numbers=note_numbers,
                                                                                         note_indices=note_indices,
                                                                                         note_names=note_names,
                                                                                         step_sizes=step_size,
                                                                                         step_trends=step_trend,
                                                                                         number_of_notes=number_of_notes,
                                                                                         level=level)
        self.level = level if level is not None else Level()

        self.chord = Chord(intervals=intervals,
                           note_numbers=note_numbers,
                           note_indices=note_indices,
                           note_names=note_names,
                           step_size=step_size,
                           step_trend=step_trend,
                           number_of_notes=number_of_notes,
                           level=self.level)


        # bottom =

        # list_of_lists = {k: create_none_list_if_necessary(v) for k, v in list_of_lists.items()}

        # if chord.size is not None:
        #     print('Chord size manual input.')
        # if (sizes is not None or trends is not None) and current_indices is not None:
        #     raise Exception('step object is over-defined')
        # if current_indices is None and previous_indices is not None:
        #     raise Exception('There is no need to input previous indices \
        #                      to step object if current indices are as of yet unknown')
        self.chord = None
        self.step = None
        if chord is not None:
            self.initialize_with_chord(chord, question_list)
        # self.chord = Chord(indices=[7]) if chord is None else chord
        # self.chord = chord if chord is not None else Chord()
        # self.chord = Chord(numbers=[60]) if chord is None else chord
        # if step is not None:
        #     self.step = step
        # elif step is None:
        #
        #
        self.response = Response()
        self.volume = Volume()
        self.attributes = Attributes(request_response)



    def initialize_with_chord(self, chord, question_list):
        self.chord = chord
        self.step = Step()
        if len(question_list) == 0:
            self.step = Step(previous_indices=initial.indices,
                             current_indices=chord.index)
        elif len(question_list) >= 1:
            self.step = Step(previous_indices=question_list[-1].question.index,
                             current_indices=chord.index)

    def play_chord(self, question_list):
        if self.chord is None:
            self = set_difficulty_distribution(self, question_list)
            self = set_chord(self, question_list)
            self = set_volume(self, question_list)
        if constants.reveal:
            print(self.chord.numbers)
            print(self.chord.names)
        try:
            for number in self.chord.numbers:
                constants.mo.send_message([rtmidi.midiconstants.NOTE_ON,
                                           number, self.volume.value])
        except:
            print('stop')
        if not self.attributes.request_response:
            time.sleep(constants.quarter_note_time)
            for number in self.chord.numbers:
                constants.mo.send_message([rtmidi.midiconstants.NOTE_OFF,
                                           number, self.volume.value])

# class Answer:
#     def __init__(self, question):
