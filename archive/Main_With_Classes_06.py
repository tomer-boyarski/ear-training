# See problem with distribution of new note index


import rtmidi.midiconstants
import numpy as np
from termcolor import colored
import matplotlib.pyplot as plt
import time
import seaborn as sns
import pickle
import helper_functions_01
import constants
from collections import namedtuple
from recordclass import recordclass


time_beginning_of_program = time.time()

my_velocity = 127

cubic_polynomial_mapping_coefficients = helper_functions.cubic_polynomial_mapping()


class Question:
    # class Note:
    #     def __init__(self):
    #         self.name = None
    #         self.numbers = None
    #         self.index = constants.note_index_initialization

    def __init__(self, previous_question_attributes,
                 step_size_level,
                 slow_state,
                 error_state, penultimate_note_index,
                 ):
        self.question_index = previous_question_attributes.question_index + 1
        self.previous_question_attributes = previous_question_attributes
        self.step_size_level = step_size_level
        self.step_size = None
        self.step_direction = constants.step_direction_initialization
        self.constants = constants
        Note = recordclass('Note', 'name numbers index')
        self.note = Note(name=None, number=None, index=constants.note_index_initialization)
        # With class rather than recordclass
        # self.note = self.Note()
        self.identified_note = None
        ResponseTime = recordclass('ResponseTime', 'raw autoregressive')
        self.response_time = ResponseTime(raw=np.nan, autoregressive=constants.optimal_response_time)
        # self.response_time = np.nan
        # self.autoregressive_response_time =
        self.slow_state = slow_state
        self.slow_answer_in_this_question = None
        self.error_state = error_state
        self.penultimate_note_index = penultimate_note_index
        self.Termination_Flag = False
        self.volume = constants.initial_volume
        self.volume_change = 1
        # self.markovian_attributes.question_index += 1

        self.True_or_False = np.nan

        # self.markovian_attributes = previous_question_index + 1

    def get_new_question_attributes(self):
        print('level = ' + str(self.step_size_level))
        if self.error_state == 'Just Made an Error' or \
                self.error_state == 'Error in Previous Question':
            self.note.index = self.penultimate_note_index
            self.step_size = self.penultimate_note_index - \
                self.previous_question_attributes.note_index
            self.step_direction = np.sign(self.step_size)
        elif self.error_state == 'No Recent Errors':
            if not self.slow_state:
                # self.set_step_size_old()
                self.set_step_size()
                self.set_step_direction_and_new_note()
            else:
                self.note.index = self.previous_question_attributes.question.index
                self.step_size = 0
                self.step_direction = 1
        self.note.number = constants.note_numbers_C_to_C[self.note.index]
        self.note.name = constants.note_names_chromatic_C_scale[self.note.number % 12]

    def set_step_size_old(self):
        max_step_size_now = self.step_size_level
        if max_step_size_now > 0:
            step_size = np.random.randint(1, max_step_size_now + 1, 1)
            step_size = step_size[0]
            if np.random.binomial(1, 1 / 4 / max_step_size_now):
                step_size = 0
        elif max_step_size_now == 0:
            step_size = 0
        self.step_size = step_size

    def set_step_size(self):
        self.step_size = np.random.choice(np.arange(8), 1, p=constants.levels[self.step_size_level, :])[0]
        if 0 > self.step_size or self.step_size > 7:
            print('step size too big or too small')

    def set_step_direction_and_new_note(self):
        while True:
            self.step_direction = self.binary_markov_chain(
                constants.probability_of_same_step_direction,
                self.previous_question_attributes.step_direction)
            self.note.index = self.previous_question_attributes.note_index + \
                              self.step_size * self.step_direction
            if 0 <= self.note.index <= 14:
                break

    def play_note(self):
        while True:
            volume_direction = self.binary_markov_chain(
                constants.probability_of_same_volume_change_direction,
                self.previous_question_attributes.volume_trend)
            volume = self.previous_question_attributes.volume + \
                     constants.volume_change * volume_direction
            if constants.min_volume <= volume <= constants.max_volume:
                self.volume_direction = volume_direction
                self.volume = volume
                break
        # x = constants.probability_of_same_volume_change_direction
        #
        # (-1) ** np.random.binomial(1, self.previous_question_attributes.volume_change)
        constants.mo.send_message([rtmidi.midiconstants.NOTE_ON,
                                   self.note.number, self.volume])

    @staticmethod
    def binary_markov_chain(probability_to_remain, previous_state):
        # My two states are +1 and -1.
        probability_to_go_negative = (1 + previous_state) / 2 - previous_state * probability_to_remain
        new_state = (-1) ** np.random.binomial(1, probability_to_go_negative)
        return new_state

    @staticmethod
    def calculate_autoregressive(x, y):
        p = constants.last_sample_weight
        return (1-p)*x + p*y

    def request_user_response(self):
        question_start_time = time.time()
        identified_note = input("Identify Note:")
        self.response_time.raw = time.time() - question_start_time
        response_time_now_fraction = self.response_time.raw - np.round(self.response_time.raw)
        # Round up sound duration to the nearest second:
        time.sleep(constants.quarter_note_time - response_time_now_fraction)
        # Turn off note:
        constants.mo.send_message([rtmidi.midiconstants.NOTE_OFF, self.note.number, self.volume])
        identified_note = identified_note.upper()
        self.identified_note = identified_note

    def check_user_response(self):
        if self.identified_note == self.note.name:
            self.True_or_False = True
            print(colored("Good :-)", 'blue'))
            self.set_next_step_size_level()
            self.determine_repeat_note_flag()
            self.update_error_state()
        elif self.identified_note == 'END':
            self.response_time.raw= np.nan
            # self.True_or_False = self.identified_note
            self.Termination_Flag = True
        elif self.identified_note == 'RESTART':
            self.response_time.raw = np.nan
            # self.True_or_False = self.identified_note
            print(colored("OK, RESTART: :-)", 'green'))
            self.note.index = helper_functions.intro(constants)
        else: # user error
            self.response_time.raw = np.nan
            self.True_or_False = False
            self.step_size_level -= constants.number_of_step_size_sub_levels
            if self.step_size_level < 0:
                self.step_size_level = 0
            print(colored("Bad :-)", 'red'))
            self.error_state = 'Just Made an Error'
            print('error_state = ' + self.error_state)

    def update_error_state(self):
        if self.error_state == 'Just Made an Error':
            self.error_state = 'Error in Previous Question'
            print('error_state = ' + self.error_state)
        elif self.error_state == 'Error in Previous Question':
            self.error_state = 'No Recent Errors'
            print('error_state = ' + self.error_state)

    def set_next_step_size_level_old(self):
        self.autoregressive_response_time = \
            self.calculate_autoregressive(
                self.previous_autoregressive_response_time,
                self.response_time
            )
        if self.autoregressive_response_time < constants.lower_bound_response_time \
                and self.step_size_level < 8:
            self.step_size_level += 1
        elif self.autoregressive_response_time > constants.upper_bound_response_time \
                and self.step_size_level > 0:
            self.step_size_level -= 1

    def set_next_step_size_level(self):
        a = constants.very_short_response_time
        b = constants.very_long_response_time
        c = constants.number_of_step_size_sub_levels
        d = -constants.number_of_step_size_sub_levels
        x = self.response_time.raw
        y = (x-a)*(d-c)/(b-a) + c
        self.step_size_level += round(y)
        if self.step_size_level >= constants.levels.shape[0]:
            self.step_size_level = constants.levels.shape[0] - 1
        if self.step_size_level < 0:
            self.step_size_level = 0

    def determine_repeat_note_flag(self):
        if self.response_time.raw < constants.quarter_note_time:
            self.slow_answer_in_this_question = False
        elif self.response_time.raw > constants.quarter_note_time:
            self.slow_answer_in_this_question = True


Previous_Question_Attributes = namedtuple('Previous_Question_Attributes', [
            'note_index',
            'step_direction',
            'volume',
            'volume_change',
            'autoregressive_response_time',
            'question_index'])

previous_question_attributes = Previous_Question_Attributes(
    note_index=7,
    step_direction=1,
    volume=constants.initial_volume,
    volume_change=1,
    autoregressive_response_time=constants.optimal_response_time,
    question_index=-2
)
question = Question(previous_question_attributes=previous_question_attributes,
                    penultimate_note_index=7,
                    step_size_level=0,
                    slow_state=False,
                    error_state='No Recent Errors',
                    )
# question.get_new_question_attributes()
question_list = [question, question]
helper_functions.intro(constants)
while not question_list[-1].Termination_Flag:
    previous_question = question_list[-1]
    previous_question_attributes = Previous_Question_Attributes(
        note_index=previous_question.note.index,
        step_direction=previous_question.step_direction,
        volume=previous_question.volume,
        volume_change=previous_question.volume_change,
        autoregressive_response_time=previous_question.response_time.autoregressive,
        question_index=previous_question.question_index
    )
    penultimate_question = question_list[-2]
    question = Question(previous_question_attributes=previous_question_attributes,
                        penultimate_note_index=penultimate_question.note.index,
                        step_size_level=previous_question.step_size_level,
                        slow_state=previous_question.slow_state,
                        error_state=previous_question.error_state,
                        )
    question.get_new_question_attributes()
    question.play_note()
    question.request_user_response()
    question.check_user_response()
    question_list.append(question)


question_list = question_list[2:]
question_list = question_list[:-1]
constants.mo.close_port()

helper_functions.my_plot(constants, question_list)
print('stop')
