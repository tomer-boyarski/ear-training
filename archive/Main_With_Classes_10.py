import rtmidi.midiconstants
import numpy as np
from termcolor import colored
import matplotlib.pyplot as plt
import time
import seaborn as sns
import pickle
import plot_functions
import constants
import initial
from collections import namedtuple
from recordclass import recordclass
from low_level_classes_01 import *

class Question:
    def __init__(self):
        self.step = Step()
        self.note = Note()
        self.response = Response()
        self.error_state = initial.error_state
        self.Termination_Flag = False
        self.volume = Volume()

    def play_note(self, question_list):
        # number_of_questions_since_last_error = self.how_many_questions_since_last_error(question_list)
        self._set_difficulty(question_list)
        if not question_list[-1].response.type:
            if question_list[-2].response.type:
                self.note.index = question_list[-2].question.index
            else:
                self.note.index = helper_functions_02.intro()
        elif not question_list[-2].response.type and \
                 question_list[-1].response.type:
            self.note.index = round((question_list[-2].question.index +
                                     question_list[-1].question.index) / 2)
        elif not question_list[-3].response.type and \
                 question_list[-2].response.type and \
                 question_list[-1].response.type:
            self.note.index = question_list[-3].question.index
        elif not question_list[-4].response.type and \
                 question_list[-3].response.type and \
                 question_list[-2].response.type and \
                 question_list[-1].response.type:
            self.note.index = question_list[-3].question.index
        elif not question_list[-5].response.type and \
                 question_list[-4].response.type and \
                 question_list[-3].response.type and \
                 question_list[-2].response.type and \
                 question_list[-1].response.type:
            self.note.index = question_list[-5].question.index
        else:
            self._set_step_size_outside_error_mode()
            self._set_step_trend_and_new_note_index_outside_error_mode(question_list)
        # This does nothing if I'm outside of error mode:
        self.step.size = self.note.index - \
                         question_list[-1].question.index
        # This does nothing if I'm outside of error mode:
        self.step.trend = np.sign(self.step.size)
        self.note.number = constants.note_numbers_C_to_C[self.note.index]
        self.note.name = constants.note_names_chromatic_C_scale[self.note.number % 12]
        self.set_volume(question_list)
        constants.mo.send_message([rtmidi.midiconstants.NOTE_ON,
                                   self.note.number, self.volume.value])

    @staticmethod
    def how_many_questions_since_last_error(question_list):
        true_or_false = [q.response.type for q in question_list]
        reversed_true_or_false = true_or_false[::-1]
        if False in reversed_true_or_false:
            return reversed_true_or_false.index(False)
        else:
            return np.infty
        print('Number of questions since last error = ' +
              str(number_of_questions_since_last_error))

    def _set_difficulty(self, question_list):
        # print('previous level = ' + str())
        if question_list[-1].response.type:
            self._set_difficulty_after_correct_answer(question_list)
        else:
            self.step.level = question_list[-1].step.total_level - \
                              constants.number_of_step_size_sub_levels
            if self.step.level < 0:
                self.step.level = 0
        print('level = ' + str(self.step.level))

    def _set_difficulty_after_correct_answer(self, question_list):
        a = constants.very_short_response_time
        b = constants.very_long_response_time
        c = constants.number_of_step_size_sub_levels
        d = -constants.number_of_step_size_sub_levels
        x = question_list[-1].response.time.raw
        y = (x - a) * (d - c) / (b - a) + c
        self.step.level = question_list[-1].step.total_level + round(y)
        if self.step.level >= constants.levels.shape[0]:
            self.step.level = constants.levels.shape[0] - 1
        if self.step.level < 0:
            self.step.level = 0

    def _set_step_size_outside_error_mode(self):
        self.step.size = np.random.choice(
            np.arange(8), 1, p=constants.levels[self.step.level, :])[0]
        if 0 > self.step.size or self.step.size > 7:
            print('step size too big or too small')

    def _set_step_trend_and_new_note_index_outside_error_mode(self, question_list):
        while True:
            self.step.trend = self._binary_markov_chain(
                constants.probability_of_same_step_direction,
                question_list[-1].step.trend)
            self.note.index = question_list[-1].question.index + \
                              self.step.size * self.step.trend
            if 0 <= self.note.index <= 14:
                break

    def set_volume(self, question_list):
        while True:
            volume_trend = self._binary_markov_chain(
                constants.probability_of_same_volume_change_direction,
                question_list[-1].volume.trend)
            volume = question_list[-1].volume.value + \
                     constants.volume_change * volume_trend
            if constants.min_volume <= volume <= constants.max_volume:
                self.volume.trend = volume_trend
                self.volume.value = round(volume)
                break

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
            # this is not necessary since true_or_false is initialized to 'True'
            # self.response.true_or_false = True
            print(colored("Good :-)", 'blue'))
        elif self.response.text == 'END':
            self.Termination_Flag = True
        elif self.response.text == 'RESTART':
            print(colored("OK, RESTART: :-)", 'green'))
            self.note.index = helper_functions.intro()
        else:  # user error
            self.response.true_or_false = False
            print(colored("Bad :-)", 'red'))
            # print('error_state = Just Made an Error')


initial_question = Question()
list_of_questions = [initial_question] * 5
helper_functions_02.intro()
while not list_of_questions[-1].Termination_Flag:
    question = Question()
    question.play_note(list_of_questions)
    question.request_user_response()
    list_of_questions.append(question)
constants.mo.close_port()

list_of_questions = list_of_questions[:-1]
list_of_questions = list_of_questions[1:]
helper_functions_02.plot_jump_success_rate(list_of_questions)
list_of_questions = list_of_questions[1:]
# helper_functions_02.my_plot(constants, list_of_questions)

# print('stop')
