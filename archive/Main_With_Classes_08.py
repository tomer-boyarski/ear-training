import rtmidi.midiconstants
import numpy as np
from termcolor import colored
import matplotlib.pyplot as plt
import time
import seaborn as sns
import pickle
import helper_functions_01
import constants
import initial
from collections import namedtuple
from recordclass import recordclass

time_beginning_of_program = time.time()

my_velocity = 127

cubic_polynomial_mapping_coefficients = helper_functions.cubic_polynomial_mapping()


class Question:
    def __init__(self):
        self.step = initial.step
        self.note = initial.note
        self.response = initial.response
        self.index = initial.index
        self.error_state = initial.error_state
        self.Termination_Flag = False
        self.volume = initial.volume
        self.list_of_questions = None

    def set_history(self, question_list):
        self.list_of_questions = question_list

    def check_user_response_in_previous_question(self):
        last_response = self.list_of_questions[-1].response.text
        last_note_name = self.list_of_questions[-1].question.name
        if last_response == last_note_name:
            print(colored("Good :-)", 'blue'))
            self._set_step_size_level()
            self._update_error_state()
        elif last_response != last_note_name and \
                last_response != 'END' and \
                last_response != 'RESTART':
            self.step.total_level -= constants.number_of_step_size_sub_levels
            if self.step.total_level < 0:
                self.step.total_level = 0
            self.error_state = 'Just Made an Error'

    def _set_step_size_level(self):
        a = constants.very_short_response_time
        b = constants.very_long_response_time
        c = constants.number_of_step_size_sub_levels
        d = -constants.number_of_step_size_sub_levels
        x = self.list_of_questions[-1].response.time.raw
        y = (x - a) * (d - c) / (b - a) + c
        self.step.total_level = self.step.total_level + round(y)
        if self.step.total_level >= constants.levels.shape[0]:
            self.step.total_level = constants.levels.shape[0] - 1
        if self.step.total_level < 0:
            self.step.total_level = 0

    def _update_error_state(self):
        if self.error_state == 'Just Made an Error':
            self.error_state = 'Error in Previous Question'
            print('error_state = ' + self.error_state)
        elif self.error_state == 'Error in Previous Question':
            self.error_state = 'No Recent Errors'
            print('error_state = ' + self.error_state)

    def get_new_question_attributes(self):
        print('level = ' + str(self.step.total_level))
        if self.error_state == 'Just Made an Error' or \
                self.error_state == 'Error in Previous Question':
            self.note.index = self.list_of_questions[-2].question.index
            self.step.size = self.note.index - \
                             self.list_of_questions[-1].question.index
            self.step.trend = np.sign(self.step.size)
        elif self.error_state == 'No Recent Errors':
            self._set_step_size()
            self._set_step_direction_and_new_note()
        self.note.number = constants.note_numbers_C_to_C[self.note.index]
        self.note.name = constants.note_names_chromatic_C_scale[self.note.number % 12]
        print('stop')
    def _set_step_size(self):
        self.step.size = np.random.choice(
            np.arange(8), 1, p=constants.levels[self.step.total_level, :])[0]
        if 0 > self.step.size or self.step.size > 7:
            print('step size too big or too small')

    def _set_step_direction_and_new_note(self):
        while True:
            self.step.trend = self._binary_markov_chain(
                constants.probability_of_same_step_direction,
                self.list_of_questions[-1].step.trend)
            self.note.index = self.list_of_questions[-1].question.index + \
                              self.step.size * self.step.trend
            if 0 <= self.note.index <= 14:
                break

    def play_note(self):
        while True:
            volume_trend = self._binary_markov_chain(
                constants.probability_of_same_volume_change_direction,
                self.list_of_questions[-1].volume.trend)
            volume = self.list_of_questions[-1].volume.value + \
                constants.volume_change * volume_trend
            if constants.min_volume <= volume <= constants.max_volume:
                self.volume.trend = volume_trend
                self.volume.value = round(volume)
                break
        constants.mo.send_message([rtmidi.midiconstants.NOTE_ON,
                                   self.note.number, self.volume.value])

    @staticmethod
    def _binary_markov_chain(probability_to_remain, previous_state):
        # My two states are +1 and -1.
        probability_to_go_negative = (1 + previous_state) / 2 - previous_state * probability_to_remain
        new_state = (-1) ** np.random.binomial(1, probability_to_go_negative)
        return new_state

    @staticmethod
    def _calculate_autoregressive(x, y):
        p = constants.last_sample_weight
        return (1 - p) * x + p * y

    def request_user_response(self):
        question_start_time = time.time()
        self.response.text = input("Identify Note:")
        self.response.time.raw = time.time() - question_start_time
        response_time_now_fraction = self.response.time.raw - np.round(self.response.time.raw)
        time.sleep(constants.quarter_note_time - response_time_now_fraction)
        constants.mo.send_message([rtmidi.midiconstants.NOTE_OFF, self.note.number, self.volume.value])
        self.response.text = self.response.text.upper()
        self._set_response_time_to_nan_if_incorrect()
        self._check_user_response_at_question_end()

    def _set_response_time_to_nan_if_incorrect(self):
        if self.response.text != self.note.name:
            self.response.time.raw = np.nan

    def _check_user_response_at_question_end(self):
        if self.response.text == self.note.name:
            self.True_or_False = True
            print(colored("Good :-)", 'blue'))
        elif self.response.text == 'END':
            self.Termination_Flag = True
        elif self.response.text == 'RESTART':
            print(colored("OK, RESTART: :-)", 'green'))
            self.note.index = helper_functions.intro()
        else:  # user error
            self.True_or_False = False
            print(colored("Bad :-)", 'red'))
            print('error_state = Just Made an Error')


question = Question()
list_of_questions = [question, question]
helper_functions.intro()
while not list_of_questions[-1].Termination_Flag:
    question = Question()
    question.set_history(list_of_questions)
    question.check_user_response_in_previous_question()
    question.get_new_question_attributes()
    question.play_note()
    question.request_user_response()
    list_of_questions.append(question)

list_of_questions = list_of_questions[2:]
list_of_questions = list_of_questions[:-1]
constants.mo.close_port()

helper_functions.my_plot(constants, list_of_questions)
print('stop')
